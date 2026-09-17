import os
import sys
import json
import shutil
import uuid
from typing import Optional, List
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, Form, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..db import get_db, StudyDocument, Flashcard

# Add src to sys.path to leverage original working domain logic
src_dir = Path(__file__).resolve().parent.parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from ai_assistant import AIAssistant
from study_materials import StudyMaterialsManager

router = APIRouter(prefix="/api/materials", tags=["materials"])

# Instantiate singletons from original modules
ai_assistant = AIAssistant()
materials_mgr = StudyMaterialsManager()


@router.get("/techniques")
def get_study_techniques():
    """Retrieve full learning techniques (Feynman, Pomodoro, Active Recall, Spaced Repetition) from src/study_materials.py."""
    data = materials_mgr.get_default_materials()
    return {
        "techniques": data.get("study_techniques", []),
        "productivity_tips": data.get("productivity_tips", []),
        "quotes": data.get("motivational_quotes", []),
    }


@router.get("/links")
def get_quick_links():
    """Retrieve quick links from src/study_materials.py."""
    return materials_mgr.materials.get("quick_links", [])


@router.get("/documents")
def list_documents(user_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """List documents from both DB and src/materials uploaded directory for the specified user."""
    if not user_id:
        return []

    docs = db.query(StudyDocument).filter(StudyDocument.user_id == user_id).all()
    results = [
        {
            "id": d.id,
            "name": d.filename,
            "size": d.file_size,
            "summary": d.summary,
            "date": d.created_at.strftime("%b %d, %H:%M") if d.created_at else "",
        }
        for d in docs
    ]

    # Also include any files in data/materials/uploaded_files matching user_id
    uploaded_dir = ai_assistant.uploaded_files_dir
    if uploaded_dir.exists():
        for meta_file in uploaded_dir.glob("*.meta.json"):
            try:
                import json
                meta = json.loads(meta_file.read_text(encoding="utf-8"))
                if meta.get("user_id") == user_id:
                    if not any(r["name"] == meta.get("original_name") for r in results):
                        results.append({
                            "id": meta_file.stem.replace(".meta", ""),
                            "name": meta.get("original_name", meta.get("title")),
                            "size": f"{meta.get('word_count', 0)} words",
                            "summary": meta.get("content", "")[:120] + "...",
                            "date": meta.get("upload_date", "")[:10],
                        })
            except Exception:
                pass

    return results


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """Upload and parse study material using original src/ai_assistant.py logic (PDF/DOCX/PPTX/TXT)."""
    temp_dir = Path("data/temp_uploads")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = temp_dir / file.filename

    # Save incoming upload temporarily
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Use original src/ai_assistant logic to extract and index
    result = ai_assistant.upload_study_material(
        file_path=str(temp_path),
        title=file.filename,
        description=f"Uploaded {file.filename} for study session context"
    )

    # Clean up temp
    try:
        temp_path.unlink()
    except Exception:
        pass

    if result.get("success"):
        meta = result.get("metadata", {})
        meta_id = result.get("material_id")
        if meta_id:
            meta_path = ai_assistant.uploaded_files_dir / f"{meta_id}.meta.json"
            if meta_path.exists():
                try:
                    import json
                    meta_data = json.loads(meta_path.read_text(encoding="utf-8"))
                    meta_data["user_id"] = user_id
                    meta_path.write_text(json.dumps(meta_data), encoding="utf-8")
                except Exception:
                    pass

        doc_id = f"doc_{uuid.uuid4().hex[:8]}"
        doc = StudyDocument(
            id=doc_id,
            user_id=user_id,
            filename=file.filename,
            file_size=f"{round(meta.get('word_count', 0) / 100, 1)} KB",
            summary=meta.get("content", "")[:150] + "...",
        )
        db.add(doc)
        db.commit()
        return {
            "success": True,
            "document": {
                "id": doc.id,
                "name": doc.filename,
                "size": doc.file_size,
                "summary": doc.summary,
            }
        }
    else:
        return {"success": False, "error": result.get("error", "Extraction failed")}


@router.delete("/documents/{doc_id}")
def delete_document(doc_id: str, db: Session = Depends(get_db)):
    """Delete a study document from database and uploaded directory."""
    doc = db.query(StudyDocument).filter(StudyDocument.id == doc_id).first()
    filename = doc.filename if doc else None
    if doc:
        db.delete(doc)
        db.commit()

    # Also clean up from uploaded_files_dir if present
    uploaded_dir = ai_assistant.uploaded_files_dir
    patterns = [f"*{doc_id}*"]
    if filename:
        patterns.append(f"*{filename}*")

    for pattern in patterns:
        for f in uploaded_dir.glob(pattern):
            try:
                f.unlink()
            except Exception:
                pass

    return {"status": "success", "message": "Document deleted"}


@router.get("/daily-motivation")
def get_daily_motivation():
    """Retrieve random motivational quote and productivity protocol tip from src/study_materials.py"""
    return {
        "quote": materials_mgr.get_daily_motivation(),
        "productivity_tip": materials_mgr.get_productivity_tip(),
    }


class QuickLinkPayload(BaseModel):
    name: str
    url: str
    category: str = "Custom"
    description: str = ""


@router.post("/links")
def add_custom_link(payload: QuickLinkPayload):
    """Add a new quick link using src/study_materials.py"""
    success = materials_mgr.add_quick_link(
        name=payload.name.strip(),
        url=payload.url.strip(),
        category=payload.category.strip(),
        description=payload.description.strip(),
    )
    return {"success": success, "links": materials_mgr.materials.get("quick_links", [])}


class CreateFlashcardRequest(BaseModel):
    question: str
    answer: str
    category: Optional[str] = "General"
    user_id: str


class GenerateFlashcardRequest(BaseModel):
    topic: Optional[str] = None
    user_id: str


@router.delete("/links/{link_name}")
def delete_quick_link(link_name: str):
    """Delete a quick link by name"""
    success = materials_mgr.remove_quick_link(link_name)
    return {"success": success, "links": materials_mgr.materials.get("quick_links", [])}


@router.get("/flashcards")
def list_flashcards(user_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    if not user_id:
        return []
    cards = db.query(Flashcard).filter(Flashcard.user_id == user_id).all()
    return [
        {
            "id": c.id,
            "question": c.question,
            "answer": c.answer,
            "category": c.category,
            "mastered": c.mastered,
        }
        for c in cards
    ]


@router.post("/flashcards")
def create_flashcard(req: CreateFlashcardRequest, db: Session = Depends(get_db)):
    """Create a new custom flashcard"""
    if not req.user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    card = Flashcard(
        user_id=req.user_id,
        question=req.question.strip(),
        answer=req.answer.strip(),
        category=req.category.strip() if req.category else "General",
        mastered=False,
        review_count=0,
    )
    db.add(card)
    db.commit()
    db.refresh(card)
    return {
        "id": card.id,
        "question": card.question,
        "answer": card.answer,
        "category": card.category,
        "mastered": card.mastered,
    }


@router.delete("/flashcards/{card_id}")
def delete_flashcard(card_id: int, db: Session = Depends(get_db)):
    """Delete a flashcard by ID"""
    card = db.query(Flashcard).filter(Flashcard.id == card_id).first()
    if not card:
        return {"success": False, "error": "Flashcard not found"}
    db.delete(card)
    db.commit()
    return {"success": True, "message": f"Flashcard {card_id} deleted"}


@router.patch("/flashcards/{card_id}/mastered")
def toggle_card_mastered(card_id: int, db: Session = Depends(get_db)):
    """Toggle mastered status of a flashcard"""
    card = db.query(Flashcard).filter(Flashcard.id == card_id).first()
    if not card:
        return {"success": False, "error": "Flashcard not found"}
    card.mastered = not card.mastered
    card.review_count = (card.review_count or 0) + 1
    db.commit()
    return {"success": True, "id": card.id, "mastered": card.mastered}


@router.post("/flashcards/generate")
def generate_ai_flashcards(req: GenerateFlashcardRequest, db: Session = Depends(get_db)):
    """Auto-generate high-yield flashcards from uploaded study notes or AI models"""
    if not req or not req.user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    user_id = req.user_id
    materials_context = ai_assistant.load_all_materials()
    generated_cards = []

    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            prompt = (
                "Generate 3 to 4 high-yield study flashcards for active recall revision. "
                + (f"Extract directly from these uploaded lecture materials:\n{materials_context[:4000]}\n" if materials_context else "Base them on essential STEM, computer science, and engineering fundamentals.\n")
                + "Return ONLY a valid JSON array of objects with keys: 'question', 'answer', 'category'. Do NOT include markdown blocks or any other text."
            )
            for model_name in ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite"]:
                try:
                    res = client.models.generate_content(model=model_name, contents=prompt)
                    if res and res.text:
                        raw = res.text.strip()
                        if raw.startswith("```"):
                            raw = raw.strip("`").replace("json\n", "", 1).replace("json", "", 1).strip()
                        parsed = json.loads(raw)
                        if isinstance(parsed, list):
                            generated_cards = parsed
                            break
                except Exception:
                    continue
        except Exception as e:
            print(f"Error generating cards with Gemini: {e}")

    # Fallback curated cards if offline or no Gemini key
    if not generated_cards:
        import random
        pool = [
            {
                "question": "What is the time complexity of QuickSelect for finding the k-th element on average?",
                "answer": "O(n) average time complexity because only one half of the partition is recursed into, compared to O(n log n) for full QuickSort.",
                "category": "Algorithms",
            },
            {
                "question": "What is Amdahl's Law and what limit does it place on parallel computing?",
                "answer": "Amdahl's Law states that theoretical speedup is limited by the sequential fraction of the task: S_latency(s) = 1 / ((1 - p) + (p / s)).",
                "category": "Computer Architecture",
            },
            {
                "question": "How does Backpropagation calculate weight gradients in deep neural networks?",
                "answer": "It applies the multivariate chain rule backwards from the loss function through each hidden layer: dL/dW = delta * a^T.",
                "category": "Machine Learning",
            },
            {
                "question": "What is the primary difference between Mutex and Semaphore primitives?",
                "answer": "A Mutex is a locking mechanism allowing only one thread to access a resource (has ownership). A Semaphore is a signaling mechanism with an integer counter allowing up to N concurrent threads.",
                "category": "Operating Systems",
            },
            {
                "question": "What is the CAP Theorem trade-off in distributed systems?",
                "answer": "A distributed data store can guarantee at most two of three properties: Consistency, Availability, and Partition Tolerance. In network partitions, you must choose C or A.",
                "category": "Distributed Systems",
            },
        ]
        generated_cards = random.sample(pool, min(3, len(pool)))

    saved_cards = []
    for c in generated_cards:
        card = Flashcard(
            user_id=user_id,
            question=c.get("question", "Question"),
            answer=c.get("answer", "Answer"),
            category=c.get("category", "General"),
            mastered=False,
            review_count=0,
        )
        db.add(card)
        db.commit()
        db.refresh(card)
        saved_cards.append({
            "id": card.id,
            "question": card.question,
            "answer": card.answer,
            "category": card.category,
            "mastered": card.mastered,
        })

    return saved_cards

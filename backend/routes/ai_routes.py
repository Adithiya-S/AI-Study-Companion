import os
import sys
import json
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from ..config import GEMINI_API_KEY, BASE_DIR

# Import original src/ai_assistant for RAG document context
src_dir = Path(__file__).resolve().parent.parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from ai_assistant import AIAssistant

ai_assistant = AIAssistant()
router = APIRouter(prefix="/api/ai", tags=["ai"])

ACTIVE_KEY = GEMINI_API_KEY or ai_assistant.api_key

SESSIONS_FILE = BASE_DIR / "data" / "materials" / "chat_sessions.json"


def _load_sessions() -> list:
    if not SESSIONS_FILE.exists():
        return []
    try:
        with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading sessions: {e}")
        return []


def _save_sessions(sessions: list):
    try:
        SESSIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(sessions, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving sessions: {e}")


def _append_to_session(session_id: Optional[str], user_text: str, reply_text: str, mode: str) -> str:
    sessions = _load_sessions()
    now_iso = datetime.now().isoformat()
    now_display = datetime.now().strftime("%I:%M %p")

    target_session = None
    if session_id:
        for s in sessions:
            if s.get("id") == session_id:
                target_session = s
                break

    if not target_session:
        new_id = session_id or f"sess_{int(datetime.now().timestamp() * 1000)}"
        clean_title = user_text[:36] + ("..." if len(user_text) > 36 else "")
        target_session = {
            "id": new_id,
            "title": clean_title or "Study Session",
            "created_at": now_iso,
            "updated_at": now_iso,
            "mode": mode,
            "preview": clean_title,
            "message_count": 0,
            "messages": [],
        }
        sessions.insert(0, target_session)

    target_session["messages"].append({
        "role": "user",
        "text": user_text,
        "timestamp": now_display,
        "iso": now_iso,
    })
    target_session["messages"].append({
        "role": "assistant",
        "text": reply_text,
        "timestamp": now_display,
        "iso": now_iso,
    })
    target_session["message_count"] = len(target_session["messages"])
    target_session["updated_at"] = now_iso
    target_session["preview"] = user_text[:60] + ("..." if len(user_text) > 60 else "")

    # Retain up to 50 sessions
    sessions = sessions[:50]
    _save_sessions(sessions)
    return target_session["id"]


class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = ""
    api_key: Optional[str] = None
    mode: Optional[str] = "internet"  # "internet" | "materials"
    session_id: Optional[str] = None


class KeyConfigRequest(BaseModel):
    api_key: str


@router.post("/set-key")
def set_api_key(req: KeyConfigRequest):
    global ACTIVE_KEY
    key = req.api_key.strip()
    ACTIVE_KEY = key
    os.environ["GEMINI_API_KEY"] = key
    ai_assistant.api_key = key

    # Write to .env file
    env_file = BASE_DIR / ".env"
    try:
        env_file.write_text(f"GEMINI_API_KEY={key}\n", encoding="utf-8")
    except Exception as e:
        print(f"Error saving to .env: {e}")

    return {"status": "success", "message": "Gemini API key configured successfully"}


@router.get("/sessions")
def get_chat_sessions():
    """Retrieve chat session history"""
    sessions = _load_sessions()
    # Sort by updated_at descending
    sessions.sort(key=lambda s: s.get("updated_at", ""), reverse=True)
    return sessions


@router.post("/new-chat")
def start_new_chat():
    """Start a fresh chat conversation with a new session ID"""
    new_id = f"sess_{int(datetime.now().timestamp() * 1000)}"
    return {
        "status": "success",
        "session_id": new_id,
        "message": "New chat session initialized",
    }


@router.delete("/sessions/{session_id}")
def delete_chat_session(session_id: str):
    """Delete a chat session from history"""
    sessions = _load_sessions()
    sessions = [s for s in sessions if s.get("id") != session_id]
    _save_sessions(sessions)
    return {"status": "success", "message": "Session deleted"}


@router.post("/chat")
def ai_chat(req: ChatRequest):
    global ACTIVE_KEY
    query = req.message.strip()
    lower = query.lower()
    mode = req.mode or "internet"
    key_to_use = req.api_key.strip() if req.api_key else ACTIVE_KEY

    # Load uploaded study materials context
    materials_context = ai_assistant.load_all_materials()

    # If in Materials mode and no materials uploaded
    is_meta_query = any(
        w in query.lower() for w in [
            "what is this", "point of this", "tell me about", "about this", "features",
            "what can you do", "hi", "hello", "hey", "who are you", "what is aura"
        ]
    )
    if mode == "materials" and not materials_context and not is_meta_query:
        return {
            "reply": "📚 **My Materials Mode**: No study documents found in your library.\n\nPlease upload your lecture notes or textbooks in **03 // STUDY MATERIALS & CARDS**, or switch to **🌐 Internet Mode** above!",
            "source": "materials_empty",
        }

    # 1. If Gemini key is available, make live API call with latest Flash models in free tier
    if key_to_use:
        try:
            from google import genai
            client = genai.Client(api_key=key_to_use)

            now_str = datetime.now().strftime("%A, %B %d, %Y (%I:%M %p)")

            platform_context = (
                "ABOUT THIS WEBSITE (THE AURA PLATFORM):\n"
                "This website is called 'AURA' (AI Deep Focus & Telemetry Workstation). It is a comprehensive, full-stack productivity workstation engineered to eliminate digital distractions and keep students in deep cognitive flow.\n"
                "IMPORTANT DISTINCTION: You are the built-in AI Study Copilot on Tab 04, which is just ONE of the core pillars of this website.\n"
                "The 5 core pillars of the AURA website are:\n"
                "1. 👁️ Live Eye & Gaze Tracking HUD (Tab 01): Hardware-accelerated in-browser MediaPipe computer vision tracks Eye Aspect Ratio (EAR) and head gaze, immediately alerting the student if they become drowsy or lose focus.\n"
                "2. 📱 YOLOv8 Phone Distraction Guard (Tab 01): Native YOLOv8 neural network runs in the background to detect physical cell phones in the camera frame, proactively stopping doomscrolling without penalizing natural reading or note-taking.\n"
                "3. ⏱️ Focus Sprint Workstation (Tab 01): Structured deep-work Pomodoro intervals (25/5, 50/10) with live focus efficiency scoring and sprint telemetry summaries.\n"
                "4. 📚 Study Materials & Dual-Mode RAG (Tab 02): Ingests PDFs, Word docs (DOCX), PowerPoint (PPTX), Excel sheets, and code files to generate spaced-repetition flashcards and build a searchable knowledge base.\n"
                "5. 📊 Telemetry Analytics & Cognitive Protocols (Tab 03): Multi-day productivity reports (1D, 7D, 14D, 30D), focus score distributions, sprint completion logs, and evidence-based protocols (Feynman Technique, Pomodoro Interval Mastery, Spaced Repetition).\n"
                "6. 🤖 AI Deep Focus Copilot (Tab 04): Dual-mode AI tutor (Internet Mode for broad STEM/coding explanations vs. My Materials Mode for strict grounding in uploaded notes).\n"
            )

            if mode == "materials":
                prompt = (
                    f"System Context: Current local date and time is {now_str}.\n"
                    f"{platform_context}\n"
                    "You are the AI Study Copilot on the AURA platform.\n\n"
                    "CRITICAL INSTRUCTION FOR QUESTIONS ABOUT THE WEBSITE, PLATFORM, OR PURPOSE:\n"
                    "- If the student asks about the website, platform, its purpose, or what it can do (e.g., 'what is the point of this website', 'tell me about this site', 'tell me about it', 'what is aura', 'features'): DO NOT just describe yourself as a chatbot! Enthusiastically promote and explain the ENTIRE AURA website workstation and all its features (Eye Tracking HUD, YOLOv8 Phone Guard, Sprint Timer, Materials & Flashcards, Analytics). Give them a clear, inspiring tour of the site!\n"
                    "- If the student sends a simple conversational greeting, respond warmly and concisely in 1-2 friendly sentences.\n"
                    "- For academic and subject questions, answer accurately based strictly on the student's study materials below. If not present in notes, explain so and suggest switching to Internet Mode.\n\n"
                    f"STUDENT STUDY MATERIALS:\n{materials_context[:8000]}\n\n"
                    f"Student: {query}\n\n"
                    "AURA:"
                )
            else:
                notes_block = (
                    f"Student's Uploaded Notes (for reference if relevant):\n{materials_context[:3000]}\n\n"
                    if materials_context else ""
                )
                prompt = (
                    f"System Context: Current local date and time is {now_str}.\n"
                    f"{platform_context}\n"
                    "You are the AI Study Copilot on the AURA platform.\n\n"
                    "CRITICAL INSTRUCTION FOR QUESTIONS ABOUT THE WEBSITE, PLATFORM, OR PURPOSE:\n"
                    "- If the student asks about the website, platform, its purpose, or what it can do (e.g., 'what is the point of this website', 'tell me about this site', 'tell me about it', 'what is aura', 'features', 'why use this'): DO NOT just talk about yourself as an AI chatbot! You MUST passionately pitch and explain the ENTIRE AURA platform! Highlight that the site is an all-in-one deep work workstation combining real-time vision tracking (MediaPipe eye drowsiness + YOLOv8 phone guard), structured Pomodoro sprint timers, multi-format lecture ingestion & flashcards, multi-day telemetry analytics, and this AI tutor. Walk them through how to use the site.\n"
                    "- Conversational queries, greetings, and check-ins (e.g., 'hi', 'hello', 'how are you', 'thank you'): Respond naturally, warmly, and concisely in 1-2 sentences. Never generate unsolicited mathematical formulas, code blocks, or academic essays for simple greetings!\n"
                    "- Time & Date: Answer directly using the current date/time provided above (e.g., 'Today is Thursday, September 17, 2026.').\n"
                    "- Academic / STEM / Study questions: Provide clear, well-structured explanations tailored to a student. Use formatting (bullet points, LaTeX math formulas, code snippets) ONLY when directly helpful and relevant to the subject matter.\n"
                    "- Tone: Supportive, engaging, motivating, and clear.\n\n"
                    f"{notes_block}"
                    f"Student: {query}\n\n"
                    "AURA:"
                )

            # Robust candidate models (ordered by capability and free-tier stability)
            candidate_models = ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite"]
            last_err = None
            response_text = None
            active_model_name = "gemini-3.6-flash"

            for model_name in candidate_models:
                try:
                    res = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                    )
                    if res and res.text:
                        response_text = res.text
                        active_model_name = model_name
                        break
                except Exception as m_err:
                    last_err = m_err
                    continue

            if response_text:
                session_id = _append_to_session(req.session_id, query, response_text, mode)
                return {
                    "reply": response_text,
                    "source": f"gemini_{active_model_name}",
                    "session_id": session_id,
                }
            elif last_err:
                raise last_err

        except Exception as e:
            print(f"Gemini API error: {e}")
            return {
                "reply": f"⚠️ **Gemini API Error**: `{str(e)}`\n\nPlease verify your API key at [Google AI Studio](https://aistudio.google.com/app/apikey).",
                "source": "error",
            }

    # 2. Dynamic Study Copilot when no key has been entered yet
    is_about_site = any(w in lower for w in [
        "what is this site", "point of this website", "point of this site", "point of the site",
        "point of the website", "tell me about this site", "tell me about the site", "tell me about it",
        "tell me about this", "about this site", "about this website", "what is aura", "what is this platform",
        "what can you do", "features", "what does this website do", "what does this site do",
        "what does this app do", "purpose of this website", "purpose of this site", "how does this site work",
        "how does this website work", "why this website", "why use this", "what is this tool", "what is this project",
        "what is the point"
    ]) or ("point" in lower and "website" in lower) or ("about" in lower and ("website" in lower or "site" in lower or "platform" in lower))

    if is_about_site:
        reply = (
            "### 🚀 Welcome to AURA // AI Deep Focus & Telemetry Companion\n\n"
            "**AURA** is not just an AI chatbot—it is an **all-in-one engineering workstation and study operating system** designed to eliminate distractions and keep you in an uninterrupted state of deep work. Here is what this entire platform provides:\n\n"
            "1. **👁️ Real-Time Eye & Gaze Tracking HUD (Tab 01)**\n"
            "   - Powered by in-browser MediaPipe FaceMesh computer vision. It monitors your Eye Aspect Ratio (EAR) and head orientation, gently alerting you if your gaze drifts away or if you begin to nod off.\n\n"
            "2. **📱 Native YOLOv8 Phone Distraction Guard (Tab 01)**\n"
            "   - Runs an ultra-fast YOLOv8 neural network in the background to detect physical smartphones in your hands or desk. It stops mindless doomscrolling while ensuring you are never penalized for looking down at books or writing paper notes.\n\n"
            "3. **⏱️ Focus Sprint Workstation (Tab 01)**\n"
            "   - Structured Pomodoro intervals (25/5 or 50/10) with live focus efficiency scoring, distraction counters, and post-sprint telemetry summaries.\n\n"
            "4. **📚 Study Materials & Flashcard Hub (Tab 02)**\n"
            "   - Drag-and-drop lecture notes, textbooks, and problem sets (PDF, Word DOCX, PowerPoint PPTX, Excel XLSX, and code files). Test your active recall with spaced repetition flashcards powered by the SM-2 algorithm.\n\n"
            "5. **📊 Telemetry Analytics & Study Protocols (Tab 03)**\n"
            "   - Review multi-day productivity curves (1, 7, 14, or 30 days), track long-term focus metrics, and practice cognitive protocols like the Feynman Technique and Leitner Box system.\n\n"
            "6. **🤖 AI Deep Focus Copilot (Tab 04)**\n"
            "   - That's this tab! Switch between **🌐 Internet Mode** (for broad STEM explanations, mathematical proofs, and code architecture) and **📚 My Materials Mode** (which strictly restricts AI reasoning to your uploaded lecture slides to prevent hallucinations).\n\n"
            "> 💡 **How to get started:** Turn on your camera in **01 // FOCUS HUD**, set a 25-minute sprint, upload your lecture slides in **02 // STUDY MATERIALS**, and get into the zone!"
        )
    elif any(w in lower for w in ["hi", "hello", "hey"]):
        reply = (
            "👋 **Hello operator! Welcome to AURA.**\n\n"
            "I'm your study copilot inside this workstation. You can ask me questions about **coding, mathematics, algorithms, study strategies, or lecture materials**.\n\n"
            "💡 **New to AURA?** Ask me *'What is the point of this website?'* to tour all of AURA's vision, sprint, and analytics features, or enter your Gemini API key above for full live reasoning!"
        )
    elif "quiz" in lower:
        reply = (
            "### 🎯 Active Recall Challenge (Test Yourself):\n\n"
            "1. **Question 1**: What mathematical relationship does the Eye Aspect Ratio (EAR) leverage to distinguish blinks from eye closures?\n"
            "2. **Question 2**: Explain why Stochastic Gradient Descent (SGD) introduces beneficial noise compared to standard Batch Gradient Descent.\n"
            "3. **Question 3**: In the Pomodoro technique, why is 50/10 often preferred over 25/5 for complex programming tasks?\n\n"
            "*Draft your response in your notes or reply with your answer to Question 1!*"
        )
    elif any(w in lower for w in ["backprop", "gradient", "neural", "deep learning"]):
        reply = (
            "### ⚡ Backpropagation Mechanics:\n\n"
            "Backpropagation computes the gradient of the loss function $L$ with respect to each network weight $W$ using the **multivariate chain rule**:\n\n"
            "$$\\frac{\\partial L}{\\partial W^{(l)}} = \\delta^{(l)} \\cdot (a^{(l-1)})^T$$\n\n"
            "1. **Forward Pass**: Activations $a^{(l)} = \\sigma(z^{(l)})$ propagate forward through each layer.\n"
            "2. **Backward Pass**: Error sensitivities $\\delta^{(l)} = \\frac{\\partial L}{\\partial z^{(l)}}$ propagate backward.\n"
            "3. **Weight Update**: Weights step against the gradient: $W \\leftarrow W - \\eta \\cdot \\nabla_W L$.\n\n"
            "What specific layer type (Dense, Conv2D, Transformer Attention) would you like to derive?"
        )
    elif any(w in lower for w in ["python", "code", "function", "javascript", "react", "algorithm", "quicksort"]):
        reply = (
            "### 💻 Code Architecture & Algorithm Breakdown:\n\n"
            f"Here is how you would structure a robust implementation related to `{query}`:\n\n"
            "```python\n"
            "# Production pattern with type annotations\n"
            "from typing import List\n\n"
            "def quicksort(arr: List[int]) -> List[int]:\n"
            "    if len(arr) <= 1:\n"
            "        return arr\n"
            "    pivot = arr[len(arr) // 2]\n"
            "    left = [x for x in arr if x < pivot]\n"
            "    middle = [x for x in arr if x == pivot]\n"
            "    right = [x for x in arr if x > pivot]\n"
            "    return quicksort(left) + middle + quicksort(right)\n"
            "```\n\n"
            "Would you like an in-place version or time/space complexity analysis?"
        )
    elif any(w in lower for w in ["focus", "tired", "sleepy", "distract", "procrastinat"]):
        reply = (
            "### 🧠 Focus & Cognition Protocol:\n\n"
            "- **The 20-20-20 Rule**: Every 20 minutes, look at an object 20 feet away for at least 20 seconds to relax ciliary eye muscles.\n"
            "- **Dopamine Reset**: Remove your phone from arm's reach. Phone presence alone reduces working memory capacity.\n"
            "- **Micro-Break**: If your EAR score is dropping below 0.22, stand up, drink 200ml of water, and do 10 deep diaphragmatic breaths."
        )
    else:
        reply = (
            f"### 📚 Concept Analysis: **\"{query}\"**\n\n"
            "- **Core Principle**: Break this problem down into atomic components. Isolate what is known from what requires derivation.\n"
            "- **Feynman Explanation**: Try stating the core mechanism in 1 single sentence without technical jargon.\n"
            "- **Practical Next Step**: Write a small test case or solve 1 concrete exercise before moving to the next chapter.\n\n"
            "> 🔑 **Connect Gemini AI**: To get complete, unrestricted real-time AI explanations for this topic, enter your free Gemini API key in the top banner!"
        )

    session_id = _append_to_session(req.session_id, query, reply, mode)
    return {"reply": reply, "source": "local_engine", "session_id": session_id}

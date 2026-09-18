import React, { useState, useEffect } from "react";
import { Upload, FileText, CheckCircle2, RotateCw, ExternalLink, Plus, BookOpen, Layers, Compass, Trash2, Quote, Sparkles, X, Shuffle, Check } from "lucide-react";
import { GlowBadge } from "../ui/GlowBadge";
import { MagneticButton } from "../ui/MagneticButton";
import { apiUrl } from "../../lib/api";

export const MaterialsTab = ({ user }) => {
  const [activeTab, setActiveTab] = useState("flashcards"); // "flashcards" | "files" | "links"
  const [documents, setDocuments] = useState([]);
  const [quickLinks, setQuickLinks] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState("");
  const [dailyQuote, setDailyQuote] = useState("");
  const [productivityTip, setProductivityTip] = useState("");
  const [showAddLinkModal, setShowAddLinkModal] = useState(false);
  const [newLink, setNewLink] = useState({ name: "", url: "", category: "Study Tools", description: "" });

  // Dynamic Flashcards state - starts empty for clean user isolation
  const [flashcards, setFlashcards] = useState([]);

  const [currentCardIdx, setCurrentCardIdx] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [knownCount, setKnownCount] = useState(0);
  const [showAddCardModal, setShowAddCardModal] = useState(false);
  const [newCard, setNewCard] = useState({ question: "", answer: "", category: "General" });
  const [isGeneratingCards, setIsGeneratingCards] = useState(false);

  const fetchFlashcards = async () => {
    if (!user?.id) return;
    try {
      const res = await fetch(apiUrl(`/api/materials/flashcards?user_id=${user.id}`));
      if (res.ok) {
        const data = await res.json();
        setFlashcards(data || []);
        const masteredCount = (data || []).filter((c) => c.mastered).length;
        setKnownCount(masteredCount);
      }
    } catch (e) {
      console.warn("Flashcards fetch error:", e);
    }
  };

  const fetchMotivation = () => {
    fetch(apiUrl("/api/materials/daily-motivation"))
      .then((r) => r.json())
      .then((data) => {
        setDailyQuote(data.quote || "The expert in anything was once a beginner.");
        setProductivityTip(data.productivity_tip || "Use the Pomodoro Technique for deep focus sprints.");
      })
      .catch((e) => console.log("Motivation fetch note:", e));
  };

  const fetchDocuments = () => {
    if (!user?.id) return;
    fetch(apiUrl(`/api/materials/documents?user_id=${user.id}`))
      .then((r) => r.json())
      .then((data) => setDocuments(data || []))
      .catch((e) => console.log("Documents fetch note:", e));
  };

  const fetchLinks = () => {
    fetch(apiUrl("/api/materials/links"))
      .then((r) => r.json())
      .then((data) => setQuickLinks(data))
      .catch((e) => console.log("Links fetch note:", e));
  };

  useEffect(() => {
    if (user?.id) {
      fetchFlashcards();
      fetchDocuments();
    }
    fetchLinks();
    fetchMotivation();
  }, [user?.id]);

  const currentCard = flashcards[currentCardIdx] || flashcards[0] || {
    question: "No flashcards yet!",
    answer: "Click '+ NEW CARD' or '✨ AI GENERATE' to add study cards.",
    category: "General",
  };

  const handleNextCard = async (known) => {
    if (known && currentCard && currentCard.id) {
      setKnownCount((prev) => prev + 1);
      try {
        await fetch(apiUrl(`/api/materials/flashcards/${currentCard.id}/mastered`), {
          method: "PATCH",
        });
        setFlashcards((prev) =>
          prev.map((c) => (c.id === currentCard.id ? { ...c, mastered: true } : c))
        );
      } catch (e) {
        // Local fallback
      }
    }
    setIsFlipped(false);
    if (flashcards.length > 0) {
      if (currentCardIdx < flashcards.length - 1) {
        setCurrentCardIdx((prev) => prev + 1);
      } else {
        setCurrentCardIdx(0);
      }
    }
  };

  const handleAddCard = async (e) => {
    e.preventDefault();
    if (!newCard.question.trim() || !newCard.answer.trim() || !user?.id) return;
    try {
      const res = await fetch(apiUrl("/api/materials/flashcards"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...newCard, user_id: user.id }),
      });
      if (res.ok) {
        const created = await res.json();
        setFlashcards((prev) => [created, ...prev]);
        setShowAddCardModal(false);
        setNewCard({ question: "", answer: "", category: "General" });
        setCurrentCardIdx(0);
        setIsFlipped(false);
      }
    } catch (err) {
      console.warn("Add card error:", err);
    }
  };

  const handleGenerateAICards = async () => {
    if (!user?.id) return;
    setIsGeneratingCards(true);
    try {
      const res = await fetch(apiUrl("/api/materials/flashcards/generate"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: user.id }),
      });
      if (res.ok) {
        const newCards = await res.json();
        if (newCards && newCards.length > 0) {
          setFlashcards((prev) => [...newCards, ...prev]);
          setCurrentCardIdx(0);
          setIsFlipped(false);
        }
      }
    } catch (err) {
      console.warn("Generate flashcards error:", err);
    } finally {
      setIsGeneratingCards(false);
    }
  };

  const handleDeleteCard = async (cardId, e) => {
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this flashcard?")) return;
    try {
      await fetch(apiUrl(`/api/materials/flashcards/${cardId}`), { method: "DELETE" });
      setFlashcards((prev) => {
        const updated = prev.filter((c) => c.id !== cardId);
        if (currentCardIdx >= updated.length) setCurrentCardIdx(Math.max(0, updated.length - 1));
        return updated;
      });
      setIsFlipped(false);
    } catch (err) {
      console.warn("Delete card error:", err);
    }
  };

  const handleShuffleCards = () => {
    setFlashcards((prev) => [...prev].sort(() => Math.random() - 0.5));
    setCurrentCardIdx(0);
    setIsFlipped(false);
  };

  // Real file upload to backend using src/ai_assistant.py
  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file || !user?.id) return;

    setIsUploading(true);
    setUploadSuccess("");

    const formData = new FormData();
    formData.append("file", file);
    formData.append("user_id", user.id);

    try {
      const res = await fetch(apiUrl("/api/materials/upload"), {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (data.success) {
        setUploadSuccess(`Indexed "${file.name}" into Gemini AI knowledgebase!`);
        fetchDocuments();
      } else {
        alert(`Upload error: ${data.error}`);
      }
    } catch (err) {
      alert("Failed to upload document to backend.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeleteDocument = async (docId, e) => {
    e.stopPropagation();
    if (!confirm("Are you sure you want to remove this document from your study library?")) return;
    try {
      await fetch(apiUrl(`/api/materials/documents/${docId}`), { method: "DELETE" });
      fetchDocuments();
    } catch (err) {
      console.warn("Delete doc error:", err);
    }
  };

  const handleAddLink = async (e) => {
    e.preventDefault();
    if (!newLink.name.trim() || !newLink.url.trim()) return;

    try {
      const res = await fetch(apiUrl("/api/materials/links"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newLink),
      });
      if (res.ok) {
        fetchLinks();
        setShowAddLinkModal(false);
        setNewLink({ name: "", url: "", category: "Study Tools", description: "" });
      }
    } catch (err) {
      console.warn("Add link error:", err);
    }
  };

  const handleDeleteLink = async (linkName, e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!confirm(`Remove quick link "${linkName}"?`)) return;
    try {
      await fetch(apiUrl(`/api/materials/links/${encodeURIComponent(linkName)}`), {
        method: "DELETE",
      });
      fetchLinks();
    } catch (err) {
      console.warn("Delete link error:", err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Daily Motivation & Productivity Protocol Banner (from src/study_materials.py) */}
      <div className="p-4 rounded-xl bg-[#090C12] border border-neutral-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="p-2 rounded-lg bg-[#121622] border border-cyan-500/30 text-cyan-400 mt-0.5">
            <Quote className="w-4 h-4" />
          </div>
          <div>
            <div className="text-xs font-mono text-cyan-400 font-bold uppercase flex items-center gap-1.5">
              <span>DAILY MOTIVATION // COGNITIVE PROTOCOL</span>
            </div>
            <div className="text-sm font-sans text-white italic mt-0.5">"{dailyQuote}"</div>
            <div className="text-xs font-mono text-neutral-400 mt-1">
              <strong className="text-emerald-400">Protocol Tip:</strong> {productivityTip}
            </div>
          </div>
        </div>

        <button
          onClick={fetchMotivation}
          className="text-xs font-mono text-neutral-400 hover:text-white px-3 py-1.5 rounded border border-neutral-800 hover:border-neutral-700 transition-colors flex items-center gap-1.5 flex-shrink-0 cursor-pointer"
        >
          <RotateCw className="w-3 h-3 text-cyan-400" /> SHUFFLE TIP
        </button>
      </div>

      {/* Sub-Navigation Tabs */}
      <div className="flex items-center justify-between border-b border-neutral-800 pb-3 flex-wrap gap-2">
        <div className="flex items-center gap-2">
          {[
            { id: "flashcards", label: "ACTIVE RECALL FLASHCARDS", icon: Layers },
            { id: "files", label: "LECTURE REPOSITORY (RAG)", icon: BookOpen },
            { id: "links", label: "QUICK LINKS & TOOLS", icon: Compass },
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-mono transition-colors cursor-pointer ${
                  activeTab === tab.id
                    ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 font-bold"
                    : "text-neutral-400 hover:text-white hover:bg-[#121622]"
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        <div className="flex items-center gap-2">
          {activeTab === "flashcards" && (
            <>
              <button
                onClick={handleShuffleCards}
                title="Shuffle card order"
                className="text-xs font-mono text-neutral-400 hover:text-white px-2.5 py-1.5 rounded border border-neutral-800 hover:bg-[#121622] transition-colors flex items-center gap-1 cursor-pointer"
              >
                <Shuffle className="w-3.5 h-3.5 text-cyan-400" /> SHUFFLE
              </button>
              <button
                onClick={handleGenerateAICards}
                disabled={isGeneratingCards}
                title="Auto-generate flashcards from uploaded materials or AI"
                className="text-xs font-mono bg-[#111726] hover:bg-[#162035] text-purple-300 border border-purple-500/40 font-bold px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-colors cursor-pointer disabled:opacity-50"
              >
                <Sparkles className="w-3.5 h-3.5 text-purple-400" />
                {isGeneratingCards ? "GENERATING..." : "AI GENERATE"}
              </button>
              <button
                onClick={() => setShowAddCardModal(true)}
                title="Add a custom flashcard"
                className="text-xs font-mono bg-cyan-500 hover:bg-cyan-400 text-black font-bold px-3 py-1.5 rounded-lg flex items-center gap-1 transition-colors cursor-pointer"
              >
                <Plus className="w-3.5 h-3.5" /> NEW CARD
              </button>
            </>
          )}

          {activeTab === "links" && (
            <button
              onClick={() => setShowAddLinkModal(true)}
              className="text-xs font-mono bg-cyan-500 hover:bg-cyan-400 text-black font-bold px-3 py-1.5 rounded-lg flex items-center gap-1 transition-colors cursor-pointer"
            >
              <Plus className="w-3.5 h-3.5" /> ADD LINK
            </button>
          )}
        </div>
      </div>

      {/* TAB 1: Active Recall Flashcards */}
      {activeTab === "flashcards" && (
        <div className="flex flex-col items-center justify-center py-6">
          <div className="flex items-center justify-between w-full max-w-xl mb-4 font-mono text-xs">
            <div className="flex items-center gap-2">
              <span className="text-neutral-400">
                CARD {flashcards.length > 0 ? currentCardIdx + 1 : 0} OF {flashcards.length}
              </span>
              {currentCard?.mastered && (
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                  MASTERED
                </span>
              )}
            </div>
            <GlowBadge status={knownCount > 0 ? "active" : "idle"}>
              MASTERED: {knownCount} / {flashcards.length}
            </GlowBadge>
          </div>

          <div
            onClick={() => setIsFlipped(!isFlipped)}
            className="w-full max-w-xl min-h-[270px] p-8 rounded-2xl bg-[#0B0E14] border border-neutral-800 hover:border-cyan-500/40 transition-all cursor-pointer flex flex-col justify-between relative select-none group"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono text-cyan-400 font-bold uppercase tracking-wider">
                {currentCard?.category || "General"}
              </span>
              <div className="flex items-center gap-3">
                {currentCard?.id && (
                  <button
                    onClick={(e) => handleDeleteCard(currentCard.id, e)}
                    title="Delete flashcard"
                    className="text-neutral-600 hover:text-red-400 p-1 rounded transition-colors"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                )}
                <span className="text-xs font-mono text-neutral-500 flex items-center gap-1">
                  <RotateCw className="w-3 h-3" /> FLIP
                </span>
              </div>
            </div>

            <div className="my-6">
              <div className="text-xs font-mono text-neutral-400 uppercase mb-2">
                {isFlipped ? "Answer / Key Concept:" : "Prompt / Recall Challenge:"}
              </div>
              <p className="text-base font-sans text-white leading-relaxed">
                {isFlipped ? currentCard?.answer : currentCard?.question}
              </p>
            </div>

            <div className="text-center text-xs font-mono text-neutral-500">
              {isFlipped ? "Tap card to hide answer" : "Attempt mental recall before flipping"}
            </div>
          </div>

          <div className="flex items-center gap-4 mt-6">
            <MagneticButton
              variant="danger"
              onClick={() => handleNextCard(false)}
              className="text-xs font-mono px-6 py-2.5"
            >
              REVIEW AGAIN
            </MagneticButton>
            <MagneticButton
              variant="primary"
              onClick={() => handleNextCard(true)}
              className="text-xs font-mono px-6 py-2.5 flex items-center gap-1.5"
            >
              <Check className="w-3.5 h-3.5" /> I KNOW THIS CARD
            </MagneticButton>
          </div>
        </div>
      )}

      {/* TAB 2: Uploaded Documents & Real Parser */}
      {activeTab === "files" && (
        <div className="space-y-6">
          <label className="border border-dashed border-neutral-700/80 hover:border-cyan-500/50 rounded-xl p-8 bg-[#090C12] text-center cursor-pointer transition-colors block">
            <input
              type="file"
              accept=".pdf,.docx,.pptx,.txt,.md"
              onChange={handleFileUpload}
              className="hidden"
            />
            <Upload className="w-8 h-8 text-neutral-400 mx-auto mb-3" />
            <h3 className="text-sm font-mono font-bold text-white mb-1">
              {isUploading ? "PARSING DOCUMENT WITH AI ASSISTANT..." : "CLICK TO BROWSE & UPLOAD LECTURE FILES"}
            </h3>
            <p className="text-xs text-neutral-500 font-mono">
              Supports PDF (PyPDF2), Word (python-docx), PowerPoint (python-pptx), and TXT. Auto-indexes for Gemini Q&A.
            </p>
            {uploadSuccess && (
              <div className="mt-3 text-xs font-mono text-emerald-400 font-bold flex items-center justify-center gap-1.5">
                <CheckCircle2 className="w-4 h-4" /> {uploadSuccess}
              </div>
            )}
          </label>

          <div className="space-y-3">
            <div className="text-xs font-mono text-neutral-400 uppercase tracking-wider">
              PARSED REPOSITORY DOCUMENTS ({documents.length})
            </div>
            {documents.length === 0 ? (
              <div className="p-8 text-center text-xs font-mono text-neutral-500 rounded-xl bg-[#0B0E14] border border-neutral-800">
                No lecture notes uploaded yet. Upload a PDF or Word document above to enable RAG document chat and flashcard generation.
              </div>
            ) : (
              documents.map((doc) => (
                <div
                  key={doc.id}
                  className="p-4 rounded-xl bg-[#0B0E14] border border-neutral-800 hover:border-neutral-700 transition-colors flex items-center justify-between"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-lg bg-[#121622] border border-neutral-700 flex items-center justify-center text-cyan-400">
                      <FileText className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="text-sm font-mono font-bold text-white flex items-center gap-2">
                        {doc.name}
                        <GlowBadge status="cyan">INDEXED</GlowBadge>
                      </div>
                      <div className="text-xs text-neutral-400 mt-0.5 max-w-xl">{doc.summary}</div>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 text-xs font-mono text-neutral-500">
                    <div className="text-right">
                      <div>{doc.size}</div>
                      <div>{doc.date}</div>
                    </div>
                    <button
                      onClick={(e) => handleDeleteDocument(doc.id, e)}
                      title="Delete document"
                      className="p-2 rounded hover:bg-neutral-800 text-neutral-500 hover:text-red-400 transition-colors cursor-pointer"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* TAB 4: Quick Links from src/study_materials.py */}
      {activeTab === "links" && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {(quickLinks.length > 0
            ? quickLinks
            : [
                { name: "Khan Academy", url: "https://www.khanacademy.org/", category: "Courses", description: "Free online courses and tutorials" },
                { name: "Coursera", url: "https://www.coursera.org/", category: "University", description: "University-level online courses" },
                { name: "Pomofocus", url: "https://pomofocus.io/", category: "Productivity", description: "Online Pomodoro timer" },
                { name: "Forest", url: "https://www.forestapp.cc/", category: "Focus App", description: "Stay focused and plant virtual trees" },
                { name: "Quizlet", url: "https://quizlet.com/", category: "Study Tools", description: "Create and study with flashcards" },
                { name: "Google AI Studio", url: "https://aistudio.google.com/", category: "AI Tools", description: "Get your free Gemini API Key" },
              ]
          ).map((link, idx) => (
            <div
              key={idx}
              className="p-5 rounded-xl bg-[#0B0E14] border border-neutral-800 hover:border-cyan-500/40 transition-colors flex flex-col justify-between group relative"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-mono text-neutral-500">{link.category}</span>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={(e) => handleDeleteLink(link.name, e)}
                      title="Remove quick link"
                      className="opacity-0 group-hover:opacity-100 text-neutral-500 hover:text-red-400 transition-opacity p-0.5 cursor-pointer"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                    <a href={link.url} target="_blank" rel="noreferrer" className="text-neutral-500 group-hover:text-cyan-400 transition-colors">
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  </div>
                </div>
                <a href={link.url} target="_blank" rel="noreferrer">
                  <h4 className="text-sm font-mono font-bold text-white group-hover:text-cyan-300 transition-colors">
                    {link.name}
                  </h4>
                  <p className="text-xs text-neutral-400 mt-1 leading-relaxed">{link.description}</p>
                </a>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Custom Quick Link Modal */}
      {showAddLinkModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-[#0B0E14] border border-neutral-800 rounded-xl max-w-md w-full p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-neutral-800 pb-3">
              <h3 className="text-sm font-mono font-bold text-white flex items-center gap-2">
                <Plus className="w-4 h-4 text-cyan-400" /> ADD CUSTOM QUICK LINK
              </h3>
              <button
                onClick={() => setShowAddLinkModal(false)}
                className="p-1 rounded hover:bg-neutral-800 text-neutral-400 hover:text-white cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleAddLink} className="space-y-3 font-mono text-xs">
              <div>
                <label className="block text-neutral-400 mb-1">RESOURCE NAME</label>
                <input
                  type="text"
                  required
                  value={newLink.name}
                  onChange={(e) => setNewLink({ ...newLink, name: e.target.value })}
                  placeholder="e.g. arXiv Computer Vision"
                  className="w-full px-3 py-2 rounded bg-[#07090D] border border-neutral-700 text-white focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="block text-neutral-400 mb-1">DESTINATION URL</label>
                <input
                  type="url"
                  required
                  value={newLink.url}
                  onChange={(e) => setNewLink({ ...newLink, url: e.target.value })}
                  placeholder="https://..."
                  className="w-full px-3 py-2 rounded bg-[#07090D] border border-neutral-700 text-white focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="block text-neutral-400 mb-1">CATEGORY</label>
                <input
                  type="text"
                  value={newLink.category}
                  onChange={(e) => setNewLink({ ...newLink, category: e.target.value })}
                  placeholder="e.g. Research / Tools"
                  className="w-full px-3 py-2 rounded bg-[#07090D] border border-neutral-700 text-white focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="block text-neutral-400 mb-1">SHORT DESCRIPTION</label>
                <input
                  type="text"
                  value={newLink.description}
                  onChange={(e) => setNewLink({ ...newLink, description: e.target.value })}
                  placeholder="e.g. Deep learning paper repository"
                  className="w-full px-3 py-2 rounded bg-[#07090D] border border-neutral-700 text-white focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddLinkModal(false)}
                  className="px-3 py-2 rounded border border-neutral-800 hover:bg-neutral-800 text-neutral-400 cursor-pointer"
                >
                  CANCEL
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded bg-cyan-500 hover:bg-cyan-400 text-black font-bold cursor-pointer"
                >
                  SAVE LINK
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Custom Flashcard Modal */}
      {showAddCardModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-[#0B0E14] border border-neutral-800 rounded-xl max-w-md w-full p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-neutral-800 pb-3">
              <h3 className="text-sm font-mono font-bold text-white flex items-center gap-2">
                <Plus className="w-4 h-4 text-cyan-400" /> CREATE CUSTOM FLASHCARD
              </h3>
              <button
                onClick={() => setShowAddCardModal(false)}
                className="p-1 rounded hover:bg-neutral-800 text-neutral-400 hover:text-white cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleAddCard} className="space-y-3 font-mono text-xs">
              <div>
                <label className="block text-neutral-400 mb-1">CATEGORY / TOPIC</label>
                <input
                  type="text"
                  value={newCard.category}
                  onChange={(e) => setNewCard({ ...newCard, category: e.target.value })}
                  placeholder="e.g. Algorithms, Machine Learning, Operating Systems"
                  className="w-full px-3 py-2 rounded bg-[#07090D] border border-neutral-700 text-white focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="block text-neutral-400 mb-1">PROMPT / QUESTION (FRONT)</label>
                <textarea
                  rows={3}
                  required
                  value={newCard.question}
                  onChange={(e) => setNewCard({ ...newCard, question: e.target.value })}
                  placeholder="What is the concept or question to recall?"
                  className="w-full px-3 py-2 rounded bg-[#07090D] border border-neutral-700 text-white focus:outline-none focus:border-cyan-500 font-sans text-xs"
                />
              </div>

              <div>
                <label className="block text-neutral-400 mb-1">ANSWER / EXPLANATION (BACK)</label>
                <textarea
                  rows={3}
                  required
                  value={newCard.answer}
                  onChange={(e) => setNewCard({ ...newCard, answer: e.target.value })}
                  placeholder="The concise answer and explanation to reveal on flip."
                  className="w-full px-3 py-2 rounded bg-[#07090D] border border-neutral-700 text-white focus:outline-none focus:border-cyan-500 font-sans text-xs"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddCardModal(false)}
                  className="px-3 py-2 rounded border border-neutral-800 hover:bg-neutral-800 text-neutral-400 cursor-pointer"
                >
                  CANCEL
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded bg-cyan-500 hover:bg-cyan-400 text-black font-bold cursor-pointer"
                >
                  SAVE FLASHCARD
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

import React, { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Send, Sparkles, Bot, User, Copy, Check, Terminal, Key, RefreshCw, ChevronDown, ChevronUp, ExternalLink, Plus, History, Globe, BookOpen, X, Trash2 } from "lucide-react";
import { GlowBadge } from "../ui/GlowBadge";

const MarkdownContent = ({ content }) => {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        h1: ({ node, ...props }) => (
          <h1 className="text-base font-mono font-bold text-white mt-3 mb-1.5 pb-1 border-b border-neutral-800" {...props} />
        ),
        h2: ({ node, ...props }) => (
          <h2 className="text-sm font-mono font-bold text-cyan-300 mt-2.5 mb-1" {...props} />
        ),
        h3: ({ node, ...props }) => (
          <h3 className="text-xs font-mono font-bold text-cyan-400 mt-2 mb-1" {...props} />
        ),
        p: ({ node, ...props }) => (
          <p className="text-[13.5px] leading-relaxed mb-2 last:mb-0 text-neutral-200" {...props} />
        ),
        strong: ({ node, ...props }) => (
          <strong className="font-semibold text-white" {...props} />
        ),
        em: ({ node, ...props }) => (
          <em className="italic text-cyan-200/90" {...props} />
        ),
        ul: ({ node, ...props }) => (
          <ul className="list-disc list-outside pl-4 space-y-1 my-2 text-[13px] text-neutral-300" {...props} />
        ),
        ol: ({ node, ...props }) => (
          <ol className="list-decimal list-outside pl-4 space-y-1 my-2 text-[13px] text-neutral-300" {...props} />
        ),
        li: ({ node, ...props }) => (
          <li className="leading-relaxed" {...props} />
        ),
        blockquote: ({ node, ...props }) => (
          <blockquote className="border-l-2 border-cyan-500/60 pl-3 py-1 my-2 bg-cyan-950/20 text-neutral-300 text-xs italic rounded-r" {...props} />
        ),
        code: ({ node, inline, className, children, ...props }) => {
          if (inline) {
            return (
              <code className="bg-[#07090D] text-cyan-300 font-mono text-[12px] px-1.5 py-0.5 rounded border border-neutral-800" {...props}>
                {children}
              </code>
            );
          }
          return (
            <code className="font-mono text-xs text-neutral-200" {...props}>
              {children}
            </code>
          );
        },
        pre: ({ node, ...props }) => (
          <pre className="bg-[#05060A] border border-neutral-800/90 rounded-lg p-3 my-2.5 overflow-x-auto text-xs font-mono text-cyan-200" {...props} />
        ),
        a: ({ node, ...props }) => (
          <a className="text-cyan-400 hover:text-cyan-300 underline inline-flex items-center gap-0.5" target="_blank" rel="noreferrer" {...props} />
        ),
        table: ({ node, ...props }) => (
          <div className="overflow-x-auto my-2">
            <table className="min-w-full border-collapse border border-neutral-800 text-xs font-mono" {...props} />
          </div>
        ),
        th: ({ node, ...props }) => (
          <th className="border border-neutral-800 bg-[#111726] px-3 py-1.5 text-left text-cyan-300 font-bold" {...props} />
        ),
        td: ({ node, ...props }) => (
          <td className="border border-neutral-800 px-3 py-1.5 text-neutral-300" {...props} />
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  );
};

export const AIChatTab = () => {
  const [messages, setMessages] = useState([
    {
      id: "m_1",
      role: "assistant",
      text: "👋 Welcome operator to **AURA // AI Deep Focus & Telemetry Companion**!\n\nI am your AI study copilot. Beyond this chat, this entire workstation features **Live Eye Tracking (EAR)**, a **Native YOLOv8 Phone Distraction Guard**, **Pomodoro Sprints**, **Document Flashcards**, and **Telemetry Analytics**.\n\nYou can query me in **🌐 Internet Mode** for broad STEM/CS knowledge, switch to **📚 My Materials Mode** to test yourself strictly against your uploaded lecture notes, or ask me: *'What is the point of this website?'*",
      timestamp: "Just now",
    },
  ]);
  const [input, setInput] = useState("");
  const [mode, setMode] = useState("internet"); // "internet" | "materials"
  const [sessionId, setSessionId] = useState(null);
  const [isTyping, setIsTyping] = useState(false);
  const [copiedId, setCopiedId] = useState(null);
  const [apiKey, setApiKey] = useState(() => localStorage.getItem("aura_gemini_key") || "");
  const [showKeyBanner, setShowKeyBanner] = useState(!localStorage.getItem("aura_gemini_key"));
  const [keySaved, setKeySaved] = useState(false);
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  const [pastSessions, setPastSessions] = useState([]);
  const [loadingSessions, setLoadingSessions] = useState(false);
  const chatEndRef = useRef(null);

  const promptChips = mode === "internet"
    ? [
        "What is the point of this website?",
        "Quiz me on 3 questions",
        "Explain Backpropagation simply",
        "How does Eye Aspect Ratio (EAR) work?",
        "Tips to combat mental fatigue",
      ]
    : [
        "What is the point of this website?",
        "Summarize my uploaded notes",
        "Generate 3 flashcards from my material",
        "What are the core equations in my document?",
        "Explain the hardest concept in my notes",
      ];

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSaveKey = async () => {
    localStorage.setItem("aura_gemini_key", apiKey.trim());
    setKeySaved(true);
    try {
      await fetch("http://127.0.0.1:8000/api/ai/set-key", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ api_key: apiKey.trim() }),
      });
    } catch (e) {
      // Ignored if offline
    }
    setTimeout(() => {
      setKeySaved(false);
      setShowKeyBanner(false);
    }, 1200);
  };

  const handleNewChat = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/ai/new-chat", { method: "POST" });
      if (res.ok) {
        const data = await res.json();
        setSessionId(data.session_id);
      }
    } catch (e) {
      setSessionId(`sess_${Date.now()}`);
    }
    setMessages([
      {
        id: `m_init_${Date.now()}`,
        role: "assistant",
        text: `New study session initialized (${mode === "internet" ? "🌐 Internet Mode" : "📚 My Materials Mode"}). Ready for your next concept!`,
        timestamp: "Just now",
      },
    ]);
  };

  const handleOpenHistory = async () => {
    setShowHistoryModal(true);
    setLoadingSessions(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/ai/sessions");
      if (res.ok) {
        const data = await res.json();
        setPastSessions(data || []);
      }
    } catch (e) {
      console.warn("Failed to load chat sessions:", e);
    } finally {
      setLoadingSessions(false);
    }
  };

  const handleLoadSession = (session) => {
    if (!session || !session.messages || session.messages.length === 0) return;
    setSessionId(session.id);
    const restored = session.messages.map((m, idx) => ({
      id: `restored_${idx}_${Date.now()}`,
      role: m.role || (m.question ? "user" : "assistant"),
      text: m.text || m.question || m.answer || "",
      timestamp: m.timestamp || "Past session",
    }));
    setMessages(restored);
    setShowHistoryModal(false);
  };

  const handleDeleteSession = async (sessId, e) => {
    e.stopPropagation();
    try {
      await fetch(`http://127.0.0.1:8000/api/ai/sessions/${sessId}`, { method: "DELETE" });
      setPastSessions((prev) => prev.filter((s) => s.id !== sessId));
      if (sessionId === sessId) {
        handleNewChat();
      }
    } catch (err) {
      console.warn("Delete session error:", err);
    }
  };

  const handleSend = async (textToSend) => {
    const query = textToSend || input;
    if (!query.trim()) return;

    const userMsg = {
      id: `u_${Date.now()}`,
      role: "user",
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsTyping(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/api/ai/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: query,
          mode: mode,
          api_key: apiKey.trim() || undefined,
          session_id: sessionId || undefined,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        if (data.session_id) setSessionId(data.session_id);
        setMessages((prev) => [
          ...prev,
          {
            id: `a_${Date.now()}`,
            role: "assistant",
            text: data.reply || data.response,
            timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          },
        ]);
        setIsTyping(false);
        return;
      }
    } catch (e) {
      console.warn("Backend chat fetch error:", e);
    }

    // Fallback response if fetch completely fails
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          id: `a_${Date.now()}`,
          role: "assistant",
          text: `Analyzing: **"${query}"**.\n\nMake sure the FastAPI backend is active at \`http://127.0.0.1:8000\` and your Gemini API key is configured above to enable live Gemini 3.5 Flash tutor answers!`,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
      setIsTyping(false);
    }, 600);
  };

  const copyToClipboard = (id, text) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 1500);
  };

  return (
    <div className="rounded-xl border border-neutral-800 bg-[#0B0E14] h-[680px] flex flex-col overflow-hidden relative">
      {/* Top Header */}
      <div className="p-4 border-b border-neutral-800/80 bg-[#080A0F] flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-[#111726] border border-cyan-500/40 flex items-center justify-center">
            <Bot className="w-4 h-4 text-cyan-400" />
          </div>
          <div>
            <div className="text-sm font-mono font-bold text-white flex items-center gap-2">
              GEMINI 3.5 FLASH COPILOT
              {apiKey ? (
                <GlowBadge status="cyan">3.5 FLASH LIVE</GlowBadge>
              ) : (
                <GlowBadge status="warning">LOCAL ASSISTANT</GlowBadge>
              )}
            </div>
            <div className="text-[11px] font-mono text-neutral-500">
              STEM TUTORING // CODE EXPLANATION // RAG LECTURE SEARCH
            </div>
          </div>
        </div>

        {/* Dual-Mode Selector & Chat Actions */}
        <div className="flex items-center gap-2 flex-wrap">
          {/* Mode Switcher */}
          <div className="flex items-center bg-[#05060A] p-1 rounded-lg border border-neutral-800 text-xs font-mono">
            <button
              onClick={() => setMode("internet")}
              title="Query broad STEM & web knowledge"
              className={`px-3 py-1 rounded transition-colors flex items-center gap-1.5 cursor-pointer ${
                mode === "internet"
                  ? "bg-cyan-500/20 text-cyan-300 font-bold border border-cyan-500/30"
                  : "text-neutral-400 hover:text-neutral-200"
              }`}
            >
              <Globe className="w-3 h-3" /> INTERNET
            </button>
            <button
              onClick={() => setMode("materials")}
              title="Query strictly against your uploaded lecture notes"
              className={`px-3 py-1 rounded transition-colors flex items-center gap-1.5 cursor-pointer ${
                mode === "materials"
                  ? "bg-purple-500/20 text-purple-300 font-bold border border-purple-500/30"
                  : "text-neutral-400 hover:text-neutral-200"
              }`}
            >
              <BookOpen className="w-3 h-3" /> MY MATERIALS
            </button>
          </div>

          <button
            onClick={handleNewChat}
            title="Start new conversation"
            className="text-xs font-mono text-neutral-400 hover:text-white px-2.5 py-1.5 rounded border border-neutral-800 hover:bg-[#121622] transition-colors flex items-center gap-1 cursor-pointer"
          >
            <Plus className="w-3.5 h-3.5 text-cyan-400" /> NEW
          </button>

          <button
            onClick={handleOpenHistory}
            title="View recent chat sessions"
            className="text-xs font-mono text-neutral-400 hover:text-white px-2.5 py-1.5 rounded border border-neutral-800 hover:bg-[#121622] transition-colors flex items-center gap-1 cursor-pointer"
          >
            <History className="w-3.5 h-3.5 text-purple-400" /> RECENT
          </button>

          <button
            onClick={() => setShowKeyBanner(!showKeyBanner)}
            className="text-xs font-mono text-neutral-400 hover:text-cyan-400 px-2.5 py-1.5 rounded border border-neutral-800 hover:border-cyan-500/40 transition-colors flex items-center gap-1 cursor-pointer"
          >
            <Key className="w-3.5 h-3.5" />
            {apiKey ? "KEY" : "ADD KEY"}
            {showKeyBanner ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          </button>
        </div>
      </div>

      {/* Collapsible Key Configuration Banner */}
      {showKeyBanner && (
        <div className="p-4 bg-[#0A0D15] border-b border-cyan-500/30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs font-mono">
          <div className="space-y-1">
            <div className="text-white font-semibold flex items-center gap-2">
              <Key className="w-4 h-4 text-cyan-400" /> Enter Google Gemini API Key (Gemini 3.5 Flash Active)
            </div>
            <div className="text-neutral-400 text-[11px]">
              Keys are 100% free from{" "}
              <a
                href="https://aistudio.google.com/app/apikey"
                target="_blank"
                rel="noreferrer"
                className="text-cyan-400 underline inline-flex items-center gap-0.5"
              >
                Google AI Studio <ExternalLink className="w-2.5 h-2.5" />
              </a>
              . Stored securely in your environment.
            </div>
          </div>

          <div className="flex items-center gap-2 w-full sm:w-auto">
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="Paste AIzaSy... key"
              className="px-3 py-1.5 rounded bg-[#05060A] border border-neutral-700 text-white text-xs font-mono focus:outline-none focus:border-cyan-500 w-full sm:w-56"
            />
            <button
              onClick={handleSaveKey}
              className="px-3 py-1.5 rounded bg-cyan-500 hover:bg-cyan-400 text-black font-bold text-xs flex items-center gap-1 transition-colors flex-shrink-0 cursor-pointer"
            >
              {keySaved ? <Check className="w-3 h-3" /> : "SAVE"}
            </button>
          </div>
        </div>
      )}

      {/* Messages Stream */}
      <div className="flex-1 p-6 overflow-y-auto space-y-6">
        {messages.map((m) => {
          const isAssistant = m.role === "assistant";
          return (
            <div
              key={m.id}
              className={`flex gap-3 max-w-3xl ${isAssistant ? "mr-auto" : "ml-auto flex-row-reverse"}`}
            >
              <div
                className={`w-7 h-7 rounded-lg flex-shrink-0 flex items-center justify-center border text-xs font-mono ${
                  isAssistant
                    ? "bg-[#111726] border-cyan-500/40 text-cyan-400"
                    : "bg-[#1A2234] border-neutral-700 text-neutral-200"
                }`}
              >
                {isAssistant ? <Bot className="w-3.5 h-3.5" /> : <User className="w-3.5 h-3.5" />}
              </div>

              <div className="space-y-1">
                <div
                  className={`p-4 rounded-xl text-sm leading-relaxed ${
                    isAssistant
                      ? "bg-[#0F1420] border border-neutral-800 text-neutral-200"
                      : "bg-cyan-500/10 border border-cyan-500/30 text-cyan-100"
                  }`}
                >
                  <MarkdownContent content={m.text} />
                </div>

                <div className="flex items-center gap-2 px-1 text-[10px] font-mono text-neutral-500">
                  <span>{m.timestamp}</span>
                  {isAssistant && (
                    <button
                      onClick={() => copyToClipboard(m.id, m.text)}
                      className="hover:text-neutral-300 flex items-center gap-1 transition-colors ml-2"
                    >
                      {copiedId === m.id ? (
                        <>
                          <Check className="w-3 h-3 text-emerald-400" /> COPIED
                        </>
                      ) : (
                        <>
                          <Copy className="w-3 h-3" /> COPY
                        </>
                      )}
                    </button>
                  )}
                </div>
              </div>
            </div>
          );
        })}

        {isTyping && (
          <div className="flex gap-3 mr-auto items-center text-xs font-mono text-cyan-400">
            <div className="w-7 h-7 rounded-lg bg-[#111726] border border-cyan-500/40 flex items-center justify-center">
              <Bot className="w-3.5 h-3.5 animate-spin" />
            </div>
            <span>GEMINI 3.5 FLASH IS REASONING...</span>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Prompt Suggestion Chips */}
      <div className="px-6 py-2 border-t border-neutral-800/60 bg-[#080A0F] flex items-center gap-2 overflow-x-auto no-scrollbar">
        {promptChips.map((chip, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(chip)}
            className="flex-shrink-0 text-[11px] font-mono px-3 py-1 rounded-full border border-neutral-800 bg-[#0E121A] text-neutral-400 hover:text-cyan-400 hover:border-cyan-500/30 transition-colors cursor-pointer"
          >
            {chip}
          </button>
        ))}
      </div>

      {/* Input Box */}
      <div className="p-4 border-t border-neutral-800 bg-[#080A0F]">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={
              mode === "materials"
                ? "Querying your uploaded materials (e.g. 'Summarize section 2', 'What are the main formulas?')..."
                : "Ask anything (e.g. 'Explain quicksort', 'Quiz me on thermodynamics', 'Debug this code')..."
            }
            className="flex-1 px-4 py-2.5 rounded-lg bg-[#0F1420] border border-neutral-800 text-sm text-white focus:outline-none focus:border-cyan-500 transition-colors placeholder:text-neutral-500 font-sans"
          />
          <button
            type="submit"
            disabled={!input.trim() || isTyping}
            className="p-2.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 disabled:opacity-40 text-black font-bold transition-colors cursor-pointer"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>

      {/* Recent Chats Modal */}
      {showHistoryModal && (
        <div className="absolute inset-0 bg-black/80 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-[#0B0E14] border border-neutral-800 rounded-xl max-w-xl w-full max-h-[500px] flex flex-col overflow-hidden">
            <div className="p-4 border-b border-neutral-800 flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm font-mono font-bold text-white">
                <History className="w-4 h-4 text-purple-400" /> RECENT CHAT SESSIONS
              </div>
              <button
                onClick={() => setShowHistoryModal(false)}
                className="p-1 rounded hover:bg-neutral-800 text-neutral-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-4 overflow-y-auto flex-1 space-y-3 font-mono text-xs">
              {loadingSessions ? (
                <div className="text-center py-8 text-neutral-500">Loading chat history...</div>
              ) : pastSessions.length === 0 ? (
                <div className="text-center py-8 text-neutral-500">No previous chat sessions found.</div>
              ) : (
                pastSessions.map((session, idx) => (
                  <div
                    key={session.id || idx}
                    onClick={() => handleLoadSession(session)}
                    className="p-3.5 rounded-lg bg-[#07090D] border border-neutral-800 hover:border-purple-500/40 cursor-pointer transition-colors space-y-1.5 group"
                  >
                    <div className="flex items-center justify-between text-neutral-400 text-[11px]">
                      <div className="flex items-center gap-2">
                        <span className="text-white font-bold">{session.title || (session.created_at ? new Date(session.created_at).toLocaleString() : `Session ${idx + 1}`)}</span>
                        {session.mode && (
                          <span className={`text-[9px] px-1.5 py-0.5 rounded border ${session.mode === "materials" ? "border-purple-500/40 text-purple-300 bg-purple-950/30" : "border-cyan-500/40 text-cyan-300 bg-cyan-950/30"}`}>
                            {session.mode.toUpperCase()}
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-purple-400">{session.message_count || session.messages?.length || 0} msgs</span>
                        <button
                          onClick={(e) => handleDeleteSession(session.id, e)}
                          title="Delete session"
                          className="text-neutral-500 hover:text-red-400 p-1 rounded transition-colors"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                    <p className="text-neutral-400 text-[11px] line-clamp-2 leading-relaxed">
                      {session.preview || "Study conversation"}
                    </p>
                    <div className="text-[10px] text-neutral-600">
                      {session.updated_at ? new Date(session.updated_at).toLocaleString() : ""}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

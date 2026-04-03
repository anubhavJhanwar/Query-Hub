import { useState, useCallback, useEffect } from "react";
import ChatWindow from "./components/ChatWindow";
import InputBox from "./components/InputBox";
import { sendQuery, ingestDocuments } from "./api";

// Config definitions
const CONFIGS = {
  faiss:  { label: "⚡ Fast",     db: "faiss",  chunkSize: 300, desc: "FAISS · chunk 300" },
  chroma: { label: "🎯 Accurate", db: "chroma", chunkSize: 700, desc: "ChromaDB · chunk 700" },
};

const ACTION_CARDS = [
  { id: "issue",   icon: "🐛", iconBg: "bg-red-500/20 border-red-500/30",    title: "Report an Issue",    subtitle: "Found a bug? Let us know.",    prompt: "I'd like to report an issue." },
  { id: "feature", icon: "💡", iconBg: "bg-yellow-500/20 border-yellow-500/30", title: "Request a Feature", subtitle: "What would you like to see?",  prompt: "I have a feature request." },
  { id: "billing", icon: "💳", iconBg: "bg-green-500/20 border-green-500/30",  title: "Billing Question",  subtitle: "Invoices, plans & payments.",   prompt: "I have a question about billing." },
  { id: "account", icon: "🔐", iconBg: "bg-blue-500/20 border-blue-500/30",    title: "Account Help",      subtitle: "Login, password & settings.",   prompt: "I need help with my account." },
];

const STORAGE_KEY = "rag_chat_history";

export default function App() {
  const [chatMode, setChatMode]   = useState(false);
  const [input, setInput]         = useState("");
  const [loading, setLoading]     = useState(false);
  const [ingestStatus, setIngestStatus] = useState("");
  const [activeConfig, setActiveConfig] = useState("faiss");

  // Load chat history from localStorage
  const [messages, setMessages] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved ? JSON.parse(saved) : [];
    } catch { return []; }
  });

  // Persist messages to localStorage on every change
  useEffect(() => {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(messages)); }
    catch { /* storage full — ignore */ }
  }, [messages]);

  // If there's saved history, go straight to chat mode
  useEffect(() => {
    if (messages.length > 0) setChatMode(true);
  }, []); // eslint-disable-line

  const cfg = CONFIGS[activeConfig];

  const startChat = useCallback((prompt = "") => {
    setChatMode(true);
    if (prompt) setInput(prompt);
  }, []);

  const clearHistory = () => {
    setMessages([]);
    localStorage.removeItem(STORAGE_KEY);
    setChatMode(false);
  };

  const handleSend = useCallback(async (overrideQuery) => {
    const query = (overrideQuery || input).trim();
    if (!query || loading) return;

    setMessages((prev) => [...prev, { role: "user", text: query }]);
    setInput("");
    setLoading(true);

    try {
      const data = await sendQuery(query, cfg.db, cfg.chunkSize);
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          text: data.answer,
          responseTime: data.response_time_ms,
          configUsed: data.config_used,
          llmUsed: data.llm_used,
          sources: data.sources,
          confidences: data.confidences,
          followups: data.followups,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: "Something went wrong. Make sure the backend is running." },
      ]);
    } finally {
      setLoading(false);
    }
  }, [input, loading, cfg]);

  const handleIngest = async () => {
    setIngestStatus(`Ingesting for ${cfg.desc}...`);
    try {
      const data = await ingestDocuments(cfg.db, cfg.chunkSize);
      setIngestStatus(data.message);
    } catch {
      setIngestStatus("Ingestion failed. Check backend.");
    }
    setTimeout(() => setIngestStatus(""), 4000);
  };

  const handleConfigSwitch = (key) => {
    setActiveConfig(key);
    // Clear cached messages when switching config so comparison is clean
    // (optional — comment out if you want to keep history across switches)
  };

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 flex items-center justify-center p-4">

      {/* Ambient blobs */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -left-40 w-96 h-96 bg-indigo-400/20 rounded-full blur-3xl" />
        <div className="absolute -bottom-40 -right-40 w-96 h-96 bg-pink-400/20 rounded-full blur-3xl" />
      </div>

      {/* Main card */}
      <div
        className="relative w-full max-w-md bg-white/10 backdrop-blur-xl border border-white/20 rounded-3xl shadow-2xl shadow-black/30 flex flex-col overflow-hidden animate-fade-in"
        style={{ height: chatMode ? "640px" : "auto" }}
      >
        {/* ── HEADER ── */}
        <div className="flex items-center justify-between px-5 pt-5 pb-3 flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-2xl bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-500/30 text-base">
              🤖
            </div>
            <div>
              <h1 className="text-white font-semibold text-sm leading-tight">Query Hub</h1>
              <div className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 bg-green-400 rounded-full" />
                <span className="text-white/45 text-[11px]">Online · RAG powered</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-1.5">
            {/* Config switcher pills */}
            <div className="flex items-center bg-black/25 border border-white/10 rounded-full p-0.5 gap-0.5">
              {Object.entries(CONFIGS).map(([key, c]) => (
                <button
                  key={key}
                  onClick={() => handleConfigSwitch(key)}
                  className={`text-[10px] px-2.5 py-1 rounded-full transition-all font-medium whitespace-nowrap ${
                    activeConfig === key
                      ? "bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-sm"
                      : "text-white/40 hover:text-white/70"
                  }`}
                >
                  {c.label}
                </button>
              ))}
            </div>

            {/* Load KB */}
            <button onClick={handleIngest} title="Load Knowledge Base"
              className="w-7 h-7 flex items-center justify-center rounded-xl bg-white/10 hover:bg-white/20 border border-white/15 transition-all hover:scale-105 active:scale-95">
              <svg className="w-3 h-3 text-white/70" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/>
              </svg>
            </button>

            {/* Clear history */}
            {messages.length > 0 && (
              <button onClick={clearHistory} title="Clear chat history"
                className="w-7 h-7 flex items-center justify-center rounded-xl bg-white/10 hover:bg-red-500/30 border border-white/15 transition-all hover:scale-105 active:scale-95">
                <svg className="w-3 h-3 text-white/70" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                </svg>
              </button>
            )}

            {/* Back to home */}
            {chatMode && (
              <button onClick={() => setChatMode(false)} title="Home"
                className="w-7 h-7 flex items-center justify-center rounded-xl bg-white/10 hover:bg-white/20 border border-white/15 transition-all hover:scale-105 active:scale-95">
                <svg className="w-3 h-3 text-white/70" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
                </svg>
              </button>
            )}
          </div>
        </div>

        {/* Active config hint */}
        <div className="px-5 pb-2 flex-shrink-0">
          <p className="text-[10px] text-white/25">
            Active: {cfg.desc} · Load KB after switching config
          </p>
        </div>

        {/* Ingest toast */}
        {ingestStatus && (
          <div className="mx-5 mb-2 px-3 py-2 bg-green-500/20 border border-green-400/30 rounded-xl text-green-300 text-xs text-center animate-fade-in flex-shrink-0">
            {ingestStatus}
          </div>
        )}

        {/* ── HERO MODE ── */}
        {!chatMode && (
          <div className="px-5 pb-6 animate-slide-up">
            <div className="mb-5">
              <h2 className="text-3xl font-bold text-white leading-tight">Hi there 👋</h2>
              <p className="text-white/55 mt-1 text-sm">How can we help you today?</p>
            </div>

            <div className="grid grid-cols-2 gap-2.5 mb-4">
              {ACTION_CARDS.map((card) => (
                <button key={card.id} onClick={() => startChat(card.prompt)}
                  className="text-left bg-white/10 hover:bg-white/15 border border-white/15 rounded-2xl p-3.5 transition-all hover:scale-105 active:scale-95">
                  <div className={`w-7 h-7 rounded-xl border flex items-center justify-center text-sm mb-2.5 ${card.iconBg}`}>
                    {card.icon}
                  </div>
                  <p className="text-white text-xs font-medium leading-tight">{card.title}</p>
                  <p className="text-white/35 text-[11px] mt-0.5 leading-tight">{card.subtitle}</p>
                </button>
              ))}
            </div>

            <div onClick={() => startChat()}
              className="flex items-center gap-3 bg-black/30 border border-white/15 rounded-full px-4 py-2.5 cursor-text hover:border-indigo-400/50 transition-all">
              <svg className="w-3.5 h-3.5 text-white/30 flex-shrink-0" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
              </svg>
              <span className="text-white/30 text-sm">Search or ask anything...</span>
            </div>

            {/* Saved history indicator */}
            {messages.length > 0 && (
              <button onClick={() => setChatMode(true)}
                className="mt-3 w-full text-center text-[11px] text-white/35 hover:text-white/60 transition-colors">
                ↩ Resume previous conversation ({messages.length} messages)
              </button>
            )}
          </div>
        )}

        {/* ── CHAT MODE ── */}
        {chatMode && (
          <>
            <ChatWindow messages={messages} loading={loading} onFollowup={(q) => handleSend(q)} />
            <div className="px-4 pb-4 pt-2 flex-shrink-0">
              <InputBox value={input} onChange={setInput} onSend={() => handleSend()} loading={loading} />
              <p className="text-center text-white/20 text-[10px] mt-1.5">
                Answers grounded in knowledge base · {cfg.desc}
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

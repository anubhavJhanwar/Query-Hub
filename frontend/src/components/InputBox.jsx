import { useRef, useEffect } from "react";

export default function InputBox({ value, onChange, onSend, loading }) {
  const ref = useRef(null);

  useEffect(() => { ref.current?.focus(); }, []);

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); onSend(); }
  };

  return (
    <div className="flex items-center gap-2 bg-slate-700/50 border border-slate-600/40 rounded-full px-4 py-2.5 focus-within:border-teal-400/60 focus-within:shadow-lg focus-within:shadow-teal-500/10 transition-all">
      <input
        ref={ref}
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKey}
        placeholder="Ask a question..."
        disabled={loading}
        className="flex-1 bg-transparent text-sm text-white placeholder-white/30 outline-none disabled:opacity-50"
      />
      <button
        onClick={onSend}
        disabled={loading || !value.trim()}
        className="w-8 h-8 flex items-center justify-center rounded-full bg-gradient-to-br from-teal-500 to-teal-600 disabled:opacity-30 hover:scale-110 active:scale-95 transition-transform shadow-md shadow-teal-500/30"
      >
        {loading ? (
          <svg className="w-3.5 h-3.5 animate-spin text-white" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
          </svg>
        ) : (
          <svg className="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5"/>
          </svg>
        )}
      </button>
    </div>
  );
}

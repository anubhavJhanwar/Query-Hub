import SourceViewer from "./SourceViewer";

export default function MessageBubble({ role, text, responseTime, configUsed, llmUsed, sources, confidences, followups, onFollowup }) {
  const isUser = role === "user";
  const topConf = confidences?.[0];

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} animate-slide-up`}>
      <div className={`max-w-[82%] flex flex-col gap-1 ${isUser ? "items-end" : "items-start"}`}>

        {/* Bubble */}
        <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap ${
          isUser
            ? "bg-gradient-to-br from-teal-500 to-teal-700 text-white rounded-br-sm shadow-lg shadow-teal-500/20"
            : "bg-slate-700/60 backdrop-blur-sm border border-slate-600/40 text-slate-100 rounded-bl-sm"
        }`}>
          {text}
        </div>

        {/* Meta row — bot only */}
        {!isUser && responseTime && (
          <div className="flex items-center gap-2 px-1 flex-wrap">
            <span className="text-[10px] text-white/30">
              ⚡ {responseTime}ms · {configUsed} · {llmUsed}
            </span>
            {/* Confidence badge for top result */}
            {topConf !== undefined && (
              <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded-full border ${
                topConf >= 70
                  ? "text-green-400 border-green-400/30 bg-green-400/10"
                  : topConf >= 40
                  ? "text-yellow-400 border-yellow-400/30 bg-yellow-400/10"
                  : "text-red-400 border-red-400/30 bg-red-400/10"
              }`}>
                {topConf}% confidence
              </span>
            )}
          </div>
        )}

        {/* Sources */}
        {!isUser && <SourceViewer sources={sources} confidences={confidences} />}

        {/* Follow-up suggestions */}
        {!isUser && followups && followups.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-1 px-1">
            {followups.map((q, i) => (
              <button
                key={i}
                onClick={() => onFollowup?.(q)}
                className="text-[11px] text-white/60 bg-white/8 hover:bg-white/15 border border-white/15 rounded-full px-3 py-1 transition-all hover:text-white hover:scale-105 active:scale-95 text-left"
              >
                {q}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

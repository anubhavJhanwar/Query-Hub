import { useState } from "react";

export default function SourceViewer({ sources, confidences }) {
  const [open, setOpen] = useState(false);
  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-1.5">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1 text-[11px] text-white/40 hover:text-white/70 transition-colors"
      >
        <span>{open ? "▾" : "▸"}</span>
        <span>View Sources ({sources.length})</span>
      </button>

      {open && (
        <div className="mt-2 space-y-2 animate-fade-in">
          {sources.map((src, i) => {
            const conf = confidences?.[i];
            const color = conf >= 70 ? "text-green-400" : conf >= 40 ? "text-yellow-400" : "text-red-400";
            return (
              <div key={i} className="text-xs bg-slate-700/50 border border-slate-600/40 rounded-xl p-3">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-white/30 font-mono">Source {i + 1}</span>
                  {conf !== undefined && (
                    <span className={`font-semibold text-[11px] ${color}`}>
                      {conf}% match
                    </span>
                  )}
                </div>
                <p className="text-white/55 leading-relaxed">{src}</p>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

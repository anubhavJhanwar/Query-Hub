import { useRef, useEffect } from "react";
import MessageBubble from "./MessageBubble";

export default function ChatWindow({ messages, loading, onFollowup }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  return (
    <div className="flex-1 overflow-y-auto px-3 py-4 space-y-4 min-h-0">
      {messages.map((msg, i) => (
        <MessageBubble key={i} {...msg} onFollowup={onFollowup} />
      ))}

      {loading && (
        <div className="flex justify-start animate-fade-in">
          <div className="bg-white/10 backdrop-blur-sm border border-white/15 rounded-2xl rounded-bl-sm px-4 py-3">
            <div className="flex items-center gap-1.5">
              <span className="text-xs text-white/40 mr-1">Thinking</span>
              {[0, 1, 2].map((i) => (
                <span
                  key={i}
                  className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce-dot"
                  style={{ animationDelay: `${i * 0.15}s` }}
                />
              ))}
            </div>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}

import { useEffect, useRef } from "react";
import Message, { Typing } from "./Message";
import Welcome from "./Welcome";

export default function MessageList({ messages, pending, debug, onPick, onRetry }) {
  const endRef = useRef(null);
  useEffect(() => {
    endRef.current?.scrollIntoView({ block: "end" });
  }, [messages.length, pending]);

  return (
    <main className="log" aria-live="polite">
      {messages.length === 0 && !pending ? (
        <Welcome onPick={onPick} />
      ) : (
        messages.map((m) => <Message key={m.id} m={m} debug={debug} onRetry={onRetry} />)
      )}
      {pending && <Typing />}
      <div ref={endRef} />
    </main>
  );
}

import { Bowl, Refresh } from "./Icons";

const fmt = (t) => new Date(t).toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" });

export default function Message({ m, debug, onRetry }) {
  const isUser = m.role === "user";
  const meta = fmt(m.time) + (debug && m.intent ? ` · ${m.intent} (${m.confidence})` : "");
  return (
    <div className={"row " + (isUser ? "user" : "bot") + (m.error ? " error" : "")}>
      {!isUser && (
        <div className="avatar">
          <Bowl />
        </div>
      )}
      <div className="msg">
        <div className="bubble">{m.text}</div>
        <div className="meta">
          {meta}
          {m.error && (
            <button type="button" className="retry" onClick={() => onRetry(m.id)}>
              <Refresh /> Thử lại
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export function Typing() {
  return (
    <div className="row bot typing" aria-label="Trợ lý đang soạn câu trả lời">
      <div className="avatar">
        <Bowl />
      </div>
      <div className="msg">
        <div className="bubble">
          <i />
          <i />
          <i />
        </div>
      </div>
    </div>
  );
}

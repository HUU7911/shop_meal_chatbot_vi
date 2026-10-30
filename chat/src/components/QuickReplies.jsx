import { SUGGESTIONS } from "../config";

export default function QuickReplies({ onPick, disabled }) {
  return (
    <div className="quick">
      {SUGGESTIONS.map((s) => (
        <button key={s} type="button" className="chip" disabled={disabled} onClick={() => onPick(s)}>
          {s}
        </button>
      ))}
    </div>
  );
}

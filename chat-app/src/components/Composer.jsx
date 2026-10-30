import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { Send } from "./Icons";

const MAX_H = 130;

export default function Composer({ onSend, pending }) {
  const [value, setValue] = useState("");
  const ref = useRef(null);

  useLayoutEffect(() => {
    const el = ref.current;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, MAX_H) + "px";
    el.style.overflowY = el.scrollHeight > MAX_H ? "auto" : "hidden";
  }, [value]);

  useEffect(() => {
    if (!pending) ref.current?.focus();
  }, [pending]);

  const submit = () => {
    if (!value.trim() || pending) return;
    onSend(value);
    setValue("");
  };

  return (
    <form
      className="composer"
      autoComplete="off"
      onSubmit={(e) => {
        e.preventDefault();
        submit();
      }}
    >
      <textarea
        ref={ref}
        rows={1}
        maxLength={2000}
        value={value}
        placeholder="Nhập câu hỏi, ví dụ: đơn hàng của tôi đang ở đâu"
        aria-label="Tin nhắn"
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
            e.preventDefault();
            submit();
          }
        }}
      />
      <button className="send" type="submit" aria-label="Gửi tin nhắn" disabled={pending || !value.trim()}>
        <Send />
      </button>
    </form>
  );
}

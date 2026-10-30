import { useCallback, useEffect, useRef, useState } from "react";
import { sendMessage, checkHealth } from "../api";
import { STORE_KEY, MAX_STORED } from "../config";

const uid = () => Date.now().toString(36) + Math.random().toString(36).slice(2, 7);

function loadHistory() {
  try {
    const d = JSON.parse(localStorage.getItem(STORE_KEY) || "[]");
    return Array.isArray(d) ? d : [];
  } catch {
    return [];
  }
}

export function useChat() {
  const [messages, setMessages] = useState(loadHistory);
  const [pending, setPending] = useState(false);
  const [status, setStatus] = useState("checking"); // checking | online | offline
  const busy = useRef(false);

  useEffect(() => {
    try {
      localStorage.setItem(STORE_KEY, JSON.stringify(messages.slice(-MAX_STORED)));
    } catch {}
  }, [messages]);

  useEffect(() => {
    checkHealth().then((ok) => setStatus(ok ? "online" : "offline"));
  }, []);

  const send = useCallback(async (raw, { resend = false } = {}) => {
    const text = (raw || "").trim();
    if (!text || busy.current) return;
    busy.current = true;
    setPending(true);
    if (!resend) {
      setMessages((m) => [...m, { id: uid(), role: "user", text, time: Date.now() }]);
    }
    try {
      const { reply, intent, confidence } = await sendMessage(text);
      setMessages((m) => [...m, { id: uid(), role: "bot", text: reply, time: Date.now(), intent, confidence }]);
      setStatus("online");
    } catch (err) {
      setMessages((m) => [
        ...m,
        {
          id: uid(),
          role: "bot",
          error: true,
          retryText: text,
          time: Date.now(),
          text: `Không kết nối được tới máy chủ (${err.message}). Hãy kiểm tra api.py đã chạy chưa, rồi thử lại.`,
        },
      ]);
      setStatus("offline");
    } finally {
      busy.current = false;
      setPending(false);
    }
  }, []);

  const retry = useCallback(
    (id) => {
      const target = messages.find((m) => m.id === id);
      if (!target?.retryText) return;
      setMessages((m) => m.filter((x) => x.id !== id));
      send(target.retryText, { resend: true });
    },
    [messages, send]
  );

  const clear = useCallback(() => setMessages([]), []);

  return { messages, pending, status, send, retry, clear };
}

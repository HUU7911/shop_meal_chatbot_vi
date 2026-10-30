import { useMemo } from "react";
import Header from "./components/Header";
import MessageList from "./components/MessageList";
import Composer from "./components/Composer";
import { useChat } from "./hooks/useChat";
import { useTheme } from "./hooks/useTheme";

export default function App() {
  const { messages, pending, status, send, retry, clear } = useChat();
  const { theme, toggle } = useTheme();
  // Thêm ?debug vào địa chỉ trang để xem intent và độ tin cậy của từng câu trả lời.
  const debug = useMemo(() => new URLSearchParams(location.search).has("debug"), []);

  return (
    <div className="app">
      <Header status={status} theme={theme} onToggleTheme={toggle} onClear={clear} canClear={messages.length > 0} />
      <MessageList messages={messages} pending={pending} debug={debug} onRetry={retry} />
      <Composer onSend={send} pending={pending} />
      <p className="foot">Enter để gửi, Shift + Enter để xuống dòng.</p>
    </div>
  );
}
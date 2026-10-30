import { Bowl, Moon, Sun, Trash } from "./Icons";

const STATUS_TEXT = {
  checking: "Đang kiểm tra kết nối…",
  online: "Đang trực tuyến",
  offline: "Chưa kết nối máy chủ",
};

export default function Header({ status, theme, onToggleTheme, onClear, canClear }) {
  const handleClear = () => {
    if (canClear && !window.confirm("Xóa toàn bộ cuộc trò chuyện này?")) return;
    onClear();
  };
  return (
    <header className="header">
      <div className="logo" aria-hidden="true">
        <Bowl />
      </div>
      <div className="title">
        <h1>Shop Meal</h1>
        <div className={"status " + status} role="status">
          <span className="dot" />
          <span>{STATUS_TEXT[status]}</span>
        </div>
      </div>
      <button
        type="button"
        className="icon-btn"
        onClick={onToggleTheme}
        aria-label={theme === "dark" ? "Chuyển sang giao diện sáng" : "Chuyển sang giao diện tối"}
        title={theme === "dark" ? "Giao diện sáng" : "Giao diện tối"}
      >
        {theme === "dark" ? <Sun /> : <Moon />}
      </button>
      <button type="button" className="icon-btn with-text" onClick={handleClear}>
        <Trash />
        <span>Xóa cuộc trò chuyện</span>
      </button>
    </header>
  );
}

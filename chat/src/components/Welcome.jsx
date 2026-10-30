import { SUGGESTIONS } from "../config";
import { Bowl } from "./Icons";

// Danh sách gợi ý trình bày như một tờ thực đơn: tên món, đường chấm, nút chọn.
export default function Welcome({ onPick }) {
  return (
    <section className="welcome">
      <div className="logo big" aria-hidden="true">
        <Bowl />
      </div>
      <h2>Hôm nay bạn muốn ăn gì?</h2>
      <p>Mình là trợ lý Shop Meal: xem thực đơn, theo dõi đơn hàng, đặt bàn và giải đáp thắc mắc.</p>
      <ul className="menu-board">
        {SUGGESTIONS.map((s) => (
          <li key={s}>
            <button type="button" onClick={() => onPick(s)}>
              <span className="menu-name">{s}</span>
              <span className="leader" aria-hidden="true" />
              <span className="menu-go">Hỏi</span>
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}

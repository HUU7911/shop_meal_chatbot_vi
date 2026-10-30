import { Bowl } from "./Icons";

export default function Welcome() {
  return (
    <section className="welcome">
      <div className="welcome-badge" aria-hidden="true">
        <Bowl />
      </div>
      <h2>Hôm nay bạn muốn ăn gì?</h2>
      <p>
        Mình là trợ lý Shop Meal. Cứ hỏi về thực đơn, đơn hàng, đặt bàn hay thanh toán, mình sẽ trả lời ngay.
      </p>
    </section>
  );
}
# Shop Meal – giao diện chatbot (Vite + React)

## Chạy thử
```bash
npm install
npm run dev
```
Mở địa chỉ Vite in ra (thường là http://localhost:5173).

## Kết nối với api.py
- Khi chạy `npm run dev`, `/chat` và `/health` được chuyển tiếp tới `http://127.0.0.1:8000`.
- Nếu api.py chạy cổng khác, tạo file `.env`:
  ```
  VITE_BACKEND=http://127.0.0.1:5000
  ```
- Tên trường gửi/nhận nằm trong `src/config.js` (`REQUEST_FIELD`, `REPLY_FIELDS`).
- Thêm `?debug` vào địa chỉ trang để xem intent và độ tin cậy.

## Đưa vào api.py
```bash
npm run build
```
Thư mục `dist/` là bản tĩnh; cho api.py phục vụ thư mục này (ví dụ FastAPI: `app.mount("/", StaticFiles(directory="dist", html=True), name="web")`, đặt sau các route `/chat` và `/health`).

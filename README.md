# Shop Meal Vietnamese Chatbot (Bitext + TF-IDF + Logistic Regression)

## 1. Yêu cầu
- Python 3.10+
- Kết nối Internet ở lần tải dataset và dịch mẫu
- Không cần GPU

## 2. Cài đặt trên Linux
```bash
cd shop_meal_chatbot_vi
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Nếu Linux báo thiếu `venv`, cài gói `python3-venv` bằng trình quản lý gói của hệ điều hành.

## 3. Chuẩn bị dữ liệu tiếng Việt
```bash
python prepare_data.py
```
Script tải CSV gốc từ Hugging Face, lấy tối đa 30 câu cho mỗi intent, dịch trường `instruction` sang tiếng Việt và thêm một số câu mẫu Shop Meal. Bản dịch được lưu cache trong `data/translation_cache.csv` để lần chạy sau không phải dịch lại các câu đã có.

Mặc định giới hạn 30 câu/intent để thử nghiệm. Khi pipeline chạy ổn, tăng `SAMPLES_PER_INTENT` trong `prepare_data.py`. Dịch tự động có thể sai hoặc bị giới hạn tốc độ; hãy rà soát `data/train_vi.csv` trước khi huấn luyện.

## 4. Huấn luyện và đánh giá
```bash
python train.py
```
Mô hình được lưu tại `models/shop_meal_intent_model.joblib`. Báo cáo đánh giá được lưu tại `models/evaluation.json`.

## 5. Chat trên terminal
```bash
python chat.py
```

## 6. Chạy REST API
```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

```bash
uvicorn api:app --reload
```
- Kiểm tra: http://localhost:8000/health
- Swagger UI: http://localhost:8000/docs
- POST `/chat` với JSON:
```json
{"message":"Tôi muốn kiểm tra đơn hàng"}
```

Ví dụ phản hồi:
```json
{
  "reply": "Bạn hãy mở mục đơn hàng trong tài khoản Shop Meal để xem trạng thái cập nhật...",
  "intent": "track_order",
  "confidence": 0.82
}
```
Confidence chỉ là điểm tin cậy tương đối của mô hình, không phải xác suất được hiệu chuẩn hay cam kết câu trả lời đúng.

## 7. Tích hợp frontend React
```javascript
const response = await fetch("http://localhost:8000/chat", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ message: inputMessage })
});
const data = await response.json();
console.log(data.reply);
```
Trong môi trường production, cấu hình CORS, xác thực, giới hạn tốc độ và URL qua biến môi trường. Có thể đặt API Python sau API Gateway hoặc để Spring Boot gọi dịch vụ Python.

## 8. Giới hạn và lưu ý
- Dataset gốc là tiếng Anh; script dịch mẫu sang tiếng Việt. Chất lượng mô hình phụ thuộc mạnh vào chất lượng bản dịch và ví dụ tiếng Việt bổ sung.
- Mô hình này phân loại ý định, không tự truy vấn trạng thái đơn hàng hoặc dữ liệu thực của Shop Meal. Muốn trả lời dữ liệu thật, cần nối từng intent như `track_order`, `check_menu` với API nghiệp vụ và xác thực người dùng.
- `response` được dùng như câu trả lời mẫu theo intent, không phải câu trả lời đã được học sinh sinh ra từ mô hình.
- Dataset Bitext dùng giấy phép CDLA-Sharing 1.0; nếu phân phối bộ dữ liệu phái sinh, hãy đọc và tuân thủ điều khoản giấy phép, ghi nhận nguồn và nghĩa vụ chia sẻ tương ứng.

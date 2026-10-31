# BÁO CÁO KỸ THUẬT: PHÂN LOẠI Ý ĐỊNH VĂN BẢN VỚI FINE-TUNING PHOBERT

---

## 1. Tổng quan phương pháp (Overview)
Phương pháp áp dụng kỹ thuật **Học chuyển giao (Transfer Learning)** bằng cách tinh chỉnh (**Fine-tuning**) mô hình ngôn ngữ lớn chuyên biệt cho tiếng Việt - **PhoBERT** (`vinai/phobert-base-v2`). Mô hình này dựa trên kiến trúc **RoBERTa (Robustly Optimized BERT Approach)** với cơ chế Transformer Attention hai chiều, cho phép mô hình nắm bắt sâu sắc ngữ cảnh, cấu trúc cú pháp và ngữ nghĩa phong phú của tiếng Việt trong bài toán phân loại ý định (Intent Classification).

---

## 2. Cơ sở lý thuyết và cấu trúc mô hình

### 2.1. Mã hóa văn bản với Byte-Pair Encoding (BPE)
PhoBERT sử dụng bộ tách từ con (subword segmentation) dựa trên BPE:
* Mỗi văn bản được thêm 2 token đặc biệt: `<s>` (Token bắt đầu chuỗi, đại diện ngữ cảnh toàn câu) và `</s>` (Token phân tách/kết thúc chuỗi).
* Đầu vào của mô hình được biểu diễn dưới dạng tổng của 3 vector embedding:
  $$\mathbf{E} = \mathbf{E}_{\text{token}} + \mathbf{E}_{\text{position}} + \mathbf{E}_{\text{segment}}$$

### 2.2. Cơ chế Self-Attention đa đầu (Multi-Head Self-Attention)
Trọng tâm của Transformer là cơ chế tính toán độ liên quan giữa mọi cặp từ trong câu thông qua bộ ba vector Query ($Q$), Key ($K$), Value ($V$):

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{Q K^T}{\sqrt{d_k}}\right) V$$

Cơ chế Multi-Head mở rộng cho phép mô hình nắm bắt đồng thời nhiều mối quan hệ ngữ nghĩa ở các không gian biểu diễn khác nhau:
$$\text{MultiHead}(Q, K, V) = \text{Concat}(\text{head}_1, \dots, \text{head}_h)\mathbf{W}^O$$
Trong đó mỗi head được tính bằng:
$$\text{head}_i = \text{Attention}(Q\mathbf{W}_i^Q, K\mathbf{W}_i^K, V\mathbf{W}_i^V)$$

### 2.3. Đầu phân loại (Sequence Classification Head)
Sau khi đi qua 12 khối Transformer Encoder, vector trạng thái ẩn tại vị trí token `<s>` đại diện cho toàn bộ câu ($\mathbf{h}_{\text{<s>}} \in \mathbb{R}^{768}$) được đưa qua tầng phân loại:

1. **Lớp chiếu phi tuyến tính và Dropout:**
   $$\mathbf{z} = \tanh(\mathbf{W}_d \cdot \mathbf{h}_{\text{<s>}} + \mathbf{b}_d)$$
   $$\mathbf{z}_{\text{drop}} = \text{Dropout}(\mathbf{z}, p=0.1)$$

2. **Lớp tuyến tính chiếu ra số lượng nhãn intent ($K$):**
   $$\mathbf{l} = \mathbf{W}_c \cdot \mathbf{z}_{\text{drop}} + \mathbf{b}_c \quad (\mathbf{l} \in \mathbb{R}^K)$$

3. **Tính toán phân phối xác suất qua Softmax:**
   $$P(\text{intent} = k \mid \text{câu}) = \frac{\exp(l_k)}{\sum_{j=1}^K \exp(l_j)}$$

### 2.4. Hàm mất mát và Tối ưu hóa (Optimization)
Mô hình được huấn luyện bằng hàm mất mát **Cross-Entropy**:
$$\mathcal{L}_{CE} = - \sum_{k=1}^K y_k \log P(\text{intent} = k)$$

Thuật toán tối ưu hóa được sử dụng là **AdamW** (Adam with Decoupled Weight Decay) kết hợp với kỹ thuật điều chỉnh tốc độ học tuyến tính (Linear Learning Rate Warmup & Decay), giúp cập nhật nhẹ các trọng số pre-trained mà không làm phá vỡ các đặc trưng ngôn ngữ tự nhiên đã học trước đó.

---

## 3. Kiến trúc huấn luyện và cấu hình tham số

```
[Văn bản đầu vào (Raw Text)]
            │
            ▼
[PhoBERT Tokenizer (BPE)] -> Padding/Truncation (max_length=128)
            │
            ▼
[Input IDs, Attention Mask]
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│  PhoBERT Base v2 Backbone (12 Layers, 768 Hidden, 12 Heads) │
│  - Pre-trained trên ngữ liệu tiếng Việt lớn                 │
│  - Cập nhật trọng số thông qua Backpropagation              │
└─────────────────────────────────────────────────────────────┘
            │
            ▼ (Vector ẩn của token <s>: 768 chiều)
[Dropout (0.1) -> Dense Layer (Tanh) -> Linear Layer (num_labels)]
            │
            ▼
[Logits] ──► [Softmax] ──► [Dự đoán Intent + Độ tự tin (Confidence)]
```

### Bảng tham số huấn luyện đề xuất:
* **Base Model:** `vinai/phobert-base-v2` (khoảng 135 triệu tham số).
* **Learning Rate:** $2 \times 10^{-5}$ (tốc độ học nhỏ để tránh hiện tượng Catastrophic Forgetting).
* **Batch Size:** $16$ hoặc $32$.
* **Epochs:** $3 - 5$ epochs.
* **Warmup Ratio:** $0.1$.
* **Đánh giá kiểm thử:** Đánh giá định kỳ theo epoch bằng chỉ số **Accuracy** và **Macro-F1**.

---

## 4. Đánh giá ưu điểm và nhược điểm

### 4.1. Ưu điểm
1. **Khả năng hiểu ngữ nghĩa và ngữ cảnh vượt trội:** Nhờ cơ chế Bidirectional Self-Attention, mô hình phân biệt rạch ròi các cấu trúc phủ định, câu điều kiện hoặc ngữ cảnh đối lập (ví dụ phân biệt giữa *"đặt bàn"* và *"hủy đặt bàn"*).
2. **Khả năng khái quát hóa cao:** Nhờ vốn từ vựng và ngữ cảnh đã học từ trước, mô hình xử lý rất tốt các câu sử dụng từ đồng nghĩa, khẩu ngữ hoặc cách đặt câu chưa từng xuất hiện trong tập huấn luyện.
3. **Độ tự tin (Confidence Score) sắc nét:** Phân phối xác suất Softmax phân tách rõ ràng, giúp thiết lập ngưỡng tin cậy để nhận diện các câu nằm ngoài phạm vi nghiệp vụ (Out-of-Scope / Fallback).

### 4.2. Nhược điểm
1. **Đòi hỏi năng lực tính toán cao:** Việc huấn luyện và suy luận đòi hỏi GPU chuyên dụng. Nếu chạy huấn luyện trên CPU, thời gian có thể kéo dài hàng giờ với tập dữ liệu lớn.
2. **Kích thước mô hình và mức tiêu thụ RAM:** File trọng số mô hình nặng khoảng $540\text{MB}$, khi chạy trên RAM/VRAM cần tối thiểu $500\text{MB} - 1\text{GB}$ bộ nhớ thường trực.
3. **Độ trễ suy luận cao hơn:** Thời gian phản hồi cho mỗi truy vấn khoảng $15 - 40\text{ms}$ (GPU) hoặc $50 - 150\text{ms}$ (CPU), cao hơn đáng kể so với phương pháp tuyến tính truyền thống.

---

## 5. Kết luận
Fine-tuning PhoBERT là giải pháp chuẩn công nghiệp hiện nay cho các hệ thống chatbot và trợ lý ảo thông minh yêu cầu chất lượng hiểu tiếng Việt sâu sắc, độ chính xác phân loại cao và khả năng xử lý linh hoạt các tình huống giao tiếp tự nhiên phức tạp.
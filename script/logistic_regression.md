# BÁO CÁO KỸ THUẬT: PHÂN LOẠI Ý ĐỊNH VĂN BẢN VỚI TF-IDF VÀ LOGISTIC REGRESSION

---

## 1. Tổng quan phương pháp (Overview)
Phương pháp tiếp cận dựa trên **TF-IDF (Term Frequency - Inverse Document Frequency)** kết hợp với **Hồi quy Logistic (Logistic Regression)** là giải pháp truyền thống (classical machine learning pipeline) trong xử lý ngôn ngữ tự nhiên (NLP). Phương pháp này tiếp cận bài toán phân loại ý định người dùng (Intent Classification) theo mô hình túi từ/túi ký tự (Bag of Words / Bag of Character n-grams), chuyển đổi chuỗi văn bản phi cấu trúc thành các vector đặc trưng tĩnh trước khi phân loại tuyến tính.

---

## 2. Cơ sở lý thuyết và công thức toán học

### 2.1. Vector hóa đặc trưng: TF-IDF ở cấp độ cụm ký tự (Character n-grams)
Thay vì tách từ theo từ điển, mô hình sử dụng `analyzer="char_wb"` với dải n-gram từ $2$ đến $5$ ký tự nằm trong ranh giới từ.

1. **Tần suất n-gram ($TF$ - Term Frequency):**
   $$TF(t, d) = 1 + \log(f_{t, d}) \quad \text{với } f_{t, d} > 0 \quad (\text{Sublinear TF})$$
   Trong đó $f_{t, d}$ là số lần n-gram ký tự $t$ xuất hiện trong văn bản $d$. Việc dùng hàm $\log$ giúp hạn chế ảnh hưởng áp đảo của các từ lặp lại nhiều lần.

2. **Tần số nghịch đảo ($IDF$ - Inverse Document Frequency):**
   $$IDF(t, D) = \log\left(\frac{1 + |D|}{1 + |\{d \in D : t \in d\}|}\right) + 1$$
   Trong đó $|D|$ là tổng số câu trong tập huấn luyện, mẫu số thể hiện số lượng câu có chứa n-gram $t$. Công thức này gán trọng số thấp cho các cụm ký tự xuất hiện phổ biến ở mọi câu và gán trọng số cao cho các cụm ký tự đặc trưng.

3. **Trọng số TF-IDF tổng hợp và chuẩn hóa:**
   $$\text{TF-IDF}(t, d, D) = TF(t, d) \times IDF(t, D)$$
   Mỗi văn bản $d$ được biểu diễn thành một vector thưa $\mathbf{x} \in \mathbb{R}^{V}$ ($V$ là kích thước từ vựng), sau đó được chuẩn hóa theo chuẩn $L_2$:
   $$\mathbf{x}_{\text{norm}} = \frac{\mathbf{x}}{\|\mathbf{x}\|_2}$$

### 2.2. Bộ phân loại: Hồi quy Logistic Đa lớp (Multinomial Logistic Regression)
Với tập nhãn gồm $K$ intent ($K \ge 2$), bài toán sử dụng mô hình Softmax Regression. Xác suất câu có vector đặc trưng $\mathbf{x}$ thuộc về nhãn thứ $k$ được tính bằng:

$$P(y = k \mid \mathbf{x}) = \frac{\exp(\mathbf{w}_k^T \mathbf{x} + b_k)}{\sum_{j=1}^K \exp(\mathbf{w}_j^T \mathbf{x} + b_j)}$$

Trong đó $\mathbf{w}_k$ và $b_k$ lần lượt là trọng số và hệ số điều chỉnh của nhãn $k$.

**Hàm tối ưu hóa (Loss function với điều hòa $L_2$ và trọng số lớp balanced):**
$$\mathcal{L}(\mathbf{W}, \mathbf{b}) = - \sum_{i=1}^N \sum_{k=1}^K w_k \cdot \mathbb{I}(y_i = k) \log P(y_i = k \mid \mathbf{x}_i) + \frac{1}{2C} \sum_{k=1}^K \|\mathbf{w}_k\|_2^2$$

Trong đó:
* $w_k$: Hệ số phạt cân bằng mẫu (Class Weight), tính theo $w_k = \frac{N}{K \cdot N_k}$ ($N_k$ là số mẫu của lớp $k$).
* $C$: Hệ số nghịch đảo của cường độ điều hòa (Regularization strength).

---

## 3. Kiến trúc Pipeline triển khai

```
[Văn bản đầu vào (Raw Text)]
            │
            ▼
[TfidfVectorizer (char_wb, n-gram 2-5)]
    - Tách n-gram ký tự trong từ
    - Lọc tần suất: min_df=2, max_features=40,000
    - Biến đổi Sublinear TF & chuẩn hóa L2
            │
            ▼
[Vector thưa kích thước cố định (Sparse Vector)]
            │
            ▼
[LogisticRegression]
    - max_iter=2000, C=2.0
    - class_weight='balanced'
    - Tối ưu hóa bằng thuật toán L-BFGS
            │
            ▼
[Dự đoán Intent & Điểm xác suất Softmax]
```

---

## 4. Đánh giá ưu điểm và nhược điểm

### 4.1. Ưu điểm
1. **Tốc độ huấn luyện và suy luận cực nhanh:** Thời gian huấn luyện trên tập dữ liệu hàng chục nghìn câu chỉ mất vài giây đến nửa phút trên CPU thông thường. Độ trễ suy luận $< 2\text{ms}$ mỗi câu.
2. **Chi phí tài nguyên thấp:** Kích thước mô hình đã nén (`joblib`) chỉ khoảng vài megabyte, tiêu tốn rất ít bộ nhớ RAM ($< 100\text{MB}$), phù hợp triển khai trên các máy chủ cấu hình yếu hoặc thiết bị nhúng.
3. **Chống chịu lỗi chính tả tốt:** Nhờ sử dụng `char_wb` (character n-grams), mô hình không bị sụp đổ khi gặp lỗi gõ dấu nhẹ hoặc biến thể từ chưa từng xuất hiện trong từ điển.

### 4.2. Nhược điểm
1. **Mất ngữ cảnh thứ tự từ:** Mô hình dựa trên giả thuyết túi từ (Bag of Words/N-grams), không phân biệt được trật tự cú pháp phức tạp trong câu.
2. **Không hiểu được ngữ nghĩa sâu và câu phủ định:** 
   * Câu *"Tôi muốn đặt bàn"* và *"Tôi bận nên không muốn đặt bàn"* đều chứa n-gram `"đặt bàn"`, dẫn đến xác suất cao bị dự đoán sai thành hành vi đặt chỗ.
3. **Khả năng khái quát hóa (Generalization) có giới hạn:** Khi người dùng sử dụng các từ đồng nghĩa hoặc cách diễn đạt hoàn toàn mới mà không chứa các n-gram đã học, mô hình sẽ không nhận diện được ý định.

---

## 5. Kết luận
Pipeline TF-IDF + Logistic Regression là giải pháp baseline lý tưởng cho giai đoạn thử nghiệm ban đầu (Proof of Concept), hệ thống yêu cầu độ trễ phản hồi siêu thấp, hoặc khi tài nguyên tính toán bị giới hạn nghiêm ngặt (không có GPU).
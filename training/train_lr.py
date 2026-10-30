import json
import os
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

DATA_PATH = "../data/train_vi.csv"
MODEL_PATH = "../models/shop_meal_intent_model.joblib"
METRICS_PATH = "../models/evaluation.json"

def main():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(
            f"Chưa có {DATA_PATH}. Hãy chạy: python prepare_data.py"
        )

    df = pd.read_csv(DATA_PATH).dropna(subset=["text", "intent"])
    df["text"] = df["text"].astype(str).str.strip()
    df["intent"] = df["intent"].astype(str).str.strip()
    df = df[(df["text"] != "") & (df["intent"] != "")]

    if df["intent"].nunique() < 2:
        raise ValueError("Cần ít nhất 2 intent để huấn luyện mô hình.")

    counts = df["intent"].value_counts()

    # Stratified split hoạt động ổn định nhất khi mỗi lớp có từ 2-5 mẫu trở lên
    can_stratify = counts.min() >= 2

    X_train, X_test, y_train, y_test = train_test_split(
        df["text"],
        df["intent"],
        test_size=0.2,
        random_state=42,
        stratify=df["intent"] if can_stratify else None,
    )

    model = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                analyzer="char_wb",
                ngram_range=(2, 5),
                min_df=2,  # Tránh các n-gram nhiễu xuất hiện 1 lần
                max_features=40000,  # Giới hạn kích thước file model
                sublinear_tf=True,
            ),
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=2000,
                C=2.0,  # Điều chỉnh hệ số phạt phù hợp với TF-IDF
                class_weight="balanced",
                random_state=42,
            ),
        ),
    ])

    print(f"Số mẫu: {len(df)} | Số intent: {df['intent'].nunique()}")
    print("Đang huấn luyện...")
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    report = classification_report(
        y_test, predictions, output_dict=True, zero_division=0
    )

    print(f"\nAccuracy trên tập test: {accuracy:.4f}")
    print(classification_report(y_test, predictions, zero_division=0))

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(
            {"accuracy": accuracy, "classification_report": report},
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"Đã lưu mô hình: {MODEL_PATH}")
    print(f"Đã lưu đánh giá: {METRICS_PATH}")


if __name__ == "__main__":
    main()
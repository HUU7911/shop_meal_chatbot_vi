import os
import json
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score

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
    # Chỉ đánh giá stratified nếu mỗi intent có ít nhất 2 mẫu.
    if counts.min() >= 2:
        X_train, X_test, y_train, y_test = train_test_split(
            df["text"], df["intent"], test_size=0.2,
            random_state=42, stratify=df["intent"]
        )
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            df["text"], df["intent"], test_size=0.2, random_state=42
        )

    model = Pipeline([
        ("tfidf", TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(2, 5),
            min_df=1,
            sublinear_tf=True
        )),
        ("classifier", LogisticRegression(
            max_iter=2000,
            class_weight="balanced"
        ))
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

    os.makedirs("../models", exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(
            {"accuracy": accuracy, "classification_report": report},
            f, ensure_ascii=False, indent=2
        )
    print(f"Đã lưu mô hình: {MODEL_PATH}")
    print(f"Đã lưu đánh giá: {METRICS_PATH}")

if __name__ == "__main__":
    main()

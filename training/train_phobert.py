import json
import os
import evaluate
import numpy as np
import pandas as pd
import torch
from datasets import Dataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollatorWithPadding,
    Trainer,
    TrainingArguments,
)

DATA_PATH = "../data/train_vi.csv"
OUTPUT_DIR = "../models/phobert_intent_model"
MODEL_NAME = "vinai/phobert-base-v2"


def compute_metrics(eval_pred):
    f1_metric = evaluate.load("f1")
    acc_metric = evaluate.load("accuracy")

    predictions, labels = eval_pred
    preds = np.argmax(predictions, axis=1)

    f1 = f1_metric.compute(
        predictions=preds, references=labels, average="macro"
    )["f1"]
    acc = acc_metric.compute(predictions=preds, references=labels)["accuracy"]
    return {"accuracy": acc, "f1_macro": f1}


def main():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Không tìm thấy file: {DATA_PATH}")

    # 1. Đọc và làm sạch dữ liệu
    df = pd.read_csv(DATA_PATH).dropna(subset=["text", "intent"])
    df["text"] = df["text"].astype(str).str.strip()
    df["intent"] = df["intent"].astype(str).str.strip()
    df = df[(df["text"] != "") & (df["intent"] != "")]

    # 2. Mã hóa nhãn (Intent -> ID số)
    label_encoder = LabelEncoder()
    df["label"] = label_encoder.fit_transform(df["intent"])
    num_labels = len(label_encoder.classes_)

    id2label = {i: label for i, label in enumerate(label_encoder.classes_)}
    label2id = {label: i for i, label in enumerate(label_encoder.classes_)}

    # 3. Chia tập train / test
    counts = df["label"].value_counts()
    can_stratify = counts.min() >= 2

    train_df, val_df = train_test_split(
        df,
        test_size=0.2,
        random_state=42,
        stratify=df["label"] if can_stratify else None,
    )

    train_dataset = Dataset.from_pandas(train_df[["text", "label"]])
    val_dataset = Dataset.from_pandas(val_df[["text", "label"]])

    # 4. Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=False)

    def preprocess_function(examples):
        return tokenizer(examples["text"], truncation=True, max_length=128)

    tokenized_train = train_dataset.map(preprocess_function, batched=True)
    tokenized_val = val_dataset.map(preprocess_function, batched=True)

    # 5. Khởi tạo mô hình PhoBERT
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=num_labels,
        id2label=id2label,
        label2id=label2id,
    )

    # 6. Thiết lập tham số huấn luyện
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=32,
        per_device_eval_batch_size=16,
        num_train_epochs=2,
        weight_decay=0.01,
        load_best_model_at_end=True,
        metric_for_best_model="f1_macro",
        greater_is_better=True,
        logging_steps=50,
        save_total_limit=2,
        report_to="none",
    )

    # DataCollator vẫn dùng tham số `tokenizer`
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    # Trainer dùng `processing_class`
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_val,
        processing_class=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
    )

    print("Bắt đầu huấn luyện...")
    trainer.train()

    # 7. Đánh giá và lưu mô hình
    eval_results = trainer.evaluate()
    print("\nKết quả đánh giá:", eval_results)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    with open(os.path.join(OUTPUT_DIR, "labels.json"), "w", encoding="utf-8") as f:
        json.dump({"id2label": id2label, "label2id": label2id}, f, ensure_ascii=False, indent=2)

    print(f"Đã lưu mô hình tại: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
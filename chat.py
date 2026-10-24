import os
import joblib
import pandas as pd

MODEL_PATH = "models/shop_meal_intent_model.joblib"
DATA_PATH = "data/train_vi.csv"
CONFIDENCE_THRESHOLD = 0.35

def load_responses():
    if not os.path.exists(DATA_PATH):
        return {}
    df = pd.read_csv(DATA_PATH).dropna(subset=["intent", "response"])
    # Lấy một phản hồi tiếng Việt cho mỗi intent.
    return df.drop_duplicates("intent").set_index("intent")["response"].to_dict()

def reply(model, responses, message):
    message = " ".join(message.lower().split())
    if not message:
        return "Bạn hãy nhập câu hỏi để mình hỗ trợ nhé.", None, 0.0

    probabilities = model.predict_proba([message])[0]
    best_index = probabilities.argmax()
    intent = model.classes_[best_index]
    confidence = float(probabilities[best_index])

    if confidence < CONFIDENCE_THRESHOLD:
        return (
            "Mình chưa hiểu rõ yêu cầu. Bạn có thể diễn đạt theo cách khác "
            "hoặc liên hệ bộ phận hỗ trợ Shop Meal nhé.",
            "unknown",
            confidence
        )

    answer = responses.get(
        intent,
        "Mình đã ghi nhận yêu cầu. Bạn vui lòng liên hệ bộ phận hỗ trợ Shop Meal để được hướng dẫn cụ thể."
    )
    return answer, intent, confidence

def main():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Chưa có model. Hãy chạy python train.py trước.")

    model = joblib.load(MODEL_PATH)
    responses = load_responses()
    print("Chatbot Shop Meal đã sẵn sàng. Gõ 'thoat' để kết thúc.\n")

    while True:
        message = input("Bạn: ").strip()
        if message.lower() in {"thoat", "exit", "quit"}:
            print("Chatbot: Cảm ơn bạn đã sử dụng Shop Meal!")
            break
        answer, intent, confidence = reply(model, responses, message)
        print(f"Chatbot: {answer}")
        print(f"[intent={intent}, confidence={confidence:.2f}]\n")

if __name__ == "__main__":
    main()

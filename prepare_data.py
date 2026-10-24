import os
import re
import time
import pandas as pd

DATA_URL = (
    "https://huggingface.co/datasets/bitext/"
    "Bitext-restaurants-llm-chatbot-training-dataset/resolve/main/"
    "bitext-restaurants-llm-chatbot-training-dataset.csv"
)

RAW_PATH = "data/bitext_restaurants.csv"
OUTPUT_PATH = "data/train_vi.csv"
CACHE_PATH = "data/translation_cache.csv"

# None = dịch TOÀN BỘ dataset; đặt số (ví dụ 30) để chỉ lấy mẫu mỗi intent.
SAMPLES_PER_INTENT = None

# Dịch cục bộ bằng model, không phụ thuộc Google nên không bị rate limit.
MODEL_NAME = "Helsinki-NLP/opus-mt-en-vi"
BATCH_SIZE = 32
MAX_LENGTH = 128
NUM_BEAMS = 2       # 1 = nhanh nhất, 4 = chất lượng cao hơn nhưng chậm hơn
SAVE_EVERY = 10     # lưu cache sau mỗi 10 lô

INTENT_RESPONSES = {
    "cancel_catering": "Bạn vui lòng mở mục đơn đặt tiệc trong tài khoản Shop Meal để kiểm tra điều kiện hủy. Nếu không thấy tùy chọn hủy, hãy liên hệ bộ phận hỗ trợ.",
    "change_catering": "Bạn vui lòng mở đơn đặt tiệc để kiểm tra các tùy chọn thay đổi. Việc thay đổi có thể phụ thuộc vào trạng thái đơn.",
    "information_catering": "Shop Meal có thể hỗ trợ bạn tìm hiểu thông tin đặt món số lượng lớn. Vui lòng cung cấp số lượng suất ăn và thời gian mong muốn.",
    "order_catering": "Để đặt món số lượng lớn, vui lòng cho biết món ăn, số lượng suất và thời gian nhận hàng.",
    "information_company": "Shop Meal là hệ thống hỗ trợ khám phá món ăn và đặt món trực tuyến. Bạn có thể xem thực đơn và thông tin trên website.",
    "locations": "Bạn muốn tìm nhà hàng hoặc cửa hàng ở khu vực nào? Hãy cho biết tỉnh/thành phố hoặc địa chỉ gần bạn.",
    "file_complaint": "Rất tiếc vì trải nghiệm chưa tốt. Bạn vui lòng mô tả vấn đề và cung cấp mã đơn hàng nếu có để bộ phận hỗ trợ kiểm tra.",
    "customer_service": "Bạn có thể liên hệ bộ phận hỗ trợ Shop Meal qua kênh liên hệ được công bố trên website.",
    "human_agent": "Mình sẽ hướng dẫn bạn liên hệ nhân viên hỗ trợ. Vui lòng mô tả ngắn gọn vấn đề bạn đang gặp phải.",
    "events": "Bạn muốn tìm chương trình hoặc sự kiện nào? Hãy kiểm tra mục thông báo trên Shop Meal để xem thông tin mới nhất.",
    "leave_review": "Bạn có thể gửi đánh giá sau khi trải nghiệm món ăn hoặc dịch vụ. Hãy chia sẻ nhận xét cụ thể để Shop Meal cải thiện chất lượng.",
    "apply_franchise": "Yêu cầu nhượng quyền cần được trao đổi trực tiếp với đơn vị phụ trách. Vui lòng liên hệ qua kênh chính thức của Shop Meal.",
    "find_franchise": "Bạn muốn tìm thông tin nhượng quyền ở khu vực nào? Hãy liên hệ Shop Meal để được cung cấp thông tin phù hợp.",
    "franchising": "Để tìm hiểu về nhượng quyền, vui lòng liên hệ Shop Meal qua kênh chính thức để nhận điều kiện và quy trình cập nhật.",
    "privacy_policy": "Bạn vui lòng xem chính sách quyền riêng tư được công bố trên website Shop Meal để biết cách dữ liệu cá nhân được xử lý.",
    "check_menu": "Bạn có thể xem thực đơn trên Shop Meal để tham khảo món ăn, mô tả và giá hiện tại.",
    "check_offers": "Bạn vui lòng kiểm tra mục khuyến mãi trên Shop Meal để xem các ưu đãi đang áp dụng.",
    "information_allergens": "Thông tin chất gây dị ứng có thể khác nhau tùy món. Vui lòng kiểm tra mô tả món hoặc liên hệ bộ phận hỗ trợ trước khi đặt.",
    "cancel_order": "Bạn vui lòng mở mục đơn hàng để kiểm tra trạng thái và tùy chọn hủy. Khả năng hủy phụ thuộc vào trạng thái xử lý đơn.",
    "change_order": "Bạn vui lòng mở đơn hàng để kiểm tra tùy chọn thay đổi. Nếu đơn đã được xử lý, hãy liên hệ bộ phận hỗ trợ.",
    "delivery_time": "Thời gian giao hàng phụ thuộc vào địa chỉ, món ăn và tình trạng đơn. Hãy kiểm tra chi tiết đơn hàng để xem thông tin mới nhất.",
    "order_food_online": "Bạn hãy chọn món trong thực đơn, thêm vào giỏ hàng, kiểm tra số lượng và địa chỉ giao hàng rồi tiến hành đặt món.",
    "order_issue": "Bạn vui lòng mô tả sự cố và cung cấp mã đơn hàng nếu có. Không gửi mật khẩu hoặc thông tin thanh toán nhạy cảm.",
    "track_order": "Bạn hãy mở mục đơn hàng trong tài khoản Shop Meal để xem trạng thái cập nhật. Nếu chưa thấy thông tin, hãy cung cấp mã đơn cho bộ phận hỗ trợ.",
    "payment_methods": "Các phương thức thanh toán hiện có sẽ được hiển thị ở bước thanh toán của Shop Meal.",
    "report_payment_issue": "Nếu gặp lỗi thanh toán, hãy kiểm tra trạng thái giao dịch và mã đơn. Không thực hiện thanh toán lặp lại khi chưa xác minh giao dịch trước.",
    "cancel_reservation": "Bạn vui lòng kiểm tra thông tin đặt chỗ và tùy chọn hủy trong hệ thống. Điều kiện hủy phụ thuộc vào chính sách áp dụng.",
    "change_reservation": "Bạn vui lòng mở thông tin đặt chỗ để kiểm tra tùy chọn thay đổi thời gian hoặc số người.",
    "make_reservation": "Bạn hãy cung cấp địa điểm, ngày giờ, số người và yêu cầu đặc biệt để được hướng dẫn đặt chỗ.",
    "find_restaurant": "Bạn muốn tìm địa điểm ăn uống ở khu vực nào? Hãy cho biết tỉnh/thành phố hoặc khu vực mong muốn.",
}

DEFAULT_RESPONSE = (
    "Mình chưa có đủ thông tin cho yêu cầu này. "
    "Bạn vui lòng liên hệ bộ phận hỗ trợ Shop Meal."
)

EXTRA_EXAMPLES = [
    ("tôi muốn xem thực đơn", "check_menu"),
    ("shop có món gì ngon", "check_menu"),
    ("cho tôi xem giá các món ăn", "check_menu"),
    ("tôi muốn tìm món ăn mới", "check_menu"),
    ("có chương trình giảm giá không", "check_offers"),
    ("shop đang có khuyến mãi gì", "check_offers"),
    ("đơn hàng của tôi đang ở đâu", "track_order"),
    ("kiểm tra trạng thái đơn hàng giúp tôi", "track_order"),
    ("đơn hàng đã giao chưa", "track_order"),
    ("tôi muốn hủy đơn hàng", "cancel_order"),
    ("tôi đặt nhầm món, sửa đơn được không", "change_order"),
    ("bao lâu nữa thì giao tới", "delivery_time"),
    ("thời gian giao hàng mất bao lâu", "delivery_time"),
    ("tôi muốn đặt món online", "order_food_online"),
    ("làm sao để đặt đồ ăn", "order_food_online"),
    ("tôi không thanh toán được", "report_payment_issue"),
    ("shop chấp nhận thanh toán bằng gì", "payment_methods"),
    ("tôi muốn phản ánh về đơn hàng", "file_complaint"),
    ("cho tôi gặp nhân viên tư vấn", "human_agent"),
    ("làm sao để liên hệ hỗ trợ", "customer_service"),
    ("món này có đậu phộng không", "information_allergens"),
    ("tôi muốn đánh giá món ăn", "leave_review"),
    ("tìm quán ăn gần tôi", "find_restaurant"),
    ("tôi muốn đặt bàn cho bốn người", "make_reservation"),
    ("tôi muốn đổi giờ đặt bàn", "change_reservation"),
    ("tôi muốn hủy đặt bàn", "cancel_reservation"),
    ("tôi muốn đặt món cho một sự kiện", "order_catering"),
    ("tôi muốn tìm hiểu về shop meal", "information_company"),
    ("tôi muốn khiếu nại dịch vụ", "file_complaint"),
    ("tôi muốn biết chính sách bảo mật", "privacy_policy"),
]


def normalize(text):
    text = str(text).strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def load_cache():
    if not os.path.exists(CACHE_PATH):
        return {}

    try:
        df = pd.read_csv(CACHE_PATH).dropna(
            subset=["source", "translation"]
        )
        return {
            normalize(row.source): str(row.translation).strip()
            for row in df.itertuples(index=False)
            if str(row.translation).strip()
        }
    except (pd.errors.EmptyDataError, KeyError, ValueError) as exc:
        print(f"[CẢNH BÁO] Không đọc được cache: {exc}")
        return {}


def save_cache(cache):
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)

    pd.DataFrame(
        [
            {"source": source, "translation": translation}
            for source, translation in cache.items()
        ]
    ).to_csv(CACHE_PATH, index=False, encoding="utf-8-sig")


def download_dataset():
    if os.path.exists(RAW_PATH):
        print(f"Đang sử dụng dataset có sẵn: {RAW_PATH}")
        return pd.read_csv(RAW_PATH)

    print("Đang tải dataset Bitext từ Hugging Face...")
    df = pd.read_csv(DATA_URL)
    df.to_csv(RAW_PATH, index=False, encoding="utf-8-sig")
    print(f"Đã lưu dataset gốc: {RAW_PATH}")
    return df


def sample_dataset(df):
    required = {"instruction", "intent"}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Dataset thiếu các cột bắt buộc: {missing}"
        )

    df = df.dropna(subset=["instruction", "intent"]).copy()
    df["instruction"] = df["instruction"].astype(str).str.strip()
    df["intent"] = df["intent"].astype(str).str.strip()

    df = df[
        (df["instruction"] != "")
        & (df["intent"] != "")
    ]

    # Lấy mẫu riêng trong từng intent, giữ lại cột intent.
    groups = []

    for _, group in df.groupby("intent", sort=True):
        if SAMPLES_PER_INTENT is None:
            groups.append(group)
        else:
            count = min(len(group), SAMPLES_PER_INTENT)
            groups.append(
                group.sample(n=count, random_state=42)
            )

    if not groups:
        raise ValueError("Dataset không có dữ liệu hợp lệ.")

    sampled = pd.concat(groups, ignore_index=True)
    sampled = sampled[["instruction", "intent"]]

    print(f"Tổng số câu được chọn: {len(sampled)}")
    print(f"Số intent: {sampled['intent'].nunique()}")

    return sampled


def load_translator():
    """Tải model dịch cục bộ (lần đầu cần mạng để tải khoảng 300 MB)."""
    try:
        import torch  # noqa: F401
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
    except ImportError as exc:
        raise SystemExit(
            "Thiếu thư viện. Hãy chạy:\n"
            "  pip install transformers torch sentencepiece"
        ) from exc

    # transformers v5 đã bỏ pipeline("translation"), nên dùng model trực tiếp.
    print(f"Đang tải model dịch: {MODEL_NAME} ...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
    model.eval()
    return tokenizer, model


def _generate(translator, texts):
    import torch

    tokenizer, model = translator

    inputs = tokenizer(
        texts,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=MAX_LENGTH,
    )

    with torch.no_grad():
        generated = model.generate(
            **inputs,
            max_new_tokens=MAX_LENGTH,
            num_beams=NUM_BEAMS,
        )

    decoded = tokenizer.batch_decode(generated, skip_special_tokens=True)
    return [text.strip() for text in decoded]


def translate_texts(translator, texts):
    """Dịch một danh sách câu; nếu cả lô lỗi thì dịch từng câu một."""
    try:
        return _generate(translator, texts)
    except Exception as exc:
        print(f"[CẢNH BÁO] Dịch lô lỗi ({exc}); thử từng câu...")

    results = []
    for text in texts:
        try:
            results.append(_generate(translator, [text])[0])
        except Exception as exc:
            print(f"[BỎ QUA] Không dịch được: {text} ({exc})")
            results.append(None)
    return results


def translate_dataset(sampled, cache):
    sources = sampled["instruction"].tolist()
    intents = sampled["intent"].tolist()

    # Gom các câu chưa có trong cache (bỏ trùng), sắp theo độ dài
    # để các câu trong cùng lô có độ dài gần nhau -> ít padding -> nhanh hơn.
    pending = {}
    for source in sources:
        key = normalize(source)
        if key not in cache and key not in pending:
            pending[key] = source

    todo = sorted(pending.values(), key=len)
    print(f"Cần dịch {len(todo)} câu (còn lại đã có trong cache).")

    if todo:
        translator = load_translator()
        started = time.time()
        total_batches = (len(todo) + BATCH_SIZE - 1) // BATCH_SIZE

        try:
            for index, start in enumerate(range(0, len(todo), BATCH_SIZE), 1):
                batch = todo[start:start + BATCH_SIZE]
                results = translate_texts(translator, batch)

                for source, result in zip(batch, results):
                    if result:
                        cache[normalize(source)] = result

                if index % SAVE_EVERY == 0 or index == total_batches:
                    save_cache(cache)

                done = min(start + BATCH_SIZE, len(todo))
                elapsed = time.time() - started
                eta = elapsed / done * (len(todo) - done)
                print(
                    f"Đã dịch {done}/{len(todo)} câu; "
                    f"còn khoảng {eta / 60:.1f} phút."
                )
        except KeyboardInterrupt:
            save_cache(cache)
            print("\nĐã dừng. Cache đã lưu, chạy lại để tiếp tục.")
            raise SystemExit(0)

    translated = []
    skipped = 0

    for source, intent in zip(sources, intents):
        vi = cache.get(normalize(source))

        if not vi:
            skipped += 1
            continue

        translated.append({
            "text": normalize(vi),
            "intent": intent,
            "response": INTENT_RESPONSES.get(intent, DEFAULT_RESPONSE),
        })

    if skipped:
        print(f"[CẢNH BÁO] Có {skipped} câu không dịch được.")

    return translated


def add_vietnamese_examples(translated):
    for text, intent in EXTRA_EXAMPLES:
        translated.append({
            "text": normalize(text),
            "intent": intent,
            "response": INTENT_RESPONSES.get(
                intent,
                "Bạn vui lòng liên hệ bộ phận hỗ trợ Shop Meal."
            )
        })

    return translated


def main():
    os.makedirs("data", exist_ok=True)

    df = download_dataset()
    sampled = sample_dataset(df)
    cache = load_cache()

    print(f"Số bản dịch đã lưu trong cache: {len(cache)}")
    print("Bắt đầu dịch dữ liệu sang tiếng Việt...")

    translated = translate_dataset(sampled, cache)
    translated = add_vietnamese_examples(translated)

    out = pd.DataFrame(translated)
    out = out.dropna(subset=["text", "intent", "response"])
    out["text"] = out["text"].astype(str).str.strip()
    out["intent"] = out["intent"].astype(str).str.strip()
    out = out[
        (out["text"] != "")
        & (out["intent"] != "")
    ]
    out = out.drop_duplicates(subset=["text", "intent"])

    out.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print("\n========== KẾT QUẢ ==========")
    print(f"Tổng mẫu: {len(out)}")
    print(f"Số intent: {out['intent'].nunique()}")
    print(f"File dữ liệu: {OUTPUT_PATH}")
    print(f"File cache: {CACHE_PATH}")
    print("\nSố mẫu theo intent:")
    print(out["intent"].value_counts().to_string())

    print(
        "\nHãy kiểm tra data/train_vi.csv để sửa các bản dịch "
        "chưa tự nhiên trước khi huấn luyện."
    )


if __name__ == "__main__":
    main()
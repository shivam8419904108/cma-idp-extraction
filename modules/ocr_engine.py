from functools import lru_cache
from modules.image_processor import preprocess_image


@lru_cache(maxsize=1)
def get_reader():
    import easyocr
    return easyocr.Reader(["en"], gpu=False)


def extract_page_text(image_array, page_number: int):
    processed = preprocess_image(image_array)
    results = get_reader().readtext(processed, detail=1, paragraph=False)
    records = []
    for box, text, confidence in results:
        xs = [point[0] for point in box]
        ys = [point[1] for point in box]
        records.append({
            "page": page_number,
            "text": text.strip(),
            "confidence": round(float(confidence) * 100, 2),
            "x1": round(min(xs), 1),
            "y1": round(min(ys), 1),
            "x2": round(max(xs), 1),
            "y2": round(max(ys), 1),
        })
    return records

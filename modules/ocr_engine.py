import os

import pandas as pd
import pytesseract
from pytesseract import Output
from PIL import Image

from modules.image_processor import preprocess_image


if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Users\ShivamGupta\AppData\Local\Tesseract-OCR\tesseract.exe"
    )

def extract_page_text(image_array, page_number: int):
    processed_image = preprocess_image(image_array)

    pil_image = Image.fromarray(processed_image)

    ocr_data = pytesseract.image_to_data(
        pil_image,
        lang="eng",
        config="--oem 3 --psm 6",
        output_type=Output.DATAFRAME
    )

    if ocr_data is None or ocr_data.empty:
        return []

    ocr_data = ocr_data.dropna(subset=["text"])

    records = []

    for _, row in ocr_data.iterrows():
        text = str(row["text"]).strip()

        if not text:
            continue

        try:
            confidence = float(row["conf"])
        except (TypeError, ValueError):
            confidence = -1

        if confidence < 0:
            continue

        x1 = int(row["left"])
        y1 = int(row["top"])
        width = int(row["width"])
        height = int(row["height"])

        records.append(
            {
                "page": page_number,
                "text": text,
                "confidence": round(confidence, 2),
                "x1": x1,
                "y1": y1,
                "x2": x1 + width,
                "y2": y1 + height,
                "block": int(row.get("block_num", 0)),
                "paragraph": int(row.get("par_num", 0)),
                "line": int(row.get("line_num", 0)),
                "word": int(row.get("word_num", 0)),
            }
        )

    return records
import re

AMOUNT_PATTERN = re.compile(r"^\(?-?₹?\s*[0-9][0-9,]*(?:\.[0-9]+)?\)?$")
YEAR_PATTERN = re.compile(r"^(?:FY\s*)?(?:19|20)\d{2}(?:[-/]\d{2,4})?$")


def normalize_amount(value: str):
    cleaned = value.replace("₹", "").replace(",", "").replace(" ", "")
    negative = cleaned.startswith("(") and cleaned.endswith(")")
    cleaned = cleaned.strip("()")
    try:
        number = float(cleaned)
        return -number if negative else number
    except ValueError:
        return None


def parse_ocr_rows(records):
    rows = []
    by_page = {}
    for record in records:
        by_page.setdefault(record["page"], []).append(record)

    for page, items in by_page.items():
        items = sorted(items, key=lambda item: (item["y1"], item["x1"]))
        labels = [item for item in items if not AMOUNT_PATTERN.match(item["text"]) and not YEAR_PATTERN.match(item["text"])]
        amounts = [item for item in items if AMOUNT_PATTERN.match(item["text"])]

        for amount in amounts:
            candidates = [
                label for label in labels
                if label["x1"] < amount["x1"] and abs(label["y1"] - amount["y1"]) <= 35
            ]
            if not candidates:
                continue
            label = min(candidates, key=lambda item: abs(item["y1"] - amount["y1"]))
            confidence = round((label["confidence"] + amount["confidence"]) / 2, 2)
            rows.append({
                "Page": page,
                "Statement": "Unclassified",
                "Raw Label": label["text"],
                "Normalized Label": label["text"],
                "Year": "",
                "Amount": normalize_amount(amount["text"]),
                "Confidence": confidence,
                "Review Status": "Accepted" if confidence >= 90 else "Review",
            })
    return rows

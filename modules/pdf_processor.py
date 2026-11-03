import io
import pymupdf
import numpy as np
from PIL import Image


def open_pdf(pdf_bytes: bytes):
    return pymupdf.open(stream=pdf_bytes, filetype="pdf")


def render_page(document, page_index: int, dpi: int = 200):
    page = document[page_index]
    pixmap = page.get_pixmap(dpi=dpi, alpha=False)
    png_bytes = pixmap.tobytes("png")
    image = Image.open(io.BytesIO(png_bytes)).convert("RGB")
    return png_bytes, np.array(image)

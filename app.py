from pathlib import Path

import streamlit as st
import pandas as pd

from modules.pdf_processor import open_pdf, render_page
from modules.ocr_engine import extract_page_text
from modules.data_parser import parse_ocr_rows
from modules.excel_exporter import build_excel

st.set_page_config(page_title="CMA IDP Extraction", page_icon="📄", layout="wide")
st.title("CMA IDP Extraction")
st.caption("Phase 1: Scanned PDF to structured Excel")
st.info("Start with a small PDF for the first test. OCR uses EasyOCR in this starter build.")

uploaded_file = st.file_uploader(
    "Upload scanned financial PDF",
    type=["pdf"]
)

if uploaded_file is not None:
    pdf_bytes = uploaded_file.getvalue()

    try:
        document = open_pdf(pdf_bytes)
    except Exception as exc:
        st.error(f"Unable to open PDF: {exc}")
        st.stop()

    c1, c2, c3 = st.columns(3)

    c1.metric("File name", uploaded_file.name)
    c2.metric(
        "File size",
        f"{uploaded_file.size / 1024 / 1024:.2f} MB"
    )
    c3.metric("Total pages", len(document))

    dpi = st.select_slider(
        "Page quality (DPI)",
        options=[150, 200, 250, 300],
        value=200
    )

    run_ocr = False

    st.info(
        "PDF preview is available. Cloud OCR is temporarily disabled "
        "while the lightweight extraction engine is being configured."
    )

    if st.button("Process PDF", type="primary"):
        progress = st.progress(0)
        status = st.empty()

        previews = []
        raw_records = []

        for page_index in range(len(document)):
            status.write(
                f"Processing page {page_index + 1} "
                f"of {len(document)}"
            )

            image_bytes, image_array = render_page(
                document,
                page_index,
                dpi=dpi
            )

            previews.append(image_bytes)

            if run_ocr:
                raw_records.extend(
                    extract_page_text(
                        image_array,
                        page_index + 1
                    )
                )

            completed = int(
                ((page_index + 1) / len(document)) * 100
            )
            progress.progress(completed)

        parsed_rows = parse_ocr_rows(raw_records)

        st.session_state["previews"] = previews
        st.session_state["raw_records"] = raw_records
        st.session_state["parsed_rows"] = parsed_rows

        status.success("PDF processing completed successfully.")

if "previews" in st.session_state:
    tab1, tab2, tab3 = st.tabs(["Page preview", "Extracted data", "Raw OCR"])

    with tab1:
        for index, image_bytes in enumerate(st.session_state["previews"]):
            with st.expander(f"Page {index + 1}", expanded=index == 0):
                st.image(image_bytes, use_container_width=True)

    with tab2:
        rows_df = pd.DataFrame(st.session_state["parsed_rows"])
        if rows_df.empty:
            st.warning("No financial rows were identified. Review Raw OCR or try 300 DPI.")
        else:
            edited_df = st.data_editor(rows_df, use_container_width=True, num_rows="dynamic")
            excel_bytes = build_excel(
                file_name=uploaded_file.name,
                extracted_df=edited_df,
                raw_df=pd.DataFrame(st.session_state["raw_records"]),
            )
            st.download_button(
                "Download Excel",
                data=excel_bytes,
                file_name=f"{Path(uploaded_file.name).stem}_extracted.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
            )

    with tab3:
        st.dataframe(pd.DataFrame(st.session_state["raw_records"]), use_container_width=True)

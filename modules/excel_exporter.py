from io import BytesIO
from datetime import datetime
import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter


def _format_sheet(worksheet):
    header_fill = PatternFill("solid", fgColor="1F4E78")
    for cell in worksheet[1]:
        cell.font = Font(color="FFFFFF", bold=True)
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")
    worksheet.freeze_panes = "A2"
    worksheet.auto_filter.ref = worksheet.dimensions
    for column_cells in worksheet.columns:
        max_length = max(len(str(cell.value or "")) for cell in column_cells)
        worksheet.column_dimensions[get_column_letter(column_cells[0].column)].width = min(max(max_length + 2, 12), 45)


def build_excel(file_name: str, extracted_df: pd.DataFrame, raw_df: pd.DataFrame):
    output = BytesIO()
    review_df = extracted_df[extracted_df.get("Review Status", pd.Series(dtype=str)) == "Review"].copy()
    summary_df = pd.DataFrame([
        {"Field": "File Name", "Value": file_name},
        {"Field": "Processing Date", "Value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
        {"Field": "Extracted Rows", "Value": len(extracted_df)},
        {"Field": "Review Required", "Value": len(review_df)},
    ])
    validation_df = pd.DataFrame(columns=["Validation", "Expected", "Actual", "Status"])

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name="Document_Summary", index=False)
        extracted_df.to_excel(writer, sheet_name="Extracted_Data", index=False)
        review_df.to_excel(writer, sheet_name="Review_Required", index=False)
        validation_df.to_excel(writer, sheet_name="Validation_Log", index=False)
        raw_df.to_excel(writer, sheet_name="Raw_OCR", index=False)
        for worksheet in writer.book.worksheets:
            _format_sheet(worksheet)

    output.seek(0)
    return output.getvalue()

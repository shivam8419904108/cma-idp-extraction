# CMA IDP Extraction Starter

## Windows setup

1. Extract this ZIP.
2. Open the extracted `CMA_IDP_App` folder.
3. Double-click `setup_windows.bat` and wait for installation.
4. Double-click `run_app.bat`.
5. Open the Local URL shown in Command Prompt, usually `http://localhost:8501`.
6. Upload a scanned PDF and click **Process PDF**.

## Notes

- The first OCR run may download EasyOCR model files and can take longer.
- Start with a short PDF and 200 DPI.
- If text extraction is weak, retry using 300 DPI.
- This starter pairs nearby OCR labels and amounts. Complex CMA tables will require document-specific table logic after testing actual samples.

## Manual commands

```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

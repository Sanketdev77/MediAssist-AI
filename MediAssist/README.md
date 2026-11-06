# Tesseract OCR setup

`pytesseract` in `requirements.txt` is a Python wrapper; OCR also requires the
Tesseract executable to be installed on the machine running MediAssist.

On Windows, install Tesseract and set `TESSERACT_CMD` to the full path of
`tesseract.exe` (commonly `C:\Program Files\Tesseract-OCR\tesseract.exe`):

```powershell
$env:TESSERACT_CMD = "C:\Program Files\Tesseract-OCR\tesseract.exe"
```

Set this variable in your environment before starting MediAssist. Alternatively,
pass the executable path to `OCRProcessor(tesseract_path=...)` in Python.
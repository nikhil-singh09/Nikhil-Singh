"""Convert the included SVG invoice sample and extract its text with PyTesseract."""
from __future__ import annotations

import argparse
import os
from io import BytesIO
from pathlib import Path

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/sample_invoice.svg"))
    parser.add_argument("--output", type=Path, default=Path("outputs/ocr.txt"))
    args = parser.parse_args()

    try:
        import cairosvg
        import pytesseract
        from PIL import Image
    except ImportError as exc:
        raise SystemExit("Install requirements.txt before running the OCR example.") from exc

    engine = os.getenv("TESSERACT_CMD", "").strip()
    if engine:
        pytesseract.pytesseract.tesseract_cmd = engine
    image_bytes = cairosvg.svg2png(bytestring=args.input.read_bytes(), output_width=1500)
    image = Image.open(BytesIO(image_bytes))
    try:
        text = pytesseract.image_to_string(image, lang="eng", timeout=30)
    except pytesseract.TesseractNotFoundError as exc:
        raise SystemExit("Tesseract engine not found. Install it separately and add it to PATH.") from exc

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()

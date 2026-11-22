"""Consolidate worksheets from an Excel workbook into a validated report."""
from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

REQUIRED = {"client_name", "invoice_no", "outstanding_amount"}


def consolidate(source: Path, destination: Path) -> None:
    sheets = pd.read_excel(source, sheet_name=None)
    if not sheets:
        raise ValueError("The workbook contains no worksheets.")

    frames = []
    for sheet_name, frame in sheets.items():
        frame.columns = [str(column).strip().lower() for column in frame.columns]
        missing = REQUIRED.difference(frame.columns)
        if missing:
            raise ValueError(f"Sheet '{sheet_name}' is missing: {', '.join(sorted(missing))}")
        frame["source_sheet"] = sheet_name
        frames.append(frame)

    detail = pd.concat(frames, ignore_index=True)
    detail["outstanding_amount"] = pd.to_numeric(detail["outstanding_amount"], errors="coerce")
    if detail["outstanding_amount"].isna().any() or (detail["outstanding_amount"] < 0).any():
        raise ValueError("Outstanding amounts must be valid non-negative numbers.")

    summary = (
        detail.groupby("client_name", as_index=False)
        .agg(invoice_count=("invoice_no", "nunique"),
             total_outstanding=("outstanding_amount", "sum"))
        .sort_values("total_outstanding", ascending=False)
    )

    destination.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(destination, engine="openpyxl") as writer:
        detail.to_excel(writer, sheet_name="Invoice_Detail", index=False)
        summary.to_excel(writer, sheet_name="Client_Summary", index=False)
        for worksheet in writer.sheets.values():
            worksheet.freeze_panes = "A2"
            worksheet.auto_filter.ref = worksheet.dimensions
            for column_cells in worksheet.columns:
                width = min(max(len(str(cell.value or "")) for cell in column_cells) + 2, 36)
                worksheet.column_dimensions[column_cells[0].column_letter].width = width


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Source .xlsx workbook")
    parser.add_argument("--output", type=Path, required=True, help="Destination .xlsx workbook")
    args = parser.parse_args()
    consolidate(args.input, args.output)
    print(f"Report saved to {args.output.resolve()}")


if __name__ == "__main__":
    main()

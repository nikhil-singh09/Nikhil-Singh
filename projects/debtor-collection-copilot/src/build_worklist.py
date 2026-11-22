"""Build a validated, client-wise collections worklist. No emails are sent."""
from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

REQUIRED = {
    "client_ref", "client_name", "invoice_no", "invoice_date", "due_date",
    "days_overdue", "outstanding_amount", "client_email",
}
MIN_DAYS_OVERDUE = 90
MIN_OUTSTANDING = 100_000


def build_worklist(source: Path, output_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    data = pd.read_csv(source)
    missing = REQUIRED.difference(data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    data["days_overdue"] = pd.to_numeric(data["days_overdue"], errors="coerce")
    data["outstanding_amount"] = pd.to_numeric(data["outstanding_amount"], errors="coerce")
    if data[["days_overdue", "outstanding_amount"]].isna().any().any():
        raise ValueError("Invalid or missing numeric values in overdue days/outstanding amount.")
    if (data["outstanding_amount"] < 0).any():
        raise ValueError("Outstanding amount cannot be negative.")

    # Deduplicate using the business key before applying the eligibility filter.
    data = data.drop_duplicates(["client_ref", "invoice_no"], keep="first")
    eligible = data.loc[
        (data["days_overdue"] > MIN_DAYS_OVERDUE)
        & (data["outstanding_amount"] > MIN_OUTSTANDING)
    ].copy()
    eligible = eligible.sort_values("outstanding_amount", ascending=False)

    summary = (
        eligible.groupby(["client_ref", "client_name", "client_email"], as_index=False)
        .agg(
            invoice_count=("invoice_no", "nunique"),
            total_outstanding=("outstanding_amount", "sum"),
            invoice_list=("invoice_no", lambda values: ", ".join(sorted(values))),
        )
        .sort_values("total_outstanding", ascending=False)
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    # CSV previews remain available when the optional Excel writer is absent.
    eligible.to_csv(output_dir / "eligible_invoices.csv", index=False)
    summary.to_csv(output_dir / "client_summary.csv", index=False)
    try:
        eligible.to_excel(output_dir / "eligible_invoices.xlsx", index=False)
        summary.to_excel(output_dir / "client_summary.xlsx", index=False)
    except ImportError:
        pass
    (output_dir / "email_previews.txt").write_text(
        "\n\n".join(
            f"To: {row.client_email}\nSubject: Payment follow-up | Client Ref: {row.client_ref}\n"
            f"Hello {row.client_name},\nOur demo worklist shows {row.invoice_count} eligible "
            f"invoice(s) totalling {row.total_outstanding:,.2f}. Invoice references: {row.invoice_list}.\n"
            "Please review this draft against the source system before sending."
            for row in summary.itertuples()
        ),
        encoding="utf-8",
    )
    return eligible, summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/sample_invoices.csv"))
    parser.add_argument("--output", type=Path, default=Path("outputs"))
    args = parser.parse_args()
    invoices, clients = build_worklist(args.input, args.output)
    print(f"Eligible invoices: {len(invoices)} | Clients: {len(clients)}")
    print(f"Files saved to: {args.output.resolve()}")


if __name__ == "__main__":
    main()

"""Create review-only client communication drafts; no email is sent."""
import argparse
import csv
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

def build_drafts(source: Path, destination: Path, min_days: int, min_amount: Decimal) -> tuple[int, int]:
    groups = defaultdict(list)
    held = []
    with source.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            try:
                amount = Decimal(row["outstanding_amount"])
                days = int(row["days_overdue"])
            except (KeyError, ValueError, InvalidOperation):
                held.append({"client_ref": row.get("client_ref", ""), "reason": "invalid amount or overdue days"})
                continue
            if not row.get("client_ref") or not row.get("invoice_no"):
                held.append({"client_ref": row.get("client_ref", ""), "reason": "missing stable identifier"})
                continue
            if days <= min_days or amount <= min_amount:
                continue
            groups[row["client_ref"]].append((row, amount))
    destination.mkdir(parents=True, exist_ok=True)
    drafts_path = destination / "drafts_for_review.csv"
    with drafts_path.open("w", newline="", encoding="utf-8") as handle:
        fields = ["client_ref", "client_name", "recipient", "subject", "draft_body", "invoice_count", "total_outstanding", "review_status"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for ref, items in sorted(groups.items()):
            addresses = {item[0].get("client_email", "").strip() for item in items}
            if len(addresses) != 1 or not next(iter(addresses), ""):
                held.append({"client_ref": ref, "reason": "missing or conflicting recipient"})
                continue
            name = items[0][0].get("client_name", "Client")
            total = sum((amount for _, amount in items), Decimal("0"))
            invoices = ", ".join(sorted({item[0]["invoice_no"] for item in items}))
            writer.writerow({
                "client_ref": ref, "client_name": name, "recipient": next(iter(addresses)),
                "subject": f"Payment follow-up | {ref}",
                "draft_body": f"Hello {name}, our sample worklist shows {len(items)} eligible invoice(s) totalling {total:.2f}: {invoices}. Please review against the source system.",
                "invoice_count": len(items), "total_outstanding": f"{total:.2f}", "review_status": "DRAFT — HUMAN REVIEW REQUIRED",
            })
    with (destination / "held_records.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["client_ref", "reason"])
        writer.writeheader()
        writer.writerows(held)
    return len(groups), len(held)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/sample_invoices.csv"))
    parser.add_argument("--output", type=Path, default=Path("outputs"))
    parser.add_argument("--min-days-overdue", type=int, default=90)
    parser.add_argument("--min-outstanding", type=Decimal, default=Decimal("100000"))
    args = parser.parse_args()
    groups, held = build_drafts(args.input, args.output, args.min_days_overdue, args.min_outstanding)
    print(f"Client groups reviewed: {groups}; held items: {held}; drafts: {args.output / 'drafts_for_review.csv'}")

if __name__ == "__main__":
    main()

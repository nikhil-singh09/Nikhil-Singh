"""Curate a local transaction batch with transparent rejects."""
import argparse
import csv
from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

def run(source: Path, output: Path) -> tuple[int, int]:
    good, bad, totals = [], [], defaultdict(lambda: Decimal("0"))
    with source.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            try:
                event_date = date.fromisoformat(row["event_date"].strip()).isoformat()
                amount = Decimal(row["amount"])
                if amount < 0:
                    raise ValueError("negative amount")
                region = row["region"].strip().title()
                if not row["record_id"].strip() or not region:
                    raise ValueError("missing key field")
            except (KeyError, ValueError, InvalidOperation) as exc:
                bad.append({**row, "reject_reason": str(exc)})
                continue
            normalized = {"record_id": row["record_id"].strip(), "event_date": event_date, "amount": f"{amount:.2f}", "region": region}
            good.append(normalized)
            totals[(event_date, region)] += amount
    output.mkdir(parents=True, exist_ok=True)
    def write(name, rows, fields):
        with (output / name).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
    write("curated_transactions.csv", good, ["record_id", "event_date", "amount", "region"])
    write("rejected_rows.csv", bad, ["record_id", "event_date", "amount", "region", "reject_reason"])
    summary = [{"event_date": day, "region": region, "total_amount": f"{total:.2f}"} for (day, region), total in sorted(totals.items())]
    write("daily_region_summary.csv", summary, ["event_date", "region", "total_amount"])
    return len(good), len(bad)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/transactions.csv"))
    parser.add_argument("--output", type=Path, default=Path("outputs"))
    args = parser.parse_args()
    good, bad = run(args.input, args.output)
    print(f"Curated {good} row(s); rejected {bad}; see {args.output.resolve()}")

if __name__ == "__main__":
    main()

"""Aggregate illustrative monthly metrics into a small BI-ready summary."""
import argparse
import csv
import json
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

def summarize(source: Path, output: Path) -> list[dict]:
    groups = defaultdict(lambda: {"revenue": Decimal("0"), "target": Decimal("0"), "headcount": 0, "periods": set()})
    with source.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            try:
                revenue, target = Decimal(row["revenue"]), Decimal(row["target"])
                headcount = int(row["headcount"])
            except (KeyError, ValueError, InvalidOperation) as exc:
                raise ValueError(f"Invalid metric row: {row}") from exc
            if target < 0 or revenue < 0 or headcount < 0:
                raise ValueError("Metrics must be non-negative.")
            group = groups[row["partner"]]
            group["revenue"] += revenue
            group["target"] += target
            group["headcount"] = max(group["headcount"], headcount)
            group["periods"].add(row["period"])
    results = []
    for partner, group in groups.items():
        target = group["target"]
        results.append({"partner": partner, "periods": len(group["periods"]), "revenue": f'{group["revenue"]:.2f}', "target": f"{target:.2f}", "attainment_pct": f'{(group["revenue"] / target * 100) if target else Decimal("0"):.1f}', "headcount": group["headcount"]})
    results.sort(key=lambda row: Decimal(row["revenue"]), reverse=True)
    output.mkdir(parents=True, exist_ok=True)
    with (output / "partner_kpis.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0]) if results else ["partner", "periods", "revenue", "target", "attainment_pct", "headcount"])
        writer.writeheader()
        writer.writerows(results)
    (output / "snapshot.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/monthly_metrics.csv"))
    parser.add_argument("--output", type=Path, default=Path("outputs"))
    args = parser.parse_args()
    print(f"Partner summaries written: {len(summarize(args.input, args.output))}")

if __name__ == "__main__":
    main()

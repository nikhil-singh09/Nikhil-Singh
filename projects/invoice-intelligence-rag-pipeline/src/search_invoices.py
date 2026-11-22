"""Search fictional local invoice text with lexical scoring and evidence."""
import argparse
import json
import math
import re
from collections import Counter
from pathlib import Path

TOKEN = re.compile(r"[a-z0-9]+", re.I)
FIELDS = {
    "invoice_number": r"Invoice\s*(?:No\.?|Number)\s*:\s*([A-Z0-9-]+)",
    "vendor": r"Vendor\s*:\s*([^\n]+)",
    "invoice_date": r"Invoice Date\s*:\s*([^\n]+)",
    "total": r"Total\s*:\s*([^\n]+)",
}

def terms(text: str) -> list[str]:
    return [token.lower() for token in TOKEN.findall(text)]

def rank_documents(query: str, directory: Path) -> list[dict]:
    query_terms = set(terms(query))
    docs = []
    paths = sorted(directory.glob("*.txt"))
    document_terms = {path: Counter(terms(path.read_text(encoding="utf-8"))) for path in paths}
    df = Counter(term for counter in document_terms.values() for term in counter.keys())
    n = max(len(paths), 1)
    for path, counts in document_terms.items():
        score = sum((1 + math.log(counts[t])) * (math.log((1 + n) / (1 + df[t])) + 1) for t in query_terms if counts[t])
        text = path.read_text(encoding="utf-8")
        fields = {}
        for name, pattern in FIELDS.items():
            match = re.search(pattern, text, flags=re.I)
            fields[name] = {"value": match.group(1).strip() if match else None, "evidence": match.group(0).strip() if match else None}
        docs.append({"source": path.name, "score": round(score, 3), "fields": fields})
    return sorted(docs, key=lambda row: (-row["score"], row["source"]))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True)
    parser.add_argument("--input", type=Path, default=Path("data"))
    parser.add_argument("--output", type=Path, default=Path("outputs"))
    args = parser.parse_args()
    results = rank_documents(args.query, args.input)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "retrieval_results.json").write_text(json.dumps({"query": args.query, "results": results}, indent=2), encoding="utf-8")
    print(json.dumps(results[:3], indent=2))
if __name__ == "__main__":
    main()

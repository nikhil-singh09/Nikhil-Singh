"""A safe, fixed-query SQLite chat demo using fictional order data."""
import argparse
import sqlite3
from pathlib import Path

ORDERS = [
    ("Northwind Demo", "North", 1250.00),
    ("Contoso Sample", "South", 890.00),
    ("Northwind Demo", "North", 450.00),
    ("Fabrikam Training", "West", 1775.00),
]

def create_db():
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE orders (customer TEXT, region TEXT, amount REAL)")
    db.executemany("INSERT INTO orders VALUES (?, ?, ?)", ORDERS)
    return db

def answer(db, question):
    text = question.lower()
    if "region" in text or "area" in text:
        rows = db.execute(
            "SELECT region, ROUND(SUM(amount), 2) AS sales "
            "FROM orders GROUP BY region ORDER BY sales DESC"
        ).fetchall()
        return "\n".join(f"{region}: {sales:.2f}" for region, sales in rows)
    if "top customer" in text or "customers" in text:
        rows = db.execute(
            "SELECT customer, ROUND(SUM(amount), 2) AS sales "
            "FROM orders GROUP BY customer ORDER BY sales DESC"
        ).fetchall()
        return "\n".join(f"{name}: {sales:.2f}" for name, sales in rows)
    if "how many" in text or "count" in text or "orders" in text:
        count = db.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        return f"Sample order count: {count}"
    return "I can answer: total sales by region, top customers, or order count."

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--questions-file",
        type=Path,
        help="Optional text file with one sample question per line.",
    )
    args = parser.parse_args()
    db = create_db()

    if args.questions_file:
        questions = [
            line.strip()
            for line in args.questions_file.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        for question in questions:
            print(f"Ask: {question}")
            print(answer(db, question))
            print()
        return

    print("Sample SQL assistant. Type 'quit' to stop.")
    while True:
        question = input("Ask: ").strip()
        if question.lower() in {"quit", "exit"}:
            break
        print(answer(db, question))

if __name__ == "__main__":
    main()

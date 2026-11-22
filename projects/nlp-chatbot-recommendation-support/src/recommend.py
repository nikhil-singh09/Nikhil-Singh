"""Rank fictional product records and FAQ snippets by word overlap."""
import argparse
import csv
import re
from pathlib import Path

STOP={"the","a","an","for","to","and","with","is","of","in","i","need","want"}
def tokens(text):
    return {word for word in re.findall(r"[a-z0-9]+",text.lower()) if word not in STOP}

def rank(query, path):
    q=tokens(query)
    matches=[]
    with path.open(newline="",encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            words=tokens(" ".join(row.values()))
            overlap=len(q & words)
            score=overlap / max(len(q),1)
            if overlap:
                matches.append((score,row))
    return sorted(matches,key=lambda item:(-item[0],item[1].get("name",item[1].get("question",""))))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query",required=True)
    parser.add_argument("--catalog",type=Path,default=Path("data/products.csv"))
    parser.add_argument("--faqs",type=Path,default=Path("data/faqs.csv"))
    parser.add_argument("--top",type=int,default=3)
    args=parser.parse_args()
    products=rank(args.query,args.catalog)[:args.top]
    faqs=rank(args.query,args.faqs)[:args.top]
    print("Product suggestions:")
    for score,row in products: print(f"- {row['name']} ({score:.0%} text match): {row['description']}")
    print("Helpful FAQ matches:")
    for score,row in faqs: print(f"- {row['question']} ({score:.0%} text match): {row['answer']}")
    if not products and not faqs: print("No close text match. Ask a more specific question.")

if __name__=="__main__":
    main()

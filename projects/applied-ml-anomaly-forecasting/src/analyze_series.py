"""Produce a z-score anomaly flag and linear trend forecast."""
import argparse
import csv
import json
import math
from pathlib import Path

def fit_line(values):
    n=len(values)
    xbar=(n-1)/2
    ybar=sum(values)/n
    denom=sum((i-xbar)**2 for i in range(n))
    slope=sum((i-xbar)*(v-ybar) for i,v in enumerate(values))/denom if denom else 0.0
    return ybar-slope*xbar, slope

def analyze(source: Path, output: Path, horizon: int):
    rows=[]
    with source.open(newline="",encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows.append((row["period"],float(row["value"])))
    if len(rows)<3:
        raise ValueError("At least three observations are required.")
    vals=[v for _,v in rows]
    mean=sum(vals)/len(vals)
    variance=sum((v-mean)**2 for v in vals)/len(vals)
    std=math.sqrt(variance)
    intercept,slope=fit_line(vals)
    output.mkdir(parents=True,exist_ok=True)
    with (output/"scored_series.csv").open("w",newline="",encoding="utf-8") as handle:
        writer=csv.writer(handle);writer.writerow(["period","actual","z_score","anomaly","trend"])
        for i,(period,value) in enumerate(rows):
            z=(value-mean)/std if std else 0.0
            writer.writerow([period,value,round(z,3),abs(z)>=2,round(intercept+slope*i,3)])
    with (output/"forecast.csv").open("w",newline="",encoding="utf-8") as handle:
        writer=csv.writer(handle);writer.writerow(["step","forecast"])
        for step in range(1,horizon+1):
            writer.writerow([step,round(intercept+slope*(len(rows)-1+step),3)])
    return {"observations":len(rows),"mean":round(mean,3),"trend_per_period":round(slope,3),"anomalies":sum(abs((v-mean)/std)>=2 for v in vals) if std else 0}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,default=Path("data/monthly_demand.csv"))
    parser.add_argument("--output",type=Path,default=Path("outputs"))
    parser.add_argument("--horizon",type=int,default=3)
    args=parser.parse_args()
    if args.horizon<1: parser.error("--horizon must be positive")
    print(json.dumps(analyze(args.input,args.output,args.horizon),indent=2))

if __name__=="__main__":
    main()

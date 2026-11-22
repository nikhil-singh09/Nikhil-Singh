# Applied ML — Anomaly & Forecast Baseline

An explainable, dependency-light time-series baseline that flags unusual observations with a z-score and fits a straight-line trend for a short forecast horizon.

> This is a teaching baseline, not an ANN/LSTM implementation or production forecast. Results are illustrative and need domain validation.

![Workflow diagram](docs/workflow.svg)

## Run
python src/analyze_series.py --input data/monthly_demand.csv --output outputs --horizon 3

## Outputs
- scored_series.csv with anomaly scores and trend values
- forecast.csv with the next periods

The demo is intentionally transparent so assumptions can be reviewed before using a more advanced model.
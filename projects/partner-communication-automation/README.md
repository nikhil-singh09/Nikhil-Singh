# Partner Communication Automation — Draft Generator

A review-first demo that groups overdue invoice rows into client-level communication drafts.

> This is an independent portfolio example with fictional records. It writes local drafts only; it never sends email or connects to Outlook, Power Automate, or an employer system.

![Workflow diagram](docs/workflow.svg)

## What it does
- Validates invoice amount, overdue days, recipient and identifiers.
- Groups eligible items by client reference.
- Produces one CSV row per client with a subject and draft body.
- Holds records with missing or conflicting recipient addresses.

## Run
python src/build_drafts.py --input data/sample_invoices.csv --output demo-output

## Controls
Thresholds are command-line options. The draft file is an intermediate review artifact; verify totals, recipients and follow-up history before sending anything.

## Bundled demo output

A sample run using the included fictional inputs is saved in `demo-output/`: drafts_for_review.csv, held_records.csv. Run commands from this project folder to regenerate the artifacts.

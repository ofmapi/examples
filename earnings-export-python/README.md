# Earnings export (Python)

Walks `GET /v1/accounts/{account_id}/transactions` from a start date with
cursor pagination and writes every transaction to CSV.

```bash
pip install requests
export OFMAPI_KEY=ofmapi_...
python export_transactions.py acct_4f8a --start 2026-01-01 -o transactions.csv
```

Handles `429` by honoring `Retry-After`, and derives the CSV columns from
the data so new fields show up automatically. Pass `--type` to filter by
transaction type.

Reference: https://ofmapi.com/docs/api

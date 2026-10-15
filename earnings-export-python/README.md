# Earnings export (Python)

Walks `GET /v1/accounts/{account_id}/transactions` from a start date with
cursor pagination and writes every transaction to CSV.

> **Fixed 2026-10-15:** earlier copies of this script checked `has_more`
> instead of the API's `hasMore` field, so they stopped after the first
> page while still printing a row count. If you exported with an earlier
> copy, run the export again to get the complete file.

```bash
pip install requests
export OFMAPI_KEY=ofmapi_...
python export_transactions.py acct_4f8a --start 2026-01-01 -o transactions.csv
```

Handles `429` by honoring `Retry-After`, and derives the CSV columns from
the data so new fields show up automatically. Pass `--type` to filter by
transaction type.

Reference: https://ofmapi.com/docs/api

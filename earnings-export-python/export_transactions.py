"""Export an account's transactions to CSV through the OFMAPI OnlyFans API.

    pip install requests
    export OFMAPI_KEY=ofmapi_...
    python export_transactions.py acct_4f8a --start 2026-01-01 -o transactions.csv

Walks GET /v1/accounts/{id}/transactions with cursor pagination until
has_more is false. Column set is derived from the first page so the script
keeps working when the API adds fields.
"""
import argparse
import csv
import os
import sys
import time

import requests

API = "https://api.ofmapi.com/v1"


def fetch_all(account_id: str, start: str, tx_type: str | None):
    headers = {"Authorization": f"Bearer {os.environ['OFMAPI_KEY']}"}
    params = {"start": start}
    if tx_type:
        params["type"] = tx_type
    cursor = None
    while True:
        if cursor:
            params["cursor"] = cursor
        r = requests.get(f"{API}/accounts/{account_id}/transactions", headers=headers, params=params, timeout=60)
        if r.status_code == 429:
            time.sleep(int(r.headers.get("Retry-After", "2")))
            continue
        if r.status_code >= 400:
            problem = r.json()
            raise SystemExit(f"{r.status_code} {problem.get('code')}: {problem.get('detail') or problem.get('title')}")
        page = r.json()
        yield from page.get("transactions", [])
        if not page.get("has_more") or not page.get("cursor"):
            return
        cursor = page["cursor"]


def flatten(row: dict, prefix: str = "") -> dict:
    out = {}
    for k, v in row.items():
        key = f"{prefix}{k}"
        if isinstance(v, dict):
            out.update(flatten(v, f"{key}."))
        else:
            out[key] = v
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("account_id")
    parser.add_argument("--start", required=True, help="ISO date, e.g. 2026-01-01")
    parser.add_argument("--type", dest="tx_type", default=None, help="optional transaction type filter")
    parser.add_argument("-o", "--output", default="transactions.csv")
    args = parser.parse_args()

    rows = [flatten(t) for t in fetch_all(args.account_id, args.start, args.tx_type)]
    if not rows:
        print("no transactions in range")
        return 0

    columns = []
    for row in rows:
        for k in row:
            if k not in columns:
                columns.append(k)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {len(rows)} transactions to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

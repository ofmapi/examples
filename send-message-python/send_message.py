"""Send a DM (optionally a paid PPV) through the OFMAPI OnlyFans API.

    pip install requests
    export OFMAPI_KEY=ofmapi_...
    python send_message.py acct_4f8a 99887766 "Thanks for subscribing!"
    python send_message.py acct_4f8a 99887766 "Custom for you" --price 9.99

Every write accepts an Idempotency-Key header, so re-running the same
command with the same key does not send twice.
"""
import argparse
import os
import sys
import uuid

import requests

API = "https://api.ofmapi.com/v1"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("account_id", help="OFMAPI account id, e.g. acct_4f8a")
    parser.add_argument("user_id", type=int, help="OnlyFans user id of the fan")
    parser.add_argument("text")
    parser.add_argument("--price", type=float, default=0, help="PPV price in dollars (0 = free)")
    parser.add_argument("--idempotency-key", default=str(uuid.uuid4()))
    args = parser.parse_args()

    headers = {
        "Authorization": f"Bearer {os.environ['OFMAPI_KEY']}",
        "Idempotency-Key": args.idempotency_key,
    }
    body = {"text": args.text}
    if args.price:
        body["price"] = args.price

    r = requests.post(
        f"{API}/accounts/{args.account_id}/conversations/{args.user_id}/messages",
        headers=headers,
        json=body,
        timeout=30,
    )
    if r.status_code >= 400:
        problem = r.json()  # RFC 7807: type, title, status, code, detail
        print(f"{r.status_code} {problem.get('code')}: {problem.get('detail') or problem.get('title')}", file=sys.stderr)
        return 1

    print(r.json())
    return 0


if __name__ == "__main__":
    sys.exit(main())

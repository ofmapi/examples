# Send a message (Python)

Sends a DM, or a paid PPV with `--price`, through
`POST /v1/accounts/{account_id}/conversations/{user_id}/messages`.

```bash
pip install requests
export OFMAPI_KEY=ofmapi_...
python send_message.py acct_4f8a 99887766 "Thanks for subscribing!"
python send_message.py acct_4f8a 99887766 "Custom for you" --price 9.99
```

The script sends an `Idempotency-Key` header (a fresh UUID unless you pass
`--idempotency-key`), so retrying the same key never double-sends. Errors
are RFC 7807 problem documents; the script prints `code` and `detail`.

Reference: https://ofmapi.com/docs/api

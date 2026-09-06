# Webhook receiver (FastAPI)

Verifies the `X-OFMAPI-Signature` header (`t=<unix>,v1=<hex HMAC-SHA256 of
"<t>.<raw body>">`), rejects stale or tampered deliveries, and logs
`messages.received` and `tips.received` events.

```bash
pip install -r requirements.txt
export OFMAPI_WEBHOOK_SECRET=whsec_...
uvicorn main:app --port 8000
```

Then register `https://<your-host>/webhooks/ofmapi` as described in the
repository README. Deliveries are at-least-once; dedupe on `event_id` if
your handler is not idempotent.

Signature scheme and event catalog: https://ofmapi.com/docs/webhooks

"""Verified OFMAPI webhook receiver (FastAPI).

Run:
    pip install -r requirements.txt
    export OFMAPI_WEBHOOK_SECRET=whsec_...   # shown once when you create the endpoint
    uvicorn main:app --port 8000

Register the public URL of this server (for local testing, expose it with a
tunnel such as `cloudflared tunnel --url http://localhost:8000`):

    curl https://api.ofmapi.com/v1/webhooks -X POST \
      -H "Authorization: Bearer $OFMAPI_KEY" -H "Content-Type: application/json" \
      -d '{"url":"https://<your-host>/webhooks/ofmapi","events":["messages.received","tips.received"]}'

Signature scheme (see https://ofmapi.com/docs/webhooks):
    X-OFMAPI-Signature: t=<unix seconds>,v1=<hex HMAC-SHA256 of "<t>.<raw body>">
"""
import hashlib
import hmac
import os
import time

from fastapi import FastAPI, Header, HTTPException, Request

app = FastAPI()
SECRET = os.environ["OFMAPI_WEBHOOK_SECRET"].encode()
TOLERANCE_SECONDS = 300


def verify(raw_body: bytes, signature_header: str) -> None:
    try:
        parts = dict(p.split("=", 1) for p in signature_header.split(","))
        timestamp, v1 = parts["t"], parts["v1"]
    except (ValueError, KeyError):
        raise HTTPException(status_code=400, detail="malformed signature header")

    if abs(time.time() - int(timestamp)) > TOLERANCE_SECONDS:
        raise HTTPException(status_code=400, detail="stale timestamp")

    expected = hmac.new(SECRET, f"{timestamp}.".encode() + raw_body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, v1):
        raise HTTPException(status_code=401, detail="bad signature")


@app.post("/webhooks/ofmapi")
async def receive(request: Request, x_ofmapi_signature: str = Header(default="")):
    raw = await request.body()
    verify(raw, x_ofmapi_signature)

    event = await request.json()
    # Envelope: event, event_id, account_id, occurred_at, ingested_at, source, payload
    kind = event.get("event")
    payload = event.get("payload", {})

    if kind == "messages.received":
        print(f"[{event['account_id']}] DM from {payload.get('from_user_id')}: {payload.get('text')!r}")
    elif kind == "tips.received":
        print(f"[{event['account_id']}] tip: {payload}")
    else:
        print(f"[{event['account_id']}] {kind}")

    # Acknowledge fast; do real work on a queue. Deliveries are at-least-once,
    # so dedupe on event_id if your handler is not idempotent.
    return {"ok": True}

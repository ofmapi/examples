# Webhook receiver (Go)

The same verified receiver in Go, standard library only.

```bash
OFMAPI_WEBHOOK_SECRET=whsec_... go run .
# listening on :8080/webhooks/ofmapi
```

Deliveries are at-least-once; dedupe on `event_id` if your handler is not
idempotent.

Signature scheme and event catalog: https://ofmapi.com/docs/webhooks

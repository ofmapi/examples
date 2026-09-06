# Webhook receiver (Hono)

The same verified receiver in TypeScript. `index.ts` is a Hono app that
runs unchanged on Cloudflare Workers, Bun, and Deno; `server.ts` hosts it
on Node.

```bash
npm install
OFMAPI_WEBHOOK_SECRET=whsec_... npm start
# listening on http://localhost:8787/webhooks/ofmapi
```

Signature verification uses Web Crypto, so no Node-only modules are
required. Deliveries are at-least-once; dedupe on `event_id` if your handler
is not idempotent.

Signature scheme and event catalog: https://ofmapi.com/docs/webhooks

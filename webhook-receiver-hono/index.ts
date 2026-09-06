/**
 * Verified OFMAPI webhook receiver (Hono). Runs on Cloudflare Workers, Bun,
 * Deno, or Node.
 *
 *   npm install
 *   OFMAPI_WEBHOOK_SECRET=whsec_... npm start        # Node via @hono/node-server
 *
 * Register the public URL once:
 *   POST https://api.ofmapi.com/v1/webhooks
 *   { "url": "https://<your-host>/webhooks/ofmapi", "events": ["messages.received"] }
 *
 * Signature scheme (https://ofmapi.com/docs/webhooks):
 *   X-OFMAPI-Signature: t=<unix seconds>,v1=<hex HMAC-SHA256 of "<t>.<raw body>">
 */
import { Hono } from "hono";

type Env = { OFMAPI_WEBHOOK_SECRET: string };

const app = new Hono<{ Bindings: Env }>();
const TOLERANCE_SECONDS = 300;

async function hmacHex(secret: string, message: string): Promise<string> {
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(message));
  return [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function timingSafeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

app.post("/webhooks/ofmapi", async (c) => {
  const secret = c.env?.OFMAPI_WEBHOOK_SECRET ?? process.env.OFMAPI_WEBHOOK_SECRET ?? "";
  const header = c.req.header("X-OFMAPI-Signature") ?? "";
  const parts = Object.fromEntries(header.split(",").map((p) => p.split("=", 2)));
  const { t, v1 } = parts as { t?: string; v1?: string };
  if (!t || !v1) return c.text("malformed signature header", 400);
  if (Math.abs(Date.now() / 1000 - Number(t)) > TOLERANCE_SECONDS) return c.text("stale timestamp", 400);

  const raw = await c.req.text();
  const expected = await hmacHex(secret, `${t}.${raw}`);
  if (!timingSafeEqual(expected, v1)) return c.text("bad signature", 401);

  const event = JSON.parse(raw) as {
    event: string;
    event_id: string;
    account_id: string;
    payload: Record<string, unknown>;
  };

  if (event.event === "messages.received") {
    console.log(`[${event.account_id}] DM from ${event.payload.from_user_id}: ${event.payload.text}`);
  } else {
    console.log(`[${event.account_id}] ${event.event}`);
  }

  // Deliveries are at-least-once: dedupe on event_id if your handler is not idempotent.
  return c.json({ ok: true });
});

export default app;

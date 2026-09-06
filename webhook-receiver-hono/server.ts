// Node entry point. On Cloudflare Workers, deploy index.ts directly instead.
import { serve } from "@hono/node-server";
import app from "./index";

const port = Number(process.env.PORT ?? 8787);
serve({ fetch: app.fetch, port }, () => {
  console.log(`listening on http://localhost:${port}/webhooks/ofmapi`);
});

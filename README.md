# OFMAPI examples

Small, self-contained examples for the [OFMAPI](https://ofmapi.com) OnlyFans
API. Each directory runs on its own with an API key from
[app.ofmapi.com/api-keys](https://app.ofmapi.com/api-keys) (free during the
public Beta, no card required).

| Example | What it shows |
|---|---|
| [`webhook-receiver-fastapi`](webhook-receiver-fastapi) | Verify the `X-OFMAPI-Signature` header and handle `messages.received` in Python. |
| [`webhook-receiver-hono`](webhook-receiver-hono) | The same receiver in TypeScript on Hono, for Node, Bun, Deno, or Cloudflare Workers. |
| [`webhook-receiver-go`](webhook-receiver-go) | The same receiver in Go with only the standard library. |
| [`send-message-python`](send-message-python) | Send a DM or a paid PPV with an `Idempotency-Key`, and read RFC 7807 errors. |
| [`earnings-export-python`](earnings-export-python) | Walk `GET /v1/accounts/{id}/transactions` with cursor pagination and write a CSV. |

Every request is plain HTTPS with a Bearer token, so the examples translate
directly to any language. For typed clients, see the generation guides for
[Python](https://ofmapi.com/docs/sdk/python),
[TypeScript](https://ofmapi.com/docs/sdk/node), and
[Go](https://ofmapi.com/docs/sdk/go).

## Register a webhook for the receivers

```bash
curl https://api.ofmapi.com/v1/webhooks -X POST \
  -H "Authorization: Bearer $OFMAPI_KEY" -H "Content-Type: application/json" \
  -d '{"url":"https://<your-host>/webhooks/ofmapi","events":["messages.received","tips.received"]}'
```

The signing secret is returned once in that response; store it as
`OFMAPI_WEBHOOK_SECRET`. For local testing expose the receiver with a tunnel
such as `cloudflared tunnel --url http://localhost:8000`.

## More

- Quickstart: https://ofmapi.com/docs/quickstart
- Interactive API reference (no login): https://ofmapi.com/docs/api
- Webhook event catalog and signature scheme: https://ofmapi.com/docs/webhooks
- Postman collection: https://github.com/ofmapi/postman-collection
- Hosted MCP server for Claude, ChatGPT, Cursor, and VS Code: https://ofmapi.com/integrations/mcp

Contributions are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).

---

OFMAPI is an independent organisation, not affiliated with OnlyFans.com or
Fenix International Limited. "OnlyFans" is a registered trademark of Fenix
International Limited.

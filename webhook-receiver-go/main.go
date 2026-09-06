// Verified OFMAPI webhook receiver (Go, standard library only).
//
//	OFMAPI_WEBHOOK_SECRET=whsec_... go run .
//
// Register the public URL once:
//
//	POST https://api.ofmapi.com/v1/webhooks
//	{ "url": "https://<your-host>/webhooks/ofmapi", "events": ["messages.received"] }
//
// Signature scheme (https://ofmapi.com/docs/webhooks):
//
//	X-OFMAPI-Signature: t=<unix seconds>,v1=<hex HMAC-SHA256 of "<t>.<raw body>">
package main

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"math"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"
)

const toleranceSeconds = 300

type envelope struct {
	Event     string                 `json:"event"`
	EventID   string                 `json:"event_id"`
	AccountID string                 `json:"account_id"`
	Payload   map[string]interface{} `json:"payload"`
}

func verify(secret []byte, header string, body []byte) error {
	parts := map[string]string{}
	for _, kv := range strings.Split(header, ",") {
		if k, v, ok := strings.Cut(kv, "="); ok {
			parts[k] = v
		}
	}
	ts, err := strconv.ParseInt(parts["t"], 10, 64)
	if err != nil || parts["v1"] == "" {
		return fmt.Errorf("malformed signature header")
	}
	if math.Abs(float64(time.Now().Unix()-ts)) > toleranceSeconds {
		return fmt.Errorf("stale timestamp")
	}
	mac := hmac.New(sha256.New, secret)
	mac.Write([]byte(parts["t"] + "."))
	mac.Write(body)
	expected := hex.EncodeToString(mac.Sum(nil))
	if !hmac.Equal([]byte(expected), []byte(parts["v1"])) {
		return fmt.Errorf("bad signature")
	}
	return nil
}

func main() {
	secret := []byte(os.Getenv("OFMAPI_WEBHOOK_SECRET"))
	if len(secret) == 0 {
		log.Fatal("OFMAPI_WEBHOOK_SECRET is required")
	}

	http.HandleFunc("/webhooks/ofmapi", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
			return
		}
		body, err := io.ReadAll(io.LimitReader(r.Body, 1<<20))
		if err != nil {
			http.Error(w, "read error", http.StatusBadRequest)
			return
		}
		if err := verify(secret, r.Header.Get("X-OFMAPI-Signature"), body); err != nil {
			http.Error(w, err.Error(), http.StatusUnauthorized)
			return
		}

		var ev envelope
		if err := json.Unmarshal(body, &ev); err != nil {
			http.Error(w, "bad json", http.StatusBadRequest)
			return
		}
		switch ev.Event {
		case "messages.received":
			log.Printf("[%s] DM from %v: %v", ev.AccountID, ev.Payload["from_user_id"], ev.Payload["text"])
		default:
			log.Printf("[%s] %s", ev.AccountID, ev.Event)
		}

		// Deliveries are at-least-once: dedupe on EventID if the handler is not idempotent.
		w.Header().Set("Content-Type", "application/json")
		w.Write([]byte(`{"ok":true}`))
	})

	addr := ":8080"
	log.Printf("listening on %s/webhooks/ofmapi", addr)
	log.Fatal(http.ListenAndServe(addr, nil))
}

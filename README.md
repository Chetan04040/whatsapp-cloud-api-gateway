# WhatsApp Cloud API & Webhook Gateway

A production-ready, asynchronous **FastAPI Webhook Gateway & Message Engine** built for the official **Meta WhatsApp Business Cloud API**. 

Designed as a modular, scalable communication service for enterprise conversational CX, CRM synchronization, and automated bot workflows.

---

## Key Features

- **Webhook Subscription Verification:** Full compliance with Meta's `hub.challenge`, `hub.mode`, and `hub.verify_token` challenge-response protocol.
- **HMAC SHA-256 Security:** Cryptographic payload verification via `X-Hub-Signature-256` header using your Meta App Secret.
- **Async Outbound Messaging:** Dispatches messages via Meta Graph API using `httpx` with connection pooling and timeouts.
- **Interactive UI Elements:** Pre-built Pydantic models and endpoints for:
  - Text messages (with optional URL previews)
  - Quick-reply action buttons (up to 3 interactive choices)
  - Interactive selection lists (categorized sections & rows)
- **Automatic Read Receipts:** Automatically marks incoming customer messages as read (double blue ticks).
- **Postman Test Suite:** Complete Postman v2.1 collection included for instant local or cloud testing.
- **Containerized:** Docker & Docker Compose ready.

---

## Architecture Flow

```
Meta WhatsApp Cloud API ──► [ GET /webhook ]  (Verification Challenge)
Meta WhatsApp Cloud API ──► [ POST /webhook ] ──► HMAC Verification ──► Event Router ──► Read Receipt / CRM
Client Application      ──► [ POST /api/v1/messages/* ] ──► WhatsApp Service ──► Meta Graph API
```

---

## Quickstart

### 1. Clone & Setup Environment

```bash
git clone https://github.com/Chetan04040/whatsapp-cloud-api-gateway.git
cd whatsapp-cloud-api-gateway

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your Meta Cloud API credentials:

```bash
cp .env.example .env
```

| Variable | Description |
|---|---|
| `WHATSAPP_TOKEN` | System User or Temporary Access Token from Meta Developer Portal |
| `PHONE_NUMBER_ID` | WhatsApp Business Phone Number ID |
| `VERIFY_TOKEN` | Custom secure string configured in Meta Webhook settings |
| `APP_SECRET` | App Secret from Meta App Dashboard (for HMAC signature check) |
| `API_VERSION` | Meta Graph API version (default: `v21.0`) |

### 3. Run the Service

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- Interactive Swagger Docs: `http://localhost:8000/docs`
- Healthcheck: `http://localhost:8000/health`

---

## Postman Collection

Import `postman_collection.json` directly into Postman to test:
1. `GET /health` - Service health status
2. `GET /webhook` - Webhook verification simulation
3. `POST /webhook` - Inbound message payload simulation
4. `POST /api/v1/messages/text` - Outbound text delivery
5. `POST /api/v1/messages/quick-replies` - Interactive button delivery
6. `POST /api/v1/messages/list` - Interactive list menu delivery

---

## Docker Deployment

```bash
docker build -t whatsapp-cloud-api-gateway .
docker run -p 8000:8000 --env-file .env whatsapp-cloud-api-gateway
```

---

## Attribution & License

- Built and maintained by [Chetan Rupchandani](https://github.com/Chetan04040).
- Foundational architectural patterns referenced from `ibrahimpelumi6142/whatsapp-cloud-api-starter`.
- Released under the [MIT License](LICENSE).

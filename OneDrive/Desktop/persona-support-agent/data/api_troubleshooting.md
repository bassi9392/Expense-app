# API Troubleshooting Guide

## Overview
This document covers the most common API integration issues and their resolutions
for the SupportDesk platform REST API (v3).

---

## 1. Authentication Errors

### 401 Unauthorized
**Cause:** The API key is missing, expired, or has insufficient scope.

**Resolution Steps:**
1. Verify the `Authorization` header is correctly formatted:
   ```
   Authorization: Bearer <your_api_key>
   ```
2. Confirm your API key has not expired. Keys expire every 90 days.
   Rotate them via: **Dashboard → Settings → API Keys → Rotate Key**
3. Ensure the key has the required permission scopes:
   - `read:tickets` — to fetch ticket data
   - `write:tickets` — to create or update tickets
   - `admin:users` — to manage user accounts
4. IP allowlisting: If your organisation has enabled IP allowlisting,
   confirm the outbound IP of your server is whitelisted.

**Sample curl test:**
```bash
curl -X GET https://api.supportdesk.io/v3/tickets \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json"
```

---

### 403 Forbidden
**Cause:** The key is valid but lacks the required scope for the endpoint.

**Resolution:** Navigate to **Dashboard → API Keys → Edit Scopes** and add the missing scope.

---

## 2. Rate Limiting

### 429 Too Many Requests
**Cause:** You've exceeded 1 000 requests per minute on the Standard plan.

**Resolution:**
- Inspect the response headers:
  ```
  X-RateLimit-Limit: 1000
  X-RateLimit-Remaining: 0
  X-RateLimit-Reset: 1718000000   ← Unix timestamp when limit resets
  ```
- Implement exponential back-off with jitter in your client:
  ```python
  import time, random
  def call_with_backoff(fn, *args, retries=5):
      for i in range(retries):
          try:
              return fn(*args)
          except RateLimitError:
              time.sleep((2**i) + random.random())
  ```
- Upgrade to the Enterprise plan for 10 000 requests/minute.

---

## 3. Webhook Configuration

### Webhook Not Firing
**Checklist:**
1. URL must be publicly accessible (not `localhost`).
2. HTTPS is required; self-signed certificates are rejected.
3. Your endpoint must respond with HTTP 200 within 5 seconds.
4. Verify the event type is subscribed: **Dashboard → Webhooks → Edit → Events**.

### Webhook Signature Verification
All payloads include an `X-SupportDesk-Signature` header.
Verify with HMAC-SHA256:
```python
import hmac, hashlib
def verify_signature(payload_bytes, signature_header, secret):
    expected = hmac.new(secret.encode(), payload_bytes, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header)
```

---

## 4. SDK Integration

### Python SDK
```bash
pip install supportdesk-sdk
```
```python
from supportdesk import Client
client = Client(api_key="YOUR_KEY")
tickets = client.tickets.list(status="open")
```

### Node.js SDK
```bash
npm install @supportdesk/sdk
```
```javascript
const { SupportDesk } = require('@supportdesk/sdk');
const client = new SupportDesk({ apiKey: process.env.SD_API_KEY });
const tickets = await client.tickets.list({ status: 'open' });
```

---

## 5. Common HTTP Status Codes

| Code | Meaning                        | Action                              |
|------|--------------------------------|-------------------------------------|
| 200  | OK                             | Success                             |
| 201  | Created                        | Resource created successfully       |
| 400  | Bad Request                    | Check request body / parameters     |
| 401  | Unauthorized                   | Check API key and Authorization header |
| 403  | Forbidden                      | Check permission scopes             |
| 404  | Not Found                      | Verify the endpoint URL             |
| 422  | Unprocessable Entity           | Validate JSON payload schema        |
| 429  | Too Many Requests              | Implement backoff / upgrade plan    |
| 500  | Internal Server Error          | Retry; contact support if persists  |
| 503  | Service Unavailable            | Check status.supportdesk.io         |

---

## 6. Data Format Requirements

### Date-Time Fields
All date-time fields must be ISO 8601 UTC:
```
"created_at": "2024-06-15T09:30:00Z"
```

### Pagination
Use cursor-based pagination:
```
GET /v3/tickets?cursor=<next_cursor>&limit=50
```
Response includes `meta.next_cursor`; pass it to retrieve the next page.

---

## 7. Contact & Escalation
- **API Status Page:** https://status.supportdesk.io
- **Developer Community:** https://community.supportdesk.io
- **Priority Support:** Available on Enterprise plan — response within 2 hours.

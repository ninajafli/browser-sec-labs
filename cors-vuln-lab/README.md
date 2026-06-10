# CORS Misconfiguration Lab

A hands-on lab demonstrating how a misconfigured CORS policy lets a malicious
website read a logged-in user's data from another origin. The victim and the
attacker run as two separate servers on different ports, so the requests in the
lab are genuinely cross-origin — the same shape as a real `evil.com` → `bank.com`
attack.

The vulnerable code is intentional. Run this only in an isolated environment.

## Layout

```
cors-vuln-lab/
├── docker-compose.yml      # starts both servers
├── victim/
│   ├── Dockerfile
│   └── app.py              # SecureBank: vulnerable + fixed endpoints
└── attacker/
    ├── Dockerfile
    └── app.py              # exploit pages and data collector
```

| Server   | Origin                  | Role                                    |
|----------|-------------------------|-----------------------------------------|
| Victim   | `http://localhost:5000` | SecureBank app with the vulnerable API  |
| Attacker | `http://localhost:8000` | Malicious site hosting the exploits     |

## Quick start

```bash
docker-compose up
```

Then, in a browser:

1. Open `http://localhost:5000/` and click **Load My Personal Data**. This sets a
   session cookie, simulating a logged-in user.
2. Open `http://localhost:8000/exploit-simple` and click **Claim my prize**.
3. The attacker's page reads your SecureBank data across origins and displays it.

Watch both servers' logs (`docker-compose logs -f`) to see the request arrive at
the victim and the stolen data arrive at the attacker.

## How the attack works

1. The victim is logged into SecureBank, so the browser holds a `session_id`
   cookie for `localhost:5000`.
2. The victim opens the attacker's page on `localhost:8000`.
3. The attacker's JavaScript issues a cross-origin request with credentials:

   ```javascript
   const xhr = new XMLHttpRequest();
   xhr.open("GET", "http://localhost:5000/api/v2/user/", true);
   xhr.withCredentials = true;   // attach the victim's cookies
   xhr.send();
   ```

4. The browser includes the victim's session cookie and sends
   `Origin: http://localhost:8000`.
5. The victim server reflects that origin back and allows credentials:

   ```
   Access-Control-Allow-Origin: http://localhost:8000
   Access-Control-Allow-Credentials: true
   ```

6. Because the server vouched for the attacker's origin, the browser lets the
   attacker's JavaScript read the response. The data is then POSTed to
   `http://localhost:8000/collect`.

## The vulnerability

In `victim/app.py`, the `/api/v2/user/` endpoint reflects whatever `Origin` it
receives:

```python
origin = request.headers.get('Origin')
if origin:
    response.headers['Access-Control-Allow-Origin'] = origin       # reflects anything
    response.headers['Access-Control-Allow-Credentials'] = 'true'
```

Reflecting the request's origin and pairing it with
`Access-Control-Allow-Credentials: true` means *any* site can read authenticated
responses on a logged-in user's behalf.

## The fix

The `/fixed/api/v2/user/` endpoint checks the origin against an allow-list before
setting any CORS headers:

```python
ALLOWED_ORIGINS = ['http://localhost:5000']

origin = request.headers.get('Origin')
if origin and origin in ALLOWED_ORIGINS:
    response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Credentials'] = 'true'
# otherwise: no CORS headers, so the browser blocks the cross-origin read
```

Compare the two endpoints with a tool like curl or Burp Repeater:

```bash
# Vulnerable: reflects the attacker's origin
curl -s -D - -o /dev/null http://localhost:5000/api/v2/user/ \
  -H 'Origin: http://localhost:8000' \
  -H 'Cookie: session_id=session_abc123'

# Fixed: no Access-Control-Allow-Origin for the attacker's origin
curl -s -D - -o /dev/null http://localhost:5000/fixed/api/v2/user/ \
  -H 'Origin: http://localhost:8000' \
  -H 'Cookie: session_id=session_abc123'
```

## Exercises

1. **Find it.** Proxy the browser through Burp, load your data on SecureBank, and
   find `GET /api/v2/user/` in the HTTP history. Send it to Repeater, add
   `Origin: http://localhost:8000`, and confirm the reflected CORS headers.
2. **Exploit it.** Run `exploit-simple`, then `exploit-advanced`, and watch the
   two-step steal-and-exfiltrate flow across both servers' logs. The collected
   data is viewable at `http://localhost:8000/stolen-data`.
3. **Confirm the fix.** Repeat the Repeater test against `/fixed/api/v2/user/`
   with both the attacker origin and `http://localhost:5000`. Only the allowed
   origin should get CORS headers back.
4. **Write your own fix.** Apply allow-list validation to `/api/v2/user/` in
   `victim/app.py`, restart with `docker-compose restart victim`, and verify the
   exploit pages now fail.

## Reference

- [PortSwigger Web Security Academy — CORS](https://portswigger.net/web-security/cors)
- [OWASP — CORS misconfiguration](https://owasp.org/www-community/attacks/CORS_OriginHeaderScrutiny)
- [MDN — Cross-Origin Resource Sharing](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)

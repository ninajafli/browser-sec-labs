from flask import Flask, make_response
import secrets

app = Flask(__name__)

with open('/app/index.html', 'r') as f:
    HTML_TEMPLATE = f.read()


@app.route('/')
def index():
    nonce = secrets.token_urlsafe(16)
    html = HTML_TEMPLATE.replace('RANDOM_NONCE_VALUE', nonce)

    # Nonce is present but there is no 'strict-dynamic', so the whitelisted
    # Google reCAPTCHA paths still apply - and they serve a full AngularJS build.
    csp = (
        f"script-src 'nonce-{nonce}' "
        "https://www.google.com/recaptcha/ "
        "https://www.gstatic.com/recaptcha/ "
        "'unsafe-inline'; "
        "default-src 'self'; "
        "img-src * data:; "
        "style-src 'self' 'unsafe-inline';"
    )

    response = make_response(html)
    response.headers['Content-Security-Policy'] = csp
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8181)

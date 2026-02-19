from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json
import os

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        # Parse query string
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        dataset   = params.get('dataset', [''])[0]
        data_id   = params.get('data_id', [''])[0]
        start_date = params.get('start_date', ['2022-01-01'])[0]
        end_date  = params.get('end_date', [''])[0]

        if not dataset:
            self._send(400, {'error': 'missing dataset'})
            return

        # Build FinMind URL
        token = os.environ.get('FINMIND_TOKEN', '')
        fm_params = {
            'dataset': dataset,
            'start_date': start_date,
        }
        if data_id:
            fm_params['data_id'] = data_id
        if end_date:
            fm_params['end_date'] = end_date
        if token:
            fm_params['token'] = token

        url = 'https://api.finmindtrade.com/api/v4/data?' + urllib.parse.urlencode(fm_params)

        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=15) as resp:
                body = resp.read()
            self._send(200, json.loads(body))
        except Exception as e:
            self._send(500, {'error': str(e)})

    def _send(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

    def log_message(self, format, *args):
        pass

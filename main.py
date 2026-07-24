import os
import re
import requests
from flask import Flask, request, jsonify, redirect

app = Flask(__name__)

# Lista de instancias públicas de Invidious para fallback si una falla
INVIDIOUS_INSTANCES = [
    "https://inv.tux.pizza",
    "https://invidious.nerdvpn.de",
    "https://invidious.drgns.space",
    "https://vid.puffyan.us"
]

@app.route('/get_stream', methods=['GET'])
def get_stream():
    url = request.args.get('url')
    if not url:
        return jsonify({'status': 'error', 'message': 'Falta el parámetro url'}), 400

    try:
        # Extraer el ID del video
        match = re.search(r'(?:v=|/live/|/embed/|youtu\.be/)([a-zA-Z0-9_-]{11})', url)
        if not match:
            return jsonify({'status': 'error', 'message': 'ID de video no válido'}), 400
        
        video_id = match.group(1)

        # Consultar la API de Invidious
        m3u8_url = None
        for instance in INVIDIOUS_INSTANCES:
            try:
                api_url = f"{instance}/api/v1/videos/{video_id}"
                resp = requests.get(api_url, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    # Invidious entrega la URL HLS del directo aquí:
                    m3u8_url = data.get('hlsUrl')
                    if m3u8_url:
                        break
            except Exception:
                continue

        if m3u8_url:
            return redirect(m3u8_url, code=302)
        else:
            return jsonify({'status': 'error', 'message': 'No se encontró la transmisión o la IP fue restringida'}), 404

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

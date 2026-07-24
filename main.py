import os
import re
import requests
from flask import Flask, request, jsonify, redirect

app = Flask(__name__)

# Instancias públicas de Piped / Cobalt optimizadas para streams en vivo
PIPED_INSTANCES = [
    "https://pipedapi.kavin.rocks",
    "https://api.piped.privacydev.net",
    "https://pipedapi.tokhmi.xyz",
    "https://piped-api.garudalinux.org"
]

@app.route('/get_stream', methods=['GET'])
def get_stream():
    url = request.args.get('url')
    if not url:
        return jsonify({'status': 'error', 'message': 'Falta el parámetro url'}), 400

    try:
        # Extraer el ID del video (soporta watch, live, embed, youtu.be)
        match = re.search(r'(?:v=|/live/|/embed/|youtu\.be/)([a-zA-Z0-9_-]{11})', url)
        if not match:
            return jsonify({'status': 'error', 'message': 'ID de video no válido'}), 400
        
        video_id = match.group(1)

        m3u8_url = None

        # Consultar las instancias de Piped API
        for instance in PIPED_INSTANCES:
            try:
                api_url = f"{instance}/streams/{video_id}"
                resp = requests.get(api_url, timeout=4)
                if resp.status_code == 200:
                    data = resp.json()
                    
                    # 1. Buscar en hls (URL del manifesto en directo)
                    m3u8_url = data.get('hls')
                    if m3u8_url:
                        break

                    # 2. Si no viene en hls, buscar en la lista de streams la variante hls/m3u8
                    audio_video_streams = data.get('audioVideoStreams', [])
                    for s in audio_video_streams:
                        if s.get('format') == 'M3U8' or '.m3u8' in s.get('url', ''):
                            m3u8_url = s.get('url')
                            break
                    
                    if m3u8_url:
                        break
            except Exception:
                continue

        if m3u8_url:
            # Redirección directa al flujo .m3u8 ejecutable
            return redirect(m3u8_url, code=302)
        else:
            return jsonify({
                'status': 'error', 
                'message': 'No se pudo obtener el stream .m3u8 en este momento'
            }), 404

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

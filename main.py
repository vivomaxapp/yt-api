import os
import re
import requests
from flask import Flask, request, jsonify, redirect

app = Flask(__name__)

@app.route('/get_stream', methods=['GET'])
def get_stream():
    url = request.args.get('url')
    if not url:
        return jsonify({'status': 'error', 'message': 'Falta el parámetro url'}), 400

    try:
        # 1. Extraer ID del video
        match = re.search(r'(?:v=|/live/|/embed/|youtu\.be/)([a-zA-Z0-9_-]{11})', url)
        if not match:
            return jsonify({'status': 'error', 'message': 'ID de video no válido'}), 400
        
        video_id = match.group(1)

        # 2. Consultar la versión de video directamente con un User-Agent de Android
        watch_url = f"https://www.youtube.com/watch?v={video_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        }

        response = requests.get(watch_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # 3. Extraer la URL del m3u8 del manifiesto HLS en el JS subyacente
            hls_match = re.search(r'["\']hlsManifestUrl["\']:\s*["\'](https?://[^"\']+\.m3u8)', response.text.replace('\\/', '/'))
            
            if hls_match:
                m3u8_url = hls_match.group(1)
                return redirect(m3u8_url, code=302)
            else:
                return jsonify({
                    'status': 'error', 
                    'message': 'No se encontró el enlace .m3u8 o la transmisión no está en vivo'
                }), 404
        else:
            return jsonify({
                'status': 'error', 
                'message': f'Error al conectar con YouTube ({response.status_code})'
            }), 500

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

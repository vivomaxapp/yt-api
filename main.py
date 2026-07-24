import os
import re
import requests
from flask import Flask, jsonify, request, redirect

app = Flask(__name__)

@app.route('/get_stream', methods=['GET'])
def get_stream():
    url = request.args.get('url')
    if not url:
        return jsonify({'status': 'error', 'message': 'Falta el parámetro url'}), 400

    try:
        # 1. Extraer el ID del video (Soporta watch, live, embed, youtu.be)
        video_id_match = re.search(r'(?:v=|/live/|/embed/|youtu\.be/)([a-zA-Z0-9_-]{11})', url)
        if not video_id_match:
            return jsonify({'status': 'error', 'message': 'ID de video no válido'}), 400

        video_id = video_id_match.group(1)

        # 2. Consultar el embed con un User-Agent moderno
        embed_url = f"https://www.youtube.com/embed/{video_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        response = requests.get(embed_url, headers=headers, timeout=10)

        # 3. Buscar hlsManifestUrl o cualquier enlace .m3u8 en el HTML/JS
        # Esta Regex busca la URL del m3u8 sin importar cuántas barras '\\' tenga escapadas
        match = re.search(r'hlsManifestUrl["\']:\s*["\'](https?://[^"\']+\.m3u8)', response.text.replace('\\/', '/'))

        if match:
            m3u8_url = match.group(1)
            # Redirige directamente al flujo .m3u8 que los reproductores (IPTV/Android) pueden reproducir
            return redirect(m3u8_url, code=302)
        else:
            return jsonify({'status': 'error', 'message': 'No se encontró el enlace .m3u8 o la transmisión no está en vivo'}), 404

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

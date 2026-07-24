import os
import re
import subprocess
from flask import Flask, request, jsonify, redirect

app = Flask(__name__)

COOKIES_FILE = 'cookies.txt'

@app.route('/get_stream', methods=['GET'])
def get_stream():
    url = request.args.get('url')
    if not url:
        return jsonify({'status': 'error', 'message': 'Falta el parámetro url'}), 400

    try:
        # 1. Extraer ID del video o directo
        match = re.search(r'(?:v=|/live/|/embed/|youtu\.be/)([a-zA-Z0-9_-]{11})', url)
        if not match:
            return jsonify({'status': 'error', 'message': 'ID de video no válido'}), 400
        
        target_url = f"https://www.youtube.com/watch?v={match.group(1)}"

        # 2. Comando yt-dlp forzando clientes móviles (iOS / Android)
        cmd = [
            'yt-dlp',
            '-g',
            '--extractor-args', 'youtube:player_client=ios,android,mweb',
            '--no-warnings',
            '--no-playlist'
        ]

        # 3. Incluir cookies si existen
        if os.path.exists(COOKIES_FILE):
            cmd.extend(['--cookies', COOKIES_FILE])

        cmd.append(target_url)

        # 4. Ejecutar el proceso
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)

        if result.returncode == 0 and result.stdout.strip():
            # Obtener el primer enlace m3u8 devuelto
            m3u8_url = result.stdout.strip().split('\n')[0]
            return redirect(m3u8_url, code=302)
        else:
            error_msg = result.stderr.strip() if result.stderr else "No se pudo extraer la URL"
            return jsonify({
                'status': 'error',
                'message': error_msg
            }), 500

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

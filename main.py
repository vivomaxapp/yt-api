import os
import subprocess
from flask import Flask, jsonify, request, redirect

app = Flask(__name__)

@app.route('/get_stream', methods=['GET'])
def get_stream():
    url = request.args.get('url')
    if not url:
        return jsonify({'status': 'error', 'message': 'Falta el parámetro url'}), 400

    try:
        # Extraer el enlace m3u8 con yt-dlp
        command = ["yt-dlp", "-g", url]
        stream_url = subprocess.check_output(command).decode('utf-8').strip()
        
        # Redirigir directamente al reproductor
        return redirect(stream_url, code=302)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

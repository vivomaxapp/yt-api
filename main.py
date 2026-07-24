import os
import yt_dlp
from flask import Flask, jsonify, request, redirect

app = Flask(__name__)

@app.route('/get_stream', methods=['GET'])
def get_stream():
    url = request.args.get('url')
    if not url:
        return jsonify({'status': 'error', 'message': 'Falta el parámetro url'}), 400

    # Cambiar el cliente de extracción a android/web_embedded para evadir el bloqueo de bot
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web_embedded']
            }
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Obtener enlace m3u8 directo
            stream_url = info.get('url')
            
            if stream_url:
                return redirect(stream_url, code=302)
            else:
                return jsonify({'status': 'error', 'message': 'No se encontró enlace ejecutable'}), 500

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

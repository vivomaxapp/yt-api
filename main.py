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

        # 2. Consultar la API interna de YouTube emulando la App de iOS (evita bloqueos de Cloud/Render)
        player_url = "https://www.youtube.com/youtubei/v1/player"
        payload = {
            "videoId": video_id,
            "context": {
                "client": {
                    "clientName": "IOS",
                    "clientVersion": "19.29.1",
                    "deviceModel": "iPhone14,3",
                    "osName": "iOS",
                    "osVersion": "17.5.1.21F90"
                }
            }
        }
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'com.google.ios.youtube/19.29.1 (iPhone14,3; U; CPU iOS 17_5_1 like Mac OS X; en_US)'
        }

        response = requests.post(player_url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            streaming_data = data.get('streamingData', {})
            
            # Obtener la URL del manifesto HLS (.m3u8) directo para el directo
            hls_manifest_url = streaming_data.get('hlsManifestUrl')
            
            if hls_manifest_url:
                # Redirección directa al .m3u8 ejecutable
                return redirect(hls_manifest_url, code=302)
            else:
                return jsonify({
                    'status': 'error', 
                    'message': 'El video no es una transmisión en vivo activa o no tiene formato HLS'
                }), 404
        else:
            return jsonify({
                'status': 'error', 
                'message': f'Error en la API de YouTube ({response.status_code})'
            }), 500

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

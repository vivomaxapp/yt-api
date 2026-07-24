import os
import re
from flask import Flask, request, jsonify, redirect
import yt_dlp

app = Flask(__name__)

@app.route('/get_stream', methods=['GET'])
def get_stream():
    url = request.args.get('url')
    if not url:
        return jsonify({'status': 'error', 'message': 'Falta el parámetro url'}), 400

    try:
        # Configuración de yt-dlp optimizada para extraer enlaces directos m3u8
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            # Forzar clientes móbiles ayuda a evitar bloqueos de IP de data centers (Render)
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'ios']
                }
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Buscar el enlace del manifiesto m3u8 / HLS
            m3u8_url = info.get('url')
            
            # Si no está directamente en 'url', buscar en los formatos disponibles
            if not m3u8_url or '.m3u8' not in m3u8_url:
                formats = info.get('formats', [])
                for f in formats:
                    if f.get('protocol') in ['m3u8', 'm3u8_native'] or '.m3u8' in f.get('url', ''):
                        m3u8_url = f.get('url')
                        break

            if m3u8_url:
                # Redirige directamente al enlace .m3u8 funcional
                return redirect(m3u8_url, code=302)
            else:
                return jsonify({
                    'status': 'error', 
                    'message': 'No se encontró el enlace .m3u8 o la transmisión no está en vivo'
                }), 404

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

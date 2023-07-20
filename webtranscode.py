import subprocess
import threading
from flask import Flask, request, Response, jsonify
import traceback

app = Flask(__name__)
ffmpeg_process = None
ffmpeg_thread = None
clients = set()

def start_ffmpeg(url_string):
    global ffmpeg_process, ffmpeg_thread
    cmd = [
        'ffmpeg',
        '-i', f'http://{url_string}',
        '-vn',  # Disable video
        '-c:a', 'libmp3lame',
        '-b:a', '320k',  # Set audio bitrate to 320 kbps
        '-f', 'mp3',
        'pipe:1'  # Output to stdout (pipe)
    ]
    ffmpeg_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ffmpeg_thread = threading.Thread(target=ffmpeg_monitor)
    ffmpeg_thread.start()

def ffmpeg_monitor():
    global ffmpeg_process, ffmpeg_thread
    ffmpeg_process.wait()  # Wait for ffmpeg process to complete
    ffmpeg_thread = None  # Reset the thread after ffmpeg completes
    print("FFmpeg process stopped.")

def stop_ffmpeg():
    global ffmpeg_process
    if ffmpeg_process:
        ffmpeg_process.kill()
        ffmpeg_process = None

@app.route('/transcode/<path:url_string>', methods=['GET'])
def transcode(url_string):
    global clients
    try:
        if not clients:
            # Start ffmpeg only if there are no active clients
            start_ffmpeg(url_string)

        # Add the client to the set of active clients
        clients.add(request.environ.get('REMOTE_ADDR'))

        def generate():
            try:
                while True:
                    data = ffmpeg_process.stdout.read(4096)
                    if not data:
                        break
                    yield data
            except:
                traceback.print_exc()
            finally:
                clients.discard(request.environ.get('REMOTE_ADDR'))
                if not clients:
                    # Stop ffmpeg when there are no active clients
                    stop_ffmpeg()

        # Set the response headers to indicate audio/mp3 content
        headers = {
            'Content-Type': 'audio/mp3',
            'Content-Disposition': 'attachment; filename="transcoded_audio.mp3"'
        }

        # Return the response with the generator as the audio data
        return Response(generate(), headers=headers)

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8901)

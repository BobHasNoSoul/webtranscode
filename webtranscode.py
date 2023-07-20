import subprocess
import threading
from flask import Flask, request, Response, jsonify
import traceback

app = Flask(__name__)
ffmpeg_processes = {}  # Dictionary to store ffmpeg processes for each active stream
ffmpeg_threads = {}    # Dictionary to store ffmpeg threads for each active stream

def start_ffmpeg(url_string, client_ip):
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
    ffmpeg_thread = threading.Thread(target=ffmpeg_monitor, args=(client_ip, ffmpeg_process))
    ffmpeg_thread.start()

    # Store the process and thread in the dictionaries
    ffmpeg_processes[client_ip] = ffmpeg_process
    ffmpeg_threads[client_ip] = ffmpeg_thread

def generate(client_ip):
    process = ffmpeg_processes.get(client_ip)
    if not process:
        return

    try:
        while process.poll() is None:  # Check if the process is still running
            data = process.stdout.read(4096)
            if not data:
                break
            yield data
    except:
        traceback.print_exc()
    finally:
        stop_ffmpeg(client_ip)


def ffmpeg_monitor(client_ip, process):
    process.wait()  # Wait for ffmpeg process to complete
    print(f"FFmpeg process for client {client_ip} stopped.")
    # Remove the process and thread from the dictionaries
    del ffmpeg_processes[client_ip]
    del ffmpeg_threads[client_ip]

def stop_ffmpeg(client_ip):
    process = ffmpeg_processes.get(client_ip)
    if process:
        process.kill()
        print(f"Stopping FFmpeg process for client {client_ip}")

@app.route('/transcode/<path:url_string>', methods=['GET'])
def transcode(url_string):
    try:
        client_ip = request.environ.get('REMOTE_ADDR')
        start_ffmpeg(url_string, client_ip)

        # Set the response headers to indicate audio/mp3 content
        headers = {
            'Content-Type': 'audio/mp3',
            'Content-Disposition': 'attachment; filename="transcoded_audio.mp3"'
        }

        # Return the response with the generator as the audio data, passing the client_ip
        return Response(generate(client_ip), headers=headers)

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
		
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8901)

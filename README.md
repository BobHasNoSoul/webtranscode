# webtranscode
a webtranscode to allow input of a hdhomerun stream to pull a mp3 stream out.. useful for navidrome radio urls (slight lag on initial load)

installation:
simply download the python script and run it and let it run and when clients connect to it via the url it will open a new ffmpeg instance and then transcode to them and when the client disconnects or stops the stream they will have the ffmpeg instance close.

you will require the following modules subprocess threading flask request Response jsonify

Usage:

`python3 webtranscode.py`

on the client stream via the following url

`http://YOUR_SERVER_IP_HERE:8901/transcode/YOUR_HDHOMERUN_STREAM_HERE`

for example if your server ip was 192.168.1.44 and the stream url was http://192.168.1.55:5004/auto/v717 it would be the following 

`http://192.168.1.76:8901/transcode/192.168.1.55:5004/auto/v717`





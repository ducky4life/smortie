FROM arm64v8/python:3.11-slim

LABEL org.opencontainers.image.source="https://github.com/ducky4life/smortie"

COPY music.py /smortie/music.py

COPY keep_alive.py /smortie/keep_alive.py

COPY .env /smortie/.env

# COPY playlists /smortie/playlists/

COPY requirements.txt /smortie/requirements.txt

RUN apt update && apt install -y ffmpeg git

RUN git clone --depth=1 https://github.com/ducky4life/smortie-playlists.git /smortie/playlists

RUN python -m pip install --upgrade pip

RUN pip install -r /smortie/requirements.txt

WORKDIR /smortie

CMD [ "python", "music.py" ]

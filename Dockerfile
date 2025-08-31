FROM arm64v8/python:3.11-slim

LABEL org.opencontainers.image.source="https://github.com/ducky4life/smortie"

COPY requirements.txt /

RUN python -m pip install --upgrade pip

RUN pip install -r requirements.txt

RUN apt update && apt install -y ffmpeg git

COPY /playlists /playlists

# RUN git clone --depth=1 https://github.com/ducky4life/smortie-playlists.git /playlists

COPY music.py keep_alive.py .env /

WORKDIR /

CMD [ "python", "music.py" ]

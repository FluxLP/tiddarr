FROM python:3.13-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY tiddarr ./tiddarr
RUN pip install --no-cache-dir .

ENV TIDDARR_DATA_DIR=/config \
    TIDDARR_MUSIC_DIR=/music \
    TIDDARR_PORT=8688 \
    PYTHONUNBUFFERED=1

VOLUME ["/config", "/music"]
EXPOSE 8688
CMD ["tiddarr"]

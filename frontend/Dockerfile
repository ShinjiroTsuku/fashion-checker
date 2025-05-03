# frontend/Dockerfile
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Fletが必要とする可能性のあるシステムライブラリ (環境によって必要になる場合)
# RUN apt-get update && apt-get install -y --no-install-recommends libgl1-mesa-glx libglib2.0-0 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

COPY ./app /app

# Fletアプリがリッスンするポート (main.pyのFLET_PORTと合わせる)
EXPOSE 8550

# Fletアプリケーションを実行 (Webモードでポートとホストを指定)
# ポート番号は docker-compose.yml や frontend/app/main.py と合わせる
# CMD ["python", "main.py"] # main.py内でft.app()でポート等を指定しているためこれで良い
# または flet run を使う場合:
CMD ["python", "main.py"]
# main.py内のft.app()で指定しているので CMD ["python", "main.py"] が推奨
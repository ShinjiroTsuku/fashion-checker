# backend/Dockerfile
# ベースイメージを指定
FROM python:3.10-slim

# 環境変数設定 (Pythonのバッファリング無効化など)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 作業ディレクトリを設定
WORKDIR /app

# 依存関係ファイルをコピーしてインストール
COPY ./app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# アプリケーションコードをコピー
COPY ./app /app

# FastAPIがリッスンするポート (Uvicornのデフォルトは8000)
EXPOSE 8000

# アプリケーションを実行
# コンテナ外からのアクセスを受け付けるために host 0.0.0.0 を指定
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
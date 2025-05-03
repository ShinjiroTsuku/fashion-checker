# backend/app/main.py
import os
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# .envファイルをコンテナ内で読み込む場合 (Composeで環境変数として渡す方が一般的)
# load_dotenv() # Docker Composeのenv_fileを使うので通常不要

# 環境変数からAPIキーを取得
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Error: GOOGLE_API_KEY environment variable not set.")
    exit() # APIキーがない場合は起動しない

try:
    genai.configure(api_key=api_key)
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    exit()

app = FastAPI(title="Gemini API Backend")

# CORS設定
# Docker環境では、Fletアプリ(ブラウザ)からのアクセス元(localhost:フロントエンドポート)を許可
# 環境変数で許可するオリジンを指定できるようにするとより柔軟
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8550") # デフォルトはComposeで設定するポート

origins = [
    FRONTEND_URL,
    "http://localhost", # ローカルデバッグ用に追加する場合
    "http://127.0.0.1", # ローカルデバッグ用に追加する場合
]
# 開発中は "*" も使えるが非推奨
# origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    prompt: str

try:
    model = genai.GenerativeModel('gemini-2.0-flash-lite') # 必要ならモデル名変更
except Exception as e:
    print(f"Error creating Gemini model: {e}")
    exit()

class Clothes(BaseModel):
    name: str

@app.post("/register", response_model=list[str])
def add_clothes(clothes: Clothes):
    new_clothes = clothes.name
    # ファイルに追記
    with open("clothes_list.txt", "a") as f:
        f.write(new_clothes + "\n")
    # ファイルから全ての服装を読み込む
    with open("clothes_list.txt", "r") as f:
        clothes_list = [line.strip() for line in f.readlines() if line.strip()]
    return clothes_list

# Uvicornはdocker-compose.ymlのcommandで起動するので、ここでは不要
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
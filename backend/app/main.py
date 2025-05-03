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
    model = genai.GenerativeModel('gemini-2.0-flash') # 必要ならモデル名変更
except Exception as e:
    print(f"Error creating Gemini model: {e}")
    exit()

@app.post("/generate", summary="Generate text using Gemini")
async def generate_text(request: PromptRequest):
    """Generates text based on the provided prompt using the Gemini API."""
    if not request.prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    try:
        response = model.generate_content(request.prompt)

        if hasattr(response, 'text'):
            generated_text = response.text
        elif response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            generated_text = "".join(part.text for part in response.candidates[0].content.parts)
        else:
            print(f"Unexpected Gemini API response format: {response}")
            raise HTTPException(status_code=500, detail="Failed to parse Gemini API response")

        return {"generated_text": generated_text}
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        error_detail = str(e)
        raise HTTPException(status_code=500, detail=f"Failed to generate text: {error_detail}")

@app.get("/", summary="Root endpoint")
def read_root():
    """Returns a welcome message indicating the backend is running."""
    return {"message": "Gemini API Backend is running!"}

# Uvicornはdocker-compose.ymlのcommandで起動するので、ここでは不要
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
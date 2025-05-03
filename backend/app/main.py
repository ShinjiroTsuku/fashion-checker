# backend/app/main.py
import os
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import datetime
import weather

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

try:
    model = genai.GenerativeModel('gemini-2.0-flash') # 必要ならモデル名変更
except Exception as e:
    print(f"Error creating Gemini model: {e}")
    exit()

class Prefecture_city(BaseModel):
    name: str

@app.post("/generate", response_model = dict, summary="Generate text using Gemini")
async def generate_text(prefecture_city: Prefecture_city):
    """
    データベース(clothes_list.txt)の内容と天気予報APIの情報を元に、Gemini APIを使用してテキストを生成。
    """
    try:
        parts = prefecture_city.name.split('_')
        if len(parts) != 2:
            raise HTTPException(status_code=400, detail="Invalid format. Expected 'prefecture_city'")
        
        prefecture, city = parts
        
        # clothes_list.txtからデータベース情報を取得
        clothes_data = "服装データが登録されていません。"
        try:
            with open("clothes_list.txt", "r", encoding="utf-8") as f:
                clothes_data = f.read().strip()
                if not clothes_data:
                    clothes_data = "服装データが登録されていません。"
        except Exception as e:
            print(f"Error reading clothes_list.txt: {e}")
            # ファイルが読めなくてもエラーにはせず、デフォルトメッセージを使用
        
        # 天気情報を取得
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="OpenWeather API key not found")
        
        # 緯度経度の取得
        coordinates = weather.get_lat_lon(prefecture, city)
        if not coordinates:
            raise HTTPException(status_code=404, detail=f"Location {prefecture}{city} not found")
        
        latitude, longitude = coordinates
        weather_data = weather.get_weather_forecast_by_coords(latitude, longitude, api_key)
        
        if not weather_data:
            raise HTTPException(status_code=500, detail="Failed to get weather forecast")
        
        # 天気情報から今日の予報を抽出
        today_forecasts = []
        now = datetime.datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        
        for forecast in weather_data.get("forecasts", []):
            forecast_time = forecast.get("datetime", "")
            if today_str in forecast_time:
                today_forecasts.append(forecast)
        
        # 天気情報の要約を作成
        weather_summary = "本日の天気情報:\n"
        for forecast in today_forecasts:
            time = forecast.get("datetime", "").split(" ")[1][:5]  # HH:MM 形式に変換
            desc = forecast.get("weather", {}).get("description", "不明")
            temp = forecast.get("temperature", "不明")
            precip = forecast.get("precipitation", 0)
            
            weather_summary += f"{time} - {desc}, 気温: {temp}℃, 降水量: {precip}mm\n"

        prompt = f"""
            あなたは優秀な天気予報士です。
            以下のテキストファイルで与えられる天気予報を参考にし、今日の服装を提案してください。
            要件は以下のとおりです。
            服装は、テキストファイル内の[服一覧]にあるものから選択してください。
            まず天気を時間帯ごとに説明し、次に服装を提案してください。
            天気を時間帯ごとに説明するときは、時間帯ごとに箇条書きで表示してください。
            1日の途中で着替えることは想定せず、想定される活動時間をいくつか示し、それぞれの場合で適切な服装を提案してください。
            一文目は、「かしこまりました」や「承知しました」とせず、天気の説明から始めてください。
            '--- END OF FILE data.txt ---'は表示しないでください。

            ## 天気情報
            場所: {prefecture}{city}
            {weather_summary}

            ## 利用可能な衣類データ
            {clothes_data}
            """

        try:
            response = model.generate_content(prompt)

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
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.get("/", summary="Root endpoint")
def read_root():
    """Returns a welcome message indicating the backend is running."""
    return {"message": "Gemini API Backend is running!"}

# Uvicornはdocker-compose.ymlのcommandで起動するので、ここでは不要
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
# backend/app/main.py
import os
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import datetime
import services.weather as weather

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
    model = genai.GenerativeModel('gemini-2.0-flash-lite') # 必要ならモデル名変更
except Exception as e:
    print(f"Error creating Gemini model: {e}")
    exit()

class Prefecture_city(BaseModel):
    name: str
      
class Clothes(BaseModel):
    name: str

class ClothesToDelete(BaseModel):
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
            with open("data/clothes_list.txt", "r", encoding="utf-8") as f:
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
        utc_now = datetime.datetime.utcnow()
        now = utc_now + datetime.timedelta(hours=9)
        today_str = now.strftime("%Y-%m-%d")
        now_str = now.strftime("%Y年%m月%d日 %H時%M分")

        daily_icon_url = weather_data.get("daily_icon_url", "")
        
        for forecast in weather_data.get("forecasts", []):
            forecast_time = forecast.get("datetime", "")
            if today_str in forecast_time:
                today_forecasts.append(forecast)
        
        # 天気情報の要約を作成
        weather_summary = "本日の天気情報:\n"
        for forecast in today_forecasts:
            time = forecast.get("datetime", "").split(" ")[1][:3]  # "HH時"のみ取得
            desc = forecast.get("weather", {}).get("description", "不明")
            temp = forecast.get("temperature", "不明")
            feels_like = forecast.get("feels_like", "不明")
            prob_precipitation = forecast.get("prob_precipitation", 0) * 100  # 確率をパーセントに変換
            precip = forecast.get("precipitation", 0)
            
            weather_summary += f"{time} - {desc}, 気温: {temp}℃, 体感温度: {feels_like}℃，降水確率: {prob_precipitation}%，降水量: {precip}mm\n"

        # プロンプトをファイルから読み込む
        try:
            with open("data/prompt_template.txt", "r", encoding="utf-8") as f:
                prompt_template = f.read()
                
            # テンプレートに変数を埋め込む
            prompt = prompt_template.format(
                now_str=now_str,
                prefecture=prefecture,
                city=city,
                weather_summary=weather_summary,
                clothes_data=clothes_data
            )
        except Exception as e:
            print(f"プロンプトテンプレートの読み込みに失敗しました: {e}")
        
        # デバッグ用にプロンプトをファイルに保存
        with open("data/prompt.txt", "w", encoding="utf-8") as f:
            f.write(prompt + "\n")

        try:
            response = model.generate_content(prompt)

            if hasattr(response, 'text'):
                generated_text = response.text
            elif response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                generated_text = "".join(part.text for part in response.candidates[0].content.parts)
            else:
                print(f"Unexpected Gemini API response format: {response}")
                raise HTTPException(status_code=500, detail="Failed to parse Gemini API response")

            return {"generated_text": generated_text, "daily_icon_url": daily_icon_url}
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            error_detail = str(e)
            raise HTTPException(status_code=500, detail=f"Failed to generate text: {error_detail}")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.post("/register", response_model=list[str])
def add_clothes(clothes: Clothes):
    new_clothes = clothes.name
    # ファイルに追記
    with open("data/clothes_list.txt", "a") as f:
        f.write(new_clothes + "\n")
    # ファイルから全ての服装を読み込む
    with open("data/clothes_list.txt", "r") as f:
        clothes_list = [line.strip() for line in f.readlines() if line.strip()]
    return clothes_list

@app.post("/delete", response_model=list[str])
def delete_clothes(clothes: ClothesToDelete):
    """
    指定された服装をデータベース(clothes_list.txt)から削除。
    """
    clothes_to_delete = clothes.name
    
    try:
        # ファイルから服装リストを読み込む
        with open("data/clothes_list.txt", "r", encoding="utf-8") as f:
            clothes_list = [line.strip() for line in f.readlines() if line.strip()]
        
        # 削除対象の服装がリストにあるか確認
        if clothes_to_delete not in clothes_list:
            raise HTTPException(status_code=404, detail=f"衣類 '{clothes_to_delete}' は見つかりませんでした")
        
        # 服装を削除
        clothes_list.remove(clothes_to_delete)
        
        # 更新されたリストをファイルに書き込む
        with open("data/clothes_list.txt", "w", encoding="utf-8") as f:
            for item in clothes_list:
                f.write(f"{item}\n")
        
        return clothes_list
    except HTTPException:
        raise
    except Exception as e:
        print(f"服装の削除中にエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail=f"服装の削除中にエラーが発生しました: {str(e)}")
    
@app.get("/list", response_model=list[str])
def get_clothes_list():
    """
    保存されている服のリストを取得する
    """
    try:
        # ファイルから服装リストを読み込む
        with open("data/clothes_list.txt", "r", encoding="utf-8") as f:
            clothes_list = [line.strip() for line in f.readlines() if line.strip()]
        
        return clothes_list
    except Exception as e:
        print(f"服装リストの取得中にエラーが発生しました: {e}")
        return []  # エラー時は空のリストを返す

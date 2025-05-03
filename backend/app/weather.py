import requests
import datetime
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

load_dotenv()

def get_lat_lon(prefecture, city):
    """
    県名と市名を入力すると、緯度と経度を出力する関数

    Args:
        prefecture (str): 県名（例: "東京都"）
        city (str): 市名（例: "新宿区"）

    Returns:
        tuple: (緯度, 経度) のタプル。見つからない場合は None を返す。
    """
    address = f"{prefecture}{city}"
    geolocator = Nominatim(user_agent="weather_app")
    try:
        location = geolocator.geocode(address, timeout=5)  # タイムアウトを設定
        if location:
            return (location.latitude, location.longitude)
        else:
            print(f"'{address}' の緯度経度が見つかりませんでした。")
            return None
    except GeocoderTimedOut:
        print("タイムアウトエラーが発生しました。")
        return None
    except GeocoderUnavailable:
        print("ジオコーダが利用できません。")
        return None
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

def get_weather_forecast_by_coords(lat, lon, api_key):
    """
    指定した緯度・経度の場所の現在時刻以降の3時間ごとの天気予報を取得する
    
    Parameters:
    -----------
    lat : float
        緯度
    lon : float
        経度
    api_key : str
        OpenWeather APIのAPIキー
    
    Returns:
    --------
    dict
        フォーマット済みの天気予報データ
    """
    
    utc_now = datetime.datetime.utcnow()
    start_time = utc_now + datetime.timedelta(hours=9)  # UTCから日本時間（+9時間）
    today = start_time.replace(hour=23, minute=59, second=59)  # 今日の終わり
    # APIのエンドポイントURL
    url = "https://api.openweathermap.org/data/2.5/forecast"
    
    # パラメータの設定
    params = {
        "lat": lat,  # 緯度
        "lon": lon,  # 経度
        "appid": api_key,  # APIキー
        "units": "metric",  # 摂氏で温度を取得
        "lang": "ja"  # 日本語で結果を取得
    }
    
    # APIリクエストを送信
    response = requests.get(url, params=params)
    
    # レスポンスが成功した場合
    if response.status_code == 200:
        data = response.json()
            
        # 必要なデータだけを抽出
        result = {
            "city": data["city"]["name"],
            "country": data["city"]["country"],
            "coordinates": {
                "latitude": lat,
                "longitude": lon
            },
            "forecasts": []
        }
        
        # 3時間ごとの予報データを処理
        for forecast in data["list"]:
            # UTC時間からJST(+9時間)に変換
            utc_time = datetime.datetime.utcfromtimestamp(forecast["dt"])
            forecast_time = utc_time + datetime.timedelta(hours=9)  # UTCから日本時間へ
            
            # 指定した開始時刻以降のデータのみ処理
            if start_time <= forecast_time <= today:
                # 降水量の取得（存在しない場合は0）
                rain_3h = forecast.get("rain", {}).get("3h", 0)
                
                # 必要なデータを抽出
                forecast_data = {
                    "datetime": forecast_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "weather": {
                        "main": forecast["weather"][0]["main"],
                        "description": forecast["weather"][0]["description"],
                        "icon": forecast["weather"][0]["icon"]
                    },
                    "temperature": forecast["main"]["temp"],
                    "feels_like": forecast["main"]["feels_like"],
                    "precipitation": rain_3h
                }
                
                result["forecasts"].append(forecast_data)
        
        return result
    else:
        print(f"エラー: {response.status_code}")
        return None

if __name__ == "__main__":
    print("This module is not intended to be run directly.")
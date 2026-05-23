from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import random

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

CACHE = {"time_slot": None, "quotes": ["Sống là cho đâu chỉ nhận riêng mình."]}

def get_weather_theme():
    try:
        response = requests.get("https://wttr.in/Ho_Chi_Minh?format=j1", timeout=3)
        data = response.json()
        code = int(data['current_condition'][0]['weatherCode'])
        
        if code == 113: return ["#f59e0b", "#d97706"], "☀️ Nắng", "☀️"
        elif code in [116, 119, 122]: return ["#475569", "#1e293b"], "☁️ Mây", "☁️"
        elif code >= 176 and code <= 356: return ["#1e3a8a", "#0f172a"], "🌧️ Mưa", "🌧️"
        return ["#111827", "#030712"], "✨ Dịu", "✨"
    except:
        return ["#065f46", "#022c22"], "🍃 Bình yên", "🍃"

def scrape_quotes():
    try:
        url = "https://www.thuvien-hay.com/danh-ngon-cuoc-song/"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')
        quotes = [p.text.strip() for p in soup.find_all('p') if len(p.text) > 20]
        return quotes if quotes else CACHE["quotes"]
    except:
        return CACHE["quotes"]

@app.get("/quote")
def get_quote():
    try:
        tz = pytz.timezone('Asia/Ho_Chi_Minh')
        now = datetime.now(tz)
        current_time_slot = f"{now.date()}_{now.hour}_{now.minute // 5}"
        
        if CACHE["time_slot"] != current_time_slot:
            CACHE["quotes"] = scrape_quotes()
            CACHE["time_slot"] = current_time_slot

        # Lấy thời tiết và màu
        colors, weather_desc, weather_icon = get_weather_theme()
        
        # Phân loại giờ (Đưa lên trước khi return)
        if 5 <= now.hour < 12: cat = "🌱 Năng lượng sáng"
        elif 12 <= now.hour < 18: cat = "💡 Góc nhìn trưa"
        else: cat = "🧠 Suy ngẫm tối"
        
        return {
            "category": f"{weather_icon} {cat} | {weather_desc}", 
            "content": random.choice(CACHE["quotes"]), 
            "bg_colors": colors,
            "icon": weather_icon
        }
    except:
        return {"category": "HỆ THỐNG", "content": "Đang kết nối...", "bg_colors": ["#374151", "#1f2937"]}

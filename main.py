from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import random

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

CACHE = {"time_slot": None, "quotes": ["Chào bạn, một ngày mới tốt lành!"]}

def get_weather_theme():
    try:
        response = requests.get("https://wttr.in/Ho_Chi_Minh?format=j1", timeout=3)
        data = response.json()
        current = data['current_condition'][0]
        code = int(current['weatherCode'])
        if code == 113: return {"desc": "☀️ Nắng", "colors": ["#f59e0b", "#d97706"]}
        elif code in [116, 119, 122]: return {"desc": "☁️ Mây", "colors": ["#475569", "#1e293b"]}
        elif code >= 176 and code <= 356: return {"desc": "🌧️ Mưa", "colors": ["#1e3a8a", "#0f172a"]}
        return {"desc": "✨ Dịu", "colors": ["#111827", "#030712"]}
    except:
        return {"desc": "🍃 Bình yên", "colors": ["#065f46", "#022c22"]}

def scrape_quotes():
    try:
        url = "https://www.thuvien-hay.com/danh-ngon-cuoc-song/"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')
        quotes = [p.text.strip() for p in soup.find_all('p') if 15 < len(p.text) < 150]
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

        # Phân loại giờ
        if 5 <= now.hour < 12: cat, keys = "🌱 Năng lượng sáng", ["mới", "sáng", "bắt đầu"]
        elif 12 <= now.hour < 18: cat, keys = "💡 Góc nhìn trưa", ["làm", "sống", "thời"]
        else: cat, keys = "🧠 Suy ngẫm tối", ["đêm", "tối", "nghỉ", "suy"]
        
        filtered = [q for q in CACHE["quotes"] if any(k in q.lower() for k in keys)]
        content = random.choice(filtered) if filtered else random.choice(CACHE["quotes"])
        weather = get_weather_theme()
        
        return {"category": f"{cat} | {weather['desc']}", "content": content, "bg_colors": weather["colors"]}
    except:
        return {"category": "HỆ THỐNG", "content": "Đang làm mới dữ liệu...", "bg_colors": ["#374151", "#1f2937"]}

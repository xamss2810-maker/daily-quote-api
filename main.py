# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests, random, pytz, os
from bs4 import BeautifulSoup
from datetime import datetime

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def scrape_and_save_quotes():
    """Cào từ nhiều nguồn và lưu vào file quotes.txt"""
    urls = [
        "https://www.thuvien-hay.com/danh-ngon-cuoc-song/",
        "https://bloganchoi.com/nhung-cau-noi-hay-ve-cuoc-song/"
    ]
    all_quotes = []
    for url in urls:
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
            soup = BeautifulSoup(response.content, 'html.parser')
            quotes = [p.text.strip() for p in soup.find_all('p') if len(p.text) > 20]
            all_quotes.extend(quotes)
        except: continue
    
    if all_quotes:
        with open("quotes.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(all_quotes))
    return all_quotes

def get_quotes_from_file():
    """Đọc câu nói từ file, nếu file trống thì cào mới"""
    if not os.path.exists("quotes.txt") or os.path.getsize("quotes.txt") == 0:
        return scrape_and_save_quotes()
    with open("quotes.txt", "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if len(line.strip()) > 20]
        return lines if lines else scrape_and_save_quotes()

def get_weather_theme(lat=None, lon=None):
    try:
        loc = f"{lat},{lon}" if (lat and lon) else "Ho_Chi_Minh"
        data = requests.get(f"https://wttr.in/{loc}?format=j1", timeout=3).json()
        code = int(data['current_condition'][0]['weatherCode'])
        if code == 113: return ["#f59e0b", "#d97706"], "Nắng", "☀️"
        elif code in [116, 119, 122]: return ["#475569", "#1e293b"], "Mây", "☁️"
        elif code >= 176 and code <= 356: return ["#1e3a8a", "#0f172a"], "Mưa", "🌧️"
        return ["#111827", "#030712"], "Dịu", "✨"
    except:
        return ["#065f46", "#022c22"], "Bình yên", "🍃"

@app.get("/quote")
def get_quote(lat: float = None, lon: float = None):
    try:
        tz = pytz.timezone('Asia/Ho_Chi_Minh')
        now = datetime.now(tz)
        
        # Lấy danh sách câu nói
        quotes = get_quotes_from_file()
        
        # Lấy thời tiết
        colors, weather_desc, weather_icon = get_weather_theme(lat, lon)
        
        cat = "🌱 Năng lượng sáng" if 5 <= now.hour < 12 else ("💡 Góc nhìn trưa" if 12 <= now.hour < 18 else "🧠 Suy ngẫm tối")
        
        return {
            "category": f"{weather_icon} {cat} | {weather_desc}", 
            "content": random.choice(quotes), 
            "bg_colors": colors,
            "icon": weather_icon
        }
    except:
        return {"category": "LỖI", "content": "Đang kết nối lại...", "bg_colors": ["#374151", "#1f2937"]}

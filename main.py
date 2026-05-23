from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Biến toàn cục để lưu cache (Giúp Widget siêu nhanh)
CACHE = {
    "date": None,
    "quotes": ["Chào bạn, một ngày mới tốt lành!"]
}

def get_weather_theme():
    """Lấy thời tiết và màu sắc Gradient"""
    try:
        response = requests.get("https://wttr.in/Ho_Chi_Minh?format=j1", timeout=5)
        data = response.json()
        current = data['current_condition'][0]
        code = int(current['weatherCode'])
        desc = current.get('lang_vnm', [{}])[0].get('value', current['weatherDesc'][0]['value'])
        
        if code == 113: return {"desc": f"☀️ {desc}", "colors": ["#f59e0b", "#d97706"]}
        if code in [116, 119, 122]: return {"desc": f"☁️ {desc}", "colors": ["#475569", "#1e293b"]}
        if code >= 176 and code <= 356: return {"desc": f"🌧️ {desc}", "colors": ["#1e3a8a", "#0f172a"]}
        return {"desc": f"✨ {desc}", "colors": ["#111827", "#030712"]}
    except:
        return {"desc": "🍃 Bình yên", "colors": ["#065f46", "#022c22"]}

def scrape_quotes():
    """Cào câu nói từ web (chỉ chạy 1 lần/ngày)"""
    try:
        url = "https://www.thuvien-hay.com/danh-ngon-cuoc-song/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        # Lọc các thẻ <p> có độ dài phù hợp, đảm bảo toàn tiếng Việt
        quotes = [p.text.strip() for p in soup.find_all('p') if 15 < len(p.text) < 150]
        return quotes if quotes else CACHE["quotes"]
    except:
        return CACHE["quotes"]

@app.get("/quote")
def get_quote():
    tz = pytz.timezone('Asia/Ho_Chi_Minh')
    now = datetime.now(tz)
    today = now.strftime("%Y-%m-%d")
    
    # Logic Cache: Nếu sang ngày mới, cào lại dữ liệu
    if CACHE["date"] != today:
        CACHE["quotes"] = scrape_quotes()
        CACHE["date"] = today
        print(f"Đã cập nhật kho câu nói cho ngày: {today}")

    # Lấy câu ngẫu nhiên từ Cache
    content = random.choice(CACHE["quotes"])
    
    # Phân loại khung giờ
    if 5 <= now.hour < 12: category = "🌱 Năng lượng sáng"
    elif 12 <= now.hour < 18: category = "💡 Góc nhìn trưa"
    else: category = "🧠 Suy ngẫm tối"
    
    weather = get_weather_theme()
    
    return {
        "category": f"{category} | {weather['desc']}",
        "content": content,
        "bg_colors": weather["colors"]
    }

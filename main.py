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

# Biến toàn cục để lưu cache
CACHE = {
    "date": None,
    "quotes": ["Chào bạn, một ngày mới tốt lành!"]
}

def get_weather_theme():
    """Lấy thời tiết, biểu tượng và màu sắc Gradient"""
    try:
        response = requests.get("https://wttr.in/Ho_Chi_Minh?format=j1", timeout=5)
        data = response.json()
        current = data['current_condition'][0]
        code = int(current['weatherCode'])
        
        # Mapping mã thời tiết sang Emoji và màu sắc
        # 113: Nắng, 116-122: Mây, 176-356: Mưa/Dông
        if code == 113: 
            return {"desc": "☀️ Nắng ráo", "colors": ["#f59e0b", "#d97706"]}
        elif code in [116, 119, 122]: 
            return {"desc": "☁️ Nhiều mây", "colors": ["#475569", "#1e293b"]}
        elif code in [143, 248, 260]: 
            return {"desc": "🌫️ Sương mù", "colors": ["#64748b", "#334155"]}
        elif code in [176, 179, 182, 185, 263, 266, 281, 284, 293, 296, 299, 302, 305, 308]: 
            return {"desc": "🌧️ Mưa nhẹ", "colors": ["#1e3a8a", "#0f172a"]}
        elif code in [311, 314, 317, 320, 353, 356, 359]: 
            return {"desc": "⛈️ Mưa lớn", "colors": ["#1e1b4b", "#020617"]}
        else: 
            return {"desc": "✨ Thời tiết đẹp", "colors": ["#111827", "#030712"]}
    except:
        return {"desc": "🍃 Dịu mát", "colors": ["#065f46", "#022c22"]}

def scrape_quotes():
    """Cào câu nói từ web"""
    try:
        url = "https://www.thuvien-hay.com/danh-ngon-cuoc-song/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        quotes = [p.text.strip() for p in soup.find_all('p') if 15 < len(p.text) < 150]
        return quotes if quotes else CACHE["quotes"]
    except:
        return CACHE["quotes"]

@app.get("/quote")
def get_quote():
    tz = pytz.timezone('Asia/Ho_Chi_Minh')
    now = datetime.now(tz)
    today = now.strftime("%Y-%m-%d")
    
    # Cập nhật cache nếu sang ngày mới
    if CACHE["date"] != today:
        CACHE["quotes"] = scrape_quotes()
        CACHE["date"] = today
        print(f"Đã cập nhật kho câu nói cho ngày: {today}")

    # Lọc câu nói theo khung giờ
    all_quotes = CACHE["quotes"]
    
    if 5 <= now.hour < 12:
        category = "🌱 Năng lượng sáng"
        # Ưu tiên các câu có từ khóa tích cực buổi sáng
        morning_keys = ["ngày", "mới", "bắt đầu", "sáng", "vui"]
        filtered = [q for q in all_quotes if any(k in q.lower() for k in morning_keys)]
        content = random.choice(filtered) if filtered else random.choice(all_quotes)
        
    elif 12 <= now.hour < 18:
        category = "💡 Góc nhìn trưa"
        # Ưu tiên câu về làm việc, cuộc sống
        noon_keys = ["làm", "việc", "cuộc", "sống", "thời", "gian"]
        filtered = [q for q in all_quotes if any(k in q.lower() for k in noon_keys)]
        content = random.choice(filtered) if filtered else random.choice(all_quotes)
        
    else: # Tối
        category = "🧠 Suy ngẫm tối"
        # Ưu tiên câu về tâm hồn, nghỉ ngơi
        night_keys = ["tâm", "hồn", "nghỉ", "đêm", "tối", "suy", "nghĩ"]
        filtered = [q for q in all_quotes if any(k in q.lower() for k in night_keys)]
        content = random.choice(filtered) if filtered else random.choice(all_quotes)
    
    weather = get_weather_theme()
    
    return {
        "category": f"{category} | {weather['desc']}",
        "content": content,
        "bg_colors": weather["colors"]
    }

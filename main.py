from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import random

app = FastAPI()

# Biến toàn cục để lưu cache
CACHE = {
    "date": None,
    "quotes": ["Hãy tận hưởng ngày mới tuyệt vời!"]
}

def scrape_quotes():
    """Chỉ cào khi cần thiết"""
    try:
        url = "https://www.thuvien-hay.com/danh-ngon-cuoc-song/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        # Lọc câu tiếng Việt dài trên 15 ký tự
        quotes = [p.text.strip() for p in soup.find_all('p') if len(p.text) > 15]
        return quotes if quotes else CACHE["quotes"]
    except:
        return CACHE["quotes"]

@app.get("/quote")
def get_quote():
    tz = pytz.timezone('Asia/Ho_Chi_Minh')
    now = datetime.now(tz)
    today = now.strftime("%Y-%m-%d")
    
    # LOGIC CACHE: Nếu là ngày mới, cào lại dữ liệu
    if CACHE["date"] != today:
        CACHE["quotes"] = scrape_quotes()
        CACHE["date"] = today
        print(f"Đã cập nhật cache cho ngày: {today}")

    # Lấy câu nói từ cache (cực nhanh vì đã nằm trong RAM)
    content = random.choice(CACHE["quotes"])
    
    # Phân loại theo giờ
    if 5 <= now.hour < 12: category = "🌱 Năng lượng"
    elif 12 <= now.hour < 18: category = "💡 Góc nhìn"
    else: category = "🧠 Suy ngẫm"
    
    # Thời tiết (giữ nguyên hàm get_weather_theme)
    weather = get_weather_theme()
    
    return {
        "category": f"{category} | {weather['desc']}",
        "content": content,
        "bg_colors": weather["colors"]
    }

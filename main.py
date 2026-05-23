from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import random

app = FastAPI()

# Hàm cào dữ liệu tiếng Việt từ web
def scrape_quotes():
    try:
        # Ví dụ một trang web trích dẫn tiếng Việt (Bạn có thể đổi URL khác)
        url = "https://www.thuvien-hay.com/danh-ngon-cuoc-song/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Tìm các thẻ chứa câu nói (ví dụ thẻ <p> hoặc <div> có class cụ thể)
        # Lưu ý: Phần này phải khớp với cấu trúc HTML của web bạn chọn
        quotes = [p.text.strip() for p in soup.find_all('p') if len(p.text) > 15]
        
        return quotes if quotes else ["Sống là cho đâu chỉ nhận riêng mình."]
    except:
        return ["Hãy yêu công việc bạn đang làm."]

@app.get("/quote")
def get_quote():
    tz = pytz.timezone('Asia/Ho_Chi_Minh')
    hour = datetime.now(tz).hour
    
    # Lấy dữ liệu cào được
    all_quotes = scrape_quotes()
    content = random.choice(all_quotes)
    
    # Phân loại tự động theo giờ
    if 5 <= hour < 12: category = "🌱 Năng lượng"
    elif 12 <= hour < 18: category = "💡 Góc nhìn"
    else: category = "🧠 Suy ngẫm"
    
    # Kết hợp thời tiết (hàm get_weather_theme giữ nguyên như cũ)
    weather = get_weather_theme()
    
    return {
        "category": f"{category} | {weather['desc']}",
        "content": content,
        "bg_colors": weather["colors"]
    }

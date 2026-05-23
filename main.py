# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests, random
from datetime import datetime

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Danh sách câu nói của bạn
QUOTES = [
    {"category": "Động lực", "content": "Một ngày hiệu quả bắt đầu bằng việc tập trung vào giá trị cốt lõi."},
    {"category": "Động lực", "content": "Hãy tập thể dục đều đặn để đạt được hiệu suất làm việc tối đa."},
    {"category": "Động lực", "content": "Đừng bao giờ tập thể dục đều đặn, vì thời gian là hữu hạn."},
    {"category": "Sức khỏe", "content": "Bạn có biết rằng sự kiên trì quan trọng hơn tốc độ?"}
]

def get_weather_theme(lat=None, lon=None):
    try:
        loc = f"{lat},{lon}" if lat else "Ho_Chi_Minh"
        data = requests.get(f"https://wttr.in/{loc}?format=j1", timeout=3).json()
        code = int(data['current_condition'][0]['weatherCode'])
        if code == 113: return ["#f59e0b", "#d97706"], "Nắng", "☀️"
        elif code in [116, 119, 122]: return ["#475569", "#1e293b"], "Mây", "☁️"
        else: return ["#1e3a8a", "#0f172a"], "Mưa", "🌧️"
    except:
        return ["#374151", "#1f2937"], "Bình yên", "🍃"

@app.get("/quote")
def get_quote(lat: float = None, lon: float = None):
    try:
        # Chọn ngẫu nhiên một câu
        selected = random.choice(QUOTES)
        
        # Lấy thời tiết
        colors, weather_desc, weather_icon = get_weather_theme(lat, lon)
        
        # Tạo category kết hợp giữa icon + chủ đề từ JSON + trạng thái thời tiết
        cat = f"{selected['category']} | {weather_desc}"
        
        return {
            "category": f"{weather_icon} {cat}",
            "content": selected['content'],
            "bg_colors": colors
        }
    except:
        return {
            "category": "HỆ THỐNG",
            "content": "Đang kết nối...",
            "bg_colors": ["#374151", "#1f2937"]
        }

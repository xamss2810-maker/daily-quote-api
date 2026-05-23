from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_QUOTES = [
    {"category": "💡 Mẹo Hay", "content": "Áp dụng quy tắc 2 phút: Nếu việc gì đó mất chưa đầy 2 phút để hoàn thành, hãy làm nó ngay lập tức."},
    {"category": "🌱 Động Lực", "content": "Hành trình vạn dặm khởi đầu từ một bước chân. Đừng nhìn vào đỉnh núi, hãy nhìn vào bước tiếp theo."},
    {"category": "🧠 Triết Lý", "content": "Chúng ta không thể chọn nơi mình sinh ra, nhưng có thể chọn cách mình đối mặt với nghịch cảnh."},
    {"category": "🎯 Tập Trung", "content": "Tắt thông báo mạng xã hội trong 2 tiếng tới. Sự tập trung sâu sẽ tạo nên sự khác biệt."}
]

def get_weather_theme():
    """Gọi API thời tiết công cộng để lấy trạng thái thời tiết thực tế"""
    try:
        # Lấy thời tiết tại TP.HCM/Việt Nam qua API công cộng (không cần API Key)
        response = requests.get("https://wttr.in/Ho_Chi_Minh?format=j1", timeout=5)
        data = response.json()
        current_condition = data['current_condition'][0]
        weather_code = int(current_condition['weatherCode'])
        weather_desc = current_condition['lang_vnm'][0]['value'] if 'lang_vnm' in current_condition else current_condition['weatherDesc'][0]['value']
        
        # Thiết lập các bảng màu Gradient thời thượng [Màu_Bắt_Đầu, Màu_Kết_Thúc]
        if weather_code in [113]:  # Trời nắng / Trời quang
            return {"desc": f"☀️ {weather_desc}", "colors": ["#f59e0b", "#d97706"]} # Gradient Cam Vàng rực rỡ
        elif weather_code in [116, 119, 122]:  # Nhiều mây / Có mây
            return {"desc": f"☁️ {weather_desc}", "colors": ["#475569", "#1e293b"]} # Gradient Xám Xanh thanh lịch
        elif weather_code in [176, 263, 266, 293, 296, 302, 353, 356]:  # Mưa rào / Mưa nhỏ
            return {"desc": f"🌧️ {weather_desc}", "colors": ["#1e3a8a", "#0f172a"]} # Gradient Xanh Dương Đậm dịu mát
        elif weather_code in [386, 389]:  # Có dông sét
            return {"desc": f"⛈️ {weather_desc}", "colors": ["#581c87", "#2e1065"]} # Gradient Tím Đậm huyền bí
        else:
            return {"desc": f"✨ {weather_desc}", "colors": ["#111827", "#030712"]} # Mặc định ban đêm/trời mát màu tối
    except Exception:
        # Phương án dự phòng nếu API thời tiết bị lỗi
        return {"desc": "🍃 Bình yên", "colors": ["#065f46", "#022c22"]} # Màu Xanh Lá Đậm mát mẻ

@app.get("/quote")
def get_quote():
    quote = random.choice(DATA_QUOTES)
    weather = get_weather_theme()
    
    return {
        "category": f"{quote['category']}  |  {weather['desc']}",
        "content": quote["content"],
        "bg_colors": weather["colors"] # Trả về mảng 2 màu để làm nền Gradient
    }

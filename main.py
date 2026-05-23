from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random

app = FastAPI()

# Mở CORS để iPhone (Scriptable) gọi vào không bị lỗi bảo mật
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_QUOTES = [
    {
        "category": "💡 Mẹo Hay",
        "content": "Áp dụng quy tắc 2 phút: Nếu việc gì đó mất chưa đầy 2 phút để hoàn thành, hãy làm nó ngay lập tức.",
        "bg_color": "#1e293b"
    },
    {
        "category": "🌱 Động Lực",
        "content": "Hành trình vạn dặm khởi đầu từ một bước chân. Đừng nhìn vào đỉnh núi, hãy nhìn vào bước tiếp theo.",
        "bg_color": "#065f46"
    },
    {
        "category": "🧠 Triết Lý",
        "content": "Chúng ta không thể chọn nơi mình sinh ra, nhưng có thể chọn cách mình đối mặt với nghịch cảnh.",
        "bg_color": "#701a75"
    }
]

@app.get("/quote")
def get_quote():
    return random.choice(DATA_QUOTES)
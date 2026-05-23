# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests, random, pytz, os, re
import google.generativeai as genai
from bs4 import BeautifulSoup
from datetime import datetime

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Cấu hình AI (Bạn thay API_KEY vào đây)
genai.configure(api_key="AIzaSyAXog4Xymr1Wb3AeSZ8SogmuNpujG4o5F0")

def is_quality_quote(text):
    """AI kiểm duyệt: Chỉ giữ lại danh ngôn sâu sắc, tích cực"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Đây có phải là một câu danh ngôn cuộc sống sâu sắc, truyền cảm hứng và tích cực không? Chỉ trả về YES hoặc NO: '{text}'"
        return "YES" in model.generate_content(prompt).text.upper()
    except: return True

def clean_text(text):
    text = re.sub(r'\((Ảnh|Hình|Nguồn):.*?\)', '', text, flags=re.IGNORECASE)
    return text.strip()

def scrape_and_save_quotes():
    """Cào, Lọc AI và lưu vào quotes.txt"""
    urls = ["https://www.thuvien-hay.com/danh-ngon-cuoc-song/", "https://bloganchoi.com/nhung-cau-noi-hay-ve-cuoc-song/"]
    valid_quotes = []
    for url in urls:
        try:
            soup = BeautifulSoup(requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5).content, 'html.parser')
            for p in soup.find_all('p'):
                clean = clean_text(p.text)
                if len(clean) > 20 and is_quality_quote(clean):
                    valid_quotes.append(clean)
        except: continue
    
    with open("quotes.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(valid_quotes))
    return valid_quotes

@app.get("/quote")
def get_quote(lat: float = None, lon: float = None):
    try:
        # Đọc file
        if not os.path.exists("quotes.txt") or os.path.getsize("quotes.txt") == 0:
            quotes = scrape_and_save_quotes()
        else:
            with open("quotes.txt", "r", encoding="utf-8") as f:
                quotes = [line.strip() for line in f.readlines()]
        
        # Lấy thời tiết
        loc = f"{lat},{lon}" if lat else "Ho_Chi_Minh"
        data = requests.get(f"https://wttr.in/{loc}?format=j1", timeout=3).json()
        code = int(data['current_condition'][0]['weatherCode'])
        
        if code == 113: theme = (["#f59e0b", "#d97706"], "Nắng", "☀️")
        elif code in [116, 119, 122]: theme = (["#475569", "#1e293b"], "Mây", "☁️")
        else: theme = (["#1e3a8a", "#0f172a"], "Mưa", "🌧️")
        
        cat = "🌱 Năng lượng sáng" if 5 <= datetime.now().hour < 12 else "💡 Góc nhìn trưa"
        
        return {"category": f"{theme[2]} {cat} | {theme[1]}", "content": random.choice(quotes), "bg_colors": theme[0]}
    except:
        return {"category": "LỖI", "content": "Đang làm mới dữ liệu...", "bg_colors": ["#374151", "#1f2937"]}

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import json
import os
import re

app = FastAPI(title="Wellbeing AI Coach API")

# --- THÊM CORS MIDDLEWARE ---
# Cho phép App Android hoặc Frontend Web gọi API mà không bị lỗi Cross-Origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong môi trường production, anh có thể đổi thành domain cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Cấu hình API và Model ở global scope để tối ưu hiệu năng
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# Chỉ định thẳng model flash để tối ưu tốc độ response
MODEL_NAME = "gemini-1.5-flash"

# 2. Bộ lọc từ khóa y tế/nhạy cảm
MEDICAL_KEYWORDS = [
    r"trầm cảm", r"tự tử", r"ung thư", r"thuốc", r"đau ngực",
    r"chóng mặt", r"khó thở", r"tuyệt vọng", r"tự hại", r"đi viện", r"bác sĩ"
]
MEDICAL_REGEX = re.compile("|".join(MEDICAL_KEYWORDS), re.IGNORECASE)

DISCLAIMER_TEXT = (
    "⚠️ AI Coach nhận thấy bạn đang có các biểu hiện về sức khỏe/tâm lý cần lưu tâm. "
    "Những phân tích trên chỉ là hỗ trợ xây dựng thói quen, KHÔNG phải chẩn đoán y tế. "
    "Vui lòng ưu tiên tham khảo ý kiến bác sĩ chuyên khoa."
)

class WeeklyData(BaseModel):
    user_id: int
    logs: list[dict]

@app.post("/api/ai/coach/analyze")
async def analyze_week(data: WeeklyData):
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY chưa được cấu hình trong biến môi trường."
        )

    # Chuyển logs thành chuỗi để quét từ khóa nhạy cảm
    logs_str = json.dumps(data.logs, ensure_ascii=False)
    needs_medical_disclaimer = bool(MEDICAL_REGEX.search(logs_str))

    # Đã chỉnh lại thụt lề cho chuẩn Python Multi-line String
    prompt = f"""
    Bạn là một AI Coach hỗ trợ xây dựng thói quen và wellbeing. 
    NGUYÊN TẮC TỐI THƯỢNG: 
    1. Bạn KHÔNG PHẢI là bác sĩ hay chuyên gia tâm lý. 
    2. TUYỆT ĐỐI KHÔNG đưa ra bất kỳ chẩn đoán y tế, bệnh lý tâm thần hay khuyên dùng thuốc.
    3. Chỉ tập trung vào việc thay đổi thói quen nhỏ, quản lý thời gian và các hành động xoa dịu an toàn.

    Dựa vào dữ liệu sau, hãy trả về một object JSON đúng định dạng:
    {{
        "summary": "Tóm tắt nhẹ nhàng, khích lệ",
        "negative_patterns": ["Thói quen xấu 1", "Thói quen xấu 2"],
        "small_goals": ["Mục tiêu nhỏ 1"],
        "safe_actions": ["Hành động an toàn 1 (vd: thiền 5 phút)"]
    }}

    Dữ liệu tuần:
    {logs_str}
    """

    try:
        model = genai.GenerativeModel(MODEL_NAME)

        # Gọi AI sinh nội dung chuẩn JSON
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )

        # Parse JSON từ AI
        result_json = json.loads(response.text)

        # 3. Tiêm thêm trường disclaimer vào JSON nếu phát hiện từ khóa y tế
        if needs_medical_disclaimer:
            result_json["disclaimer"] = DISCLAIMER_TEXT
        else:
            result_json["disclaimer"] = None

        return result_json

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Lỗi: AI không trả về đúng định dạng JSON.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống AI: {str(e)}")
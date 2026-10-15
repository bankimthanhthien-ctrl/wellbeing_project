from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import json
import os

app = FastAPI()

# Đọc API Key một cách an toàn từ biến môi trường của hệ thống
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)


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
    {json.dumps(data.logs, ensure_ascii=False)}
    """

    try:
        # Tự động quét và tìm model hỗ trợ 'generateContent' đầu tiên trong tài khoản
        available_model = None
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_model = m.name
                break

        if not available_model:
            raise Exception("Không tìm thấy model Gemini nào hỗ trợ generateContent trên API Key này.")

        # Khởi tạo model tự động tìm được
        model = genai.GenerativeModel(available_model)

        # Gọi AI sinh nội dung (yêu cầu đầu ra dạng text JSON)
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
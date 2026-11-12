import os
from google import genai


def analyze_user_logs(logs_data):
    # Lấy API Key từ biến môi trường trên Render
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"summary": "Lỗi: Chưa cấu hình GEMINI_API_KEY trên Render.", "negative_patterns": [], "small_goals": [],
                "safe_actions": [], "disclaimer": ""}

    client = genai.Client(api_key=api_key)

    # Gom nội dung nhật ký 7 ngày lại để gửi cho AI
    logs_text = "\n".join(
        [f"Ngày {l['date']} - Cảm xúc: {l['mood']} - Ngủ: {l['sleep_hours']}h - Nhật ký: {l['content']}" for l in
         logs_data])

    prompt = f"""
    Bạn là AI Wellbeing Coach chuyên gia tâm lý và sức khỏe tinh thần. Hãy phân tích 7 ngày nhật ký sau đây của người dùng và trả về kết quả dưới dạng JSON thuần túy (không kèm markdown như ```json) với các trường sau:
    - summary: Tóm tắt ngắn gọn tâm trạng và xu hướng tuần qua.
    - negative_patterns: Danh sách các pattern tiêu cực hoặc thói quen xấu (nếu có).
    - small_goals: Danh sách 2-3 mục tiêu nhỏ thực tế cho tuần tới.
    - safe_actions: Danh sách hành động xoa dịu tinh thần an toàn.
    - disclaimer: Cảnh báo y tế nếu phát hiện từ khóa nguy hiểm (ví dụ đau ngực, khó thở, tự hại), ngược lại để trống.

    Dữ liệu nhật ký:
    {logs_text}
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',  # Hoặc model anh đang dùng
            contents=prompt,
        )

        import json
        # Parse chuỗi JSON do AI trả về
        raw_text = response.text.strip().replace("```json", "").replace("```", "")
        data = json.loads(raw_text)
        return data
    except Exception as e:
        return {
            "summary": f"AI đang bận hoặc lỗi phân tích: {str(e)}",
            "negative_patterns": [],
            "small_goals": [],
            "safe_actions": [],
            "disclaimer": ""
        }
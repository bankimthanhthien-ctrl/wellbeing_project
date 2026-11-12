import os
import requests
from datetime import date
from .models import DailyLog, AIWeeklyReport


def process_weekly_coach():
    # Lấy danh sách tất cả các user có log trong hệ thống
    users = DailyLog.objects.values_list('user', flat=True).distinct()

    # Địa chỉ API FastAPI (nếu chạy local là http://127.0.0.1:8000/api/ai/coach/analyze, trên Render là link service FastAPI của anh)
    fastapi_url = os.getenv('FASTAPI_URL', 'http://127.0.0.1:8000/api/ai/coach/analyze')

    for user_id in users:
        # Lấy 7 ngày log gần nhất của user
        logs = DailyLog.objects.filter(user_id=user_id).order_by('-date')[:7]
        if not logs:
            continue

        # Chuẩn bị dữ liệu JSON gửi sang FastAPI giống hệt cấu trúc FastAPI yêu cầu
        payload_logs = [
            {
                "date": log.date.strftime("%Y-%m-%d"),
                "mood": log.mood,
                "sleep_hours": float(log.sleep_hours),
                "content": log.journal
            }
            for log in logs
        ]

        payload = {
            "user_id": str(user_id),
            "logs": payload_logs
        }

        try:
            # Gửi request POST sang FastAPI
            response = requests.post(fastapi_url, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()

                # Lưu kết quả trả về từ AI vào bảng AIWeeklyReport trong database
                AIWeeklyReport.objects.create(
                    user_id=user_id,
                    week_start_date=logs.last().date,  # Ngày bắt đầu của tuần
                    summary=data.get("summary", ""),
                    negative_patterns=data.get("negative_patterns", []),
                    small_goals=data.get("small_goals", []),
                    safe_actions=data.get("safe_actions", []),
                    disclaimer=data.get("disclaimer", "")
                )
                print(f"✅ Đã lưu kết quả AI thành công cho user ID: {user_id}")
            else:
                print(f"❌ Lỗi từ FastAPI: {response.text}")
        except Exception as e:
            print(f"❌ Không thể kết nối tới FastAPI service: {e}")
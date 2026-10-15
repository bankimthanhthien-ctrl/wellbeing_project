import os
import requests
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from tracker.models import DailyLog, AIWeeklyReport


def generate_all_weekly_reports():
    print("🔄 Bắt đầu tiến trình gom dữ liệu và gọi AI Coach...")

    # URL của FastAPI (đang chạy ở port 8000)
    fastapi_host = os.environ.get('FASTAPI_HOSTPORT', 'localhost:8000')
    url = f"http://{fastapi_host}/api/ai/coach/analyze"

    # Lấy ngày hiện tại và 6 ngày trước đó (tổng 7 ngày)
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=6)

    users = User.objects.all()
    for user in users:
        # 1. Lấy dữ liệu nhật ký của user trong 7 ngày
        logs_qs = DailyLog.objects.filter(user=user, date__range=[start_date, end_date])

        if not logs_qs.exists():
            print(f"⏩ User {user.username} không có dữ liệu tuần này. Bỏ qua.")
            continue

        # 2. Chuyển đổi dữ liệu thành dạng danh sách (List of Dictionaries) để gửi JSON
        logs_list = list(logs_qs.values('date', 'mood', 'sleep_hours', 'journal'))
        for log in logs_list:
            log['date'] = str(log['date'])  # Ép kiểu ngày thành chữ để không bị lỗi JSON

        payload = {
            "user_id": user.id,
            "logs": logs_list
        }

        try:
            print(f"🚀 Đang gửi dữ liệu của {user.username} cho AI xử lý...")
            response = requests.post(url, json=payload)

            if response.status_code == 200:
                ai_data = response.json()

                # 3. Lưu kết quả trả về từ AI vào Database
                AIWeeklyReport.objects.create(
                    user=user,
                    week_start_date=start_date,
                    summary=ai_data.get('summary', ''),
                    negative_patterns=ai_data.get('negative_patterns', []),
                    small_goals=ai_data.get('small_goals', []),
                    safe_actions=ai_data.get('safe_actions', [])
                )
                print(f"✅ Đã lưu báo cáo AI cho user {user.username} thành công!")
            else:
                print(f"❌ Lỗi từ FastAPI: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"⚠️ Không thể kết nối tới FastAPI: {e}")
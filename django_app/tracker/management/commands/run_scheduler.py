from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tracker.models import DailyLog, AIWeeklyReport
import requests
from datetime import date


class Command(BaseCommand):
    help = 'Chạy tiến trình AI Scheduler tự động cho tất cả user'

    def handle(self, *args, **options):
        self.stdout.write("Đang khởi động APScheduler...")


        users = User.objects.all()

        if not users.exists():
            self.stdout.write("Không tìm thấy user nào có dữ liệu nhật ký.")
            return

        for user in users:
            self.stdout.write(f"🔄 Đang xử lý dữ liệu cho user: {user.username}...")

            # Lấy dữ liệu nhật ký của user hiện tại (7 ngày gần nhất)
            logs = DailyLog.objects.filter(user=user).order_by('-date')[:7]

            if not logs.exists():
                continue

            # Chuyển đổi dữ liệu sang dạng dict để gửi qua FastAPI
            logs_data = [
                {
                    "date": str(log.date),
                    "mood": log.mood,
                    "sleep_hours": float(log.sleep_hours),
                    "journal": log.journal
                }
                for log in logs
            ]

            try:
                # Gửi yêu cầu sang FastAPI phân tích
                response = requests.post(
                    "http://127.0.0.1:8000/api/ai/coach/analyze",
                    json={
                        "user_id": user.id,
                        "logs": logs_data}
                )

                if response.status_code == 200:
                    ai_result = response.json()

                    # Lưu hoặc cập nhật báo cáo AI gắn đúng với user đó vào database
                    AIWeeklyReport.objects.update_or_create(
                        user=user,
                        defaults={
                            'week_start_date': date.today(),
                            'summary': ai_result.get("summary", ""),
                            'negative_patterns': ai_result.get("negative_patterns", []),
                            'small_goals': ai_result.get("small_goals", []),
                            'safe_actions': ai_result.get("safe_actions", [])
                        }
                    )
                    self.stdout.write(f"✅ Đã lưu báo cáo AI cho user {user.username} thành công!")
                else:
                    self.stdout.write(
                        f"❌ Lỗi từ FastAPI cho user {user.username}: {response.status_code} - {response.text}")

            except Exception as e:
                self.stdout.write(f"❌ Lỗi khi xử lý cho user {user.username}: {str(e)}")
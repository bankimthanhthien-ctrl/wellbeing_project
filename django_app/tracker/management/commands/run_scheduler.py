from django.core.management.base import BaseCommand
from django.contrib.auth.models import User  # Import model User của Django
from tracker.models import DailyLog, AIWeeklyReport


# ... các import gọi API sang FastAPI khác của bạn ...

class Command(BaseCommand):
    help = 'Chạy tiến trình AI Scheduler tự động cho tất cả user'

    def handle(self, *args, **options):
        self.stdout.write("Đang khởi động APScheduler...")

        # Lấy tất cả các user đang có trong hệ thống (hoặc lọc user có DailyLog)
        users = User.objects.filter(dailylog__isnull=False).distinct()

        if not users.exists():
            self.stdout.write("Không tìm thấy user nào có dữ liệu nhật ký.")
            return

        for user in users:
            self.stdout.write(f"🔄 Đang xử lý dữ liệu cho user: {user.username}...")

            # Lấy dữ liệu nhật ký của user hiện tại
            logs = DailyLog.objects.filter(user=user).order_by('-date')[:7]

            if not logs.exists():
                continue

            # Chuyển đổi dữ liệu sang dạng dict để gửi qua FastAPI
            logs_data = [
                {
                    "date": str(log.date),
                    "mood": log.mood,
                    "sleep_hours": log.sleep_hours,
                    "journal": log.journal
                }
                for log in logs
            ]

            try:
                # Gọi API FastAPI phân tích (ví dụ qua requests)
                # response = requests.post("http://127.0.0.1:8000/api/ai/coach/analyze", json={"user_id": user.id, "logs": logs_data})

                # Sau khi có kết quả trả về từ AI, lưu báo cáo gắn đúng với user đó:
                # AIWeeklyReport.objects.create(user=user, summary=result['summary'], ...)

                self.stdout.write(f"✅ Đã lưu báo cáo AI cho user {user.username} thành công!")
            except Exception as e:
                self.stdout.write(f"❌ Lỗi khi xử lý cho user {user.username}: {str(e)}")
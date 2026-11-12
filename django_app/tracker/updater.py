from .models import DailyLog, AIWeeklyReport
from .ai_service import analyze_user_logs


def process_weekly_coach():
    users = DailyLog.objects.values_list('user', flat=True).distinct()

    for user_id in users:
        # Chuyển QuerySet thành list Python bằng cách dùng list() sau khi slice
        logs_queryset = DailyLog.objects.filter(user_id=user_id).order_by('-date')[:7]
        logs = list(logs_queryset)

        if not logs:
            continue

        payload_logs = [
            {
                "date": log.date.strftime("%Y-%m-%d"),
                "mood": log.mood,
                "sleep_hours": float(log.sleep_hours),
                "content": log.journal
            }
            for log in logs
        ]

        try:
            # Gọi trực tiếp hàm Python xử lý AI không cần qua FastAPI
            data = analyze_user_logs(payload_logs)

            # Vì logs đã là list Python, logs[-1] chính là phần tử cuối cùng (cũ nhất trong tuần)
            week_start = logs[-1].date

            # Lưu kết quả vào cơ sở dữ liệu (NeonDB)
            AIWeeklyReport.objects.create(
                user_id=user_id,
                week_start_date=week_start,
                summary=data.get("summary", ""),
                negative_patterns=data.get("negative_patterns", []),
                small_goals=data.get("small_goals", []),
                safe_actions=data.get("safe_actions", []),
                disclaimer=data.get("disclaimer", "")
            )
            print(f"✅ Đã lưu kết quả AI thành công cho user ID: {user_id}")
        except Exception as e:
            print(f"❌ Lỗi xử lý AI: {e}")
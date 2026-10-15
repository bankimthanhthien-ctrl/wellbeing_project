from django.core.management.base import BaseCommand
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from django_apscheduler.jobstores import DjangoJobStore
from tracker.tasks import generate_all_weekly_reports

class Command(BaseCommand):
    help = "Chạy APScheduler để tự động gọi AI Coach"

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone="Asia/Ho_Chi_Minh")
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # ---------------------------------------------------------
        # MÔI TRƯỜNG TEST: Chạy lặp lại mỗi 1 phút để test ngay lập tức
        # ---------------------------------------------------------
        scheduler.add_job(
            generate_all_weekly_reports,
            trigger=IntervalTrigger(minutes=1),
            id="test_weekly_ai_report",
            max_instances=1,
            replace_existing=True,
        )

        # ---------------------------------------------------------
        # MÔI TRƯỜNG THẬT: Bỏ comment đoạn dưới để chạy 20:00 Chủ Nhật
        # ---------------------------------------------------------
        # scheduler.add_job(
        #     generate_all_weekly_reports,
        #     trigger=CronTrigger(day_of_week="sun", hour="20", minute="00"),
        #     id="production_weekly_ai_report",
        #     max_instances=1,
        #     replace_existing=True,
        # )

        try:
            self.stdout.write("Đang khởi động APScheduler...")
            self.stdout.write("Chế độ test đang bật: Tác vụ gọi AI sẽ chạy mỗi 1 phút.")
            scheduler.start()
        except KeyboardInterrupt:
            self.stdout.write("Đã dừng APScheduler.")
            scheduler.shutdown()
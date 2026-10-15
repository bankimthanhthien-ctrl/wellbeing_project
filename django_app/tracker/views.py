from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import DailyLog, AIWeeklyReport
from .forms import DailyLogForm
from django.shortcuts import get_object_or_404


@login_required(login_url='/admin/login/')
def edit_log(request, pk):
    log = get_object_or_404(DailyLog, pk=pk, user=request.user)
    if request.method == 'POST':
        form = DailyLogForm(request.POST, instance=log)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật nhật ký thành công!')
            return redirect('dashboard')
    else:
        form = DailyLogForm(instance=log)

    return render(request, 'tracker/edit_log.html', {'form': form, 'log': log})


def dashboard(request):
    if request.method == 'POST':
        # Kiểm tra nếu chưa đăng nhập mà cố submit form
        if not request.user.is_authenticated:
            return redirect('/admin/login/')

        form = DailyLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            # Xử lý lỗi trùng ngày
            if DailyLog.objects.filter(user=request.user, date=log.date).exists():
                messages.error(request, 'Bạn đã nhập nhật ký cho ngày này rồi!')
            else:
                log.save()
                messages.success(request, 'Đã lưu nhật ký thành công!')
                return redirect('dashboard')
    else:
        form = DailyLogForm()

    # Chỉ truy vấn dữ liệu khi người dùng đã đăng nhập để tránh lỗi AnonymousUser
    if request.user.is_authenticated:
        recent_logs = DailyLog.objects.filter(user=request.user).order_by('-date')[:7]
        latest_report = AIWeeklyReport.objects.filter(user=request.user).order_by('-created_at').first()
    else:
        recent_logs = []
        latest_report = None

    context = {
        'form': form,
        'recent_logs': recent_logs,
        'latest_report': latest_report,
    }
    return render(request, 'tracker/dashboard.html', context)
# views.py
from django.shortcuts import render
from django.db.models import Count, Sum
from .models import ProjectMaster, JobMaster, CampMaster, ManningReport, WorkOrder

def dashboard(request):
    projects = ProjectMaster.objects.all()
    jobs = JobMaster.objects.all()
    camps = CampMaster.objects.all()

    manning_reports = ManningReport.objects.all()
    work_orders = WorkOrder.objects.all()

    context = {
        'projects': projects,
        'jobs': jobs,
        'camps': camps,
        'manning_reports': manning_reports,
        'work_orders': work_orders,
    }
    return render(request, 'dashboard.html', context)

def manning_summary(request):
    if request.method == 'POST':
        project_ids = request.POST.getlist('projects')
        job_ids = request.POST.getlist('jobs')

        manning_reports = ManningReport.objects.filter(ProjectName__in=project_ids, JobName__in=job_ids)
        context = {
            'manning_reports': manning_reports,
        }
        return render(request, 'manning_summary.html', context)
    return render(request, 'manning_summary.html')

def work_order_summary(request):
    if request.method == 'POST':
        camp_ids = request.POST.getlist('camps')
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')

        work_orders = WorkOrder.objects.filter(CampId__in=camp_ids, Date__range=[from_date, to_date])
        context = {
            'work_orders': work_orders,
        }
        return render(request, 'work_order_summary.html', context)
    return render(request, 'work_order_summary.html')

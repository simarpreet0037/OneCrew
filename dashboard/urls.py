# dashboard/urls.py
from django.urls import path
from .views import (LoginView, DashboardView, WorkOrderReportView, RecruitmentView)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('', DashboardView.as_view(), name='dashboard'),
    path('work-order/', WorkOrderReportView.as_view(), name='work-order'),
    path('job-master/', RecruitmentView.as_view(), name='job-master'),
]

from django.urls import path
from .views import (LoginView, LogoutView, DashboardView, ManageEmployeeView,
                         RecruitmentSummaryView, ExportRecruitmentSummary,
                       ViewEmployeeDetails, EditEmployeeDetails, UpdateEmployeeDetails)

from .views import (create_job, create_project, job_master, worker_work_orders, signup_view, InitiateWorkOrderView,
                         employee_profile_view)
from . import views


from .views import (DashboardView,AllWorkOrderView)
from.models import get_latest_work_order

urlpatterns = [
    
    #complted end points

    path('login/', LoginView.as_view(), name='login'),              #for login
    path('logout/', LogoutView.as_view(), name='logout'),           #for logout
    path("signup/", signup_view, name="signup"),                    #for signup

    
    path('', DashboardView.as_view(), name='dashboard'),
    path('ajax/get-latest-work-order/', get_latest_work_order, name='get_latest_work_order'),
    
    
    path('job-master/', job_master, name='job_master'),             #for job master  
    path('create-project/', create_project, name='create_project'), #for create project
    path('create-job/', create_job, name='create_job'),             #for create job
    path('workorder/initiate/<int:job_id>/', InitiateWorkOrderView.as_view(), name='initiate_work_order'), #for initiate work order

    
    path('manage-employee', ManageEmployeeView.as_view(), name='manage-employee'),
    path('employee/<int:employee_id>/view/', ViewEmployeeDetails.as_view(), name='view-employee'),
    path('employee/<int:employee_id>/edit/', EditEmployeeDetails.as_view(), name='edit-employee'),
    path('employee/<int:employee_id>/update/', UpdateEmployeeDetails.as_view(), name='update-employee'),
   
    path('recruitment-summary', RecruitmentSummaryView.as_view(), name='recruitment-summary'),
    path('export-recruitment-summary', ExportRecruitmentSummary.as_view(), name='export-recruitment-summary'),

    path('workorder-list/', AllWorkOrderView.as_view(), name='workorder-list'),
    path('edit_or_complete_work_order_admin/<int:wo_id>/', views.complete_or_edit_work_order_admin, name='edit_or_complete_work_order_admin'),
   


    path('workorder/worker/', worker_work_orders, name='worker_work_orders'),
    path('work-order/', worker_work_orders, name='work-order'),

    path('edit_or_complete_work_order/<int:wo_id>/', views.edit_or_complete_work_order, name='edit_or_complete_work_order'),
    
    path('profile/', employee_profile_view, name='employee-profile'),


 

]
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse, HttpResponse
from datetime import datetime, timedelta
from django.views import View
from django.db import models
from django.views.decorators.http import require_http_methods
from dashboard.models import User, JobMaster, ProjectMaster, Employee, NewHire, WorkOrder
from dashboard.forms import EmployeeUploadForm, EmployeeProfileForm
from openpyxl import Workbook
import pandas as pd
import io
import xlsxwriter
import datetime
import random
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
import json
from datetime import date
from decimal import Decimal
from django.contrib.auth.decorators import login_required


#---LOginView---Works---
class LoginView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, 'signin.html')

    def post(self, request, *args, **kwargs):
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        # Authenticate user
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid email or password.")
        return render(request, 'signin.html') 
    

#--LogoutView---Works---
class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
        return redirect('login')


#------signup view ------works------
from .forms import SignupForm
from .models import Employee, EmployeeFactory

def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()

            # Use EmployeeFactory to create the default Employee
            EmployeeFactory.create_employee(user=user)

            login(request, user)  # Automatically log in the user after signup
            messages.success(request, "Your account has been created successfully.")
            return redirect("dashboard")

        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = SignupForm()

    return render(request, "signup.html", {"form": form})

#Jobs-View-works---------
@login_required
def job_master(request):
    projects = ProjectMaster.objects.all()  # Get all projects
    
    project_id = request.GET.get('project')  # Get selected project ID from query params
    if project_id:
        jobs = JobMaster.objects.filter(project_id=project_id)  # Filter jobs by selected project
    else:
        jobs = JobMaster.objects.all()  # Show all jobs if no project is selected

    # Pagination for jobs
    page_size = request.GET.get('page_size', 10)
    paginator = Paginator(jobs, page_size)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'job_master.html', {
        'projects': projects,
        'jobs': page_obj,
        'selected_project_id': int(project_id) if project_id else None,
        'paginator': paginator,
        'total_pages': paginator.num_pages,
        'page_range': range(1, paginator.num_pages + 1),
        'page_size': int(page_size),
    })

#--------create a new project----works
from .forms import ProjectMasterForm
#@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectMasterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Project created successfully!")
            return redirect('job_master')  # Redirect to job listing page
    else:
        form = ProjectMasterForm()

    return render(request, 'create_project.html', {'form': form})

#add new job @login_required
from .forms import JobMasterForm
def create_job(request):
    if request.method == 'POST':
        form = JobMasterForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.created_by = request.user  # Assign current user as the creator
            job.save()
            messages.success(request, "Job created successfully!")
            return redirect('job_master')  # Redirect to job listing page
    else:
        form = JobMasterForm()

    return render(request, 'create_job.html', {'form': form})


#---initiate work order view---works---
from django.shortcuts import render, get_object_or_404, redirect
from .models import WorkOrder, JobMaster, WorkOrderFactory
from .forms import InitiateWorkOrderForm, CompleteWorkOrderForm
from django.contrib.auth.decorators import login_required

class InitiateWorkOrderView(View):
    def get(self, request, job_id):
        job = get_object_or_404(JobMaster, job_id=job_id)

    
        work_order = WorkOrderFactory.create_work_order(job, request.user, address="")

        # Preload the form with the existing work order details
        form = InitiateWorkOrderForm(instance=work_order, user=request.user, job=job)

        return render(request, 'workorder/initiate_work_order.html', {
            'form': form,
            'job': job,
            'work_order': work_order
        })

    def post(self, request, job_id):
        job = get_object_or_404(JobMaster, job_id=job_id)

        # Retrieve the existing work order for the job and user
        work_order = WorkOrder.objects.filter(job=job, user=request.user).last()

        if not work_order:
            return redirect('job_master')  # Ensure we have a work order

        form = InitiateWorkOrderForm(request.POST, instance=work_order, user=request.user, job=job)

        if form.is_valid():
            updated_work_order = form.save(commit=False)
            updated_work_order.worker = form.cleaned_data.get('worker')  # Assign selected worker
            updated_work_order.save()
            return redirect('job_master')

        return render(request, 'workorder/initiate_work_order.html', {
            'form': form,
            'job': job,
            'work_order': work_order
        })

'''
@login_required
def complete_work_order(request, wo_id):
    work_order = get_object_or_404(WorkOrder, pk=wo_id)

    if request.method == "POST":
        form = CompleteWorkOrderForm(request.POST, instance=work_order)
        if form.is_valid():
            work_order.status = 'completed'
            form.save()
            return redirect('job_master')  # Redirect back after completion
    else:
        form = CompleteWorkOrderForm(instance=work_order)

    return render(request, 'workorder/complete_work_order.html', {'form': form, 'work_order': work_order})'''



class BulkUploadWorkOrderView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Get filter values from query parameters
        project_filter = request.GET.get('project', None)
        status_filter = request.GET.get('status', None)

        # Build the query filters
        filters = {}
        if project_filter:
            filters['project__project_name'] = project_filter
        if status_filter:
            filters['status'] = status_filter

        # Fetch the work orders based on the filters
        work_orders = WorkOrder.objects.filter(**filters).order_by('-wo_id')[:20]

        context = {
            'work_orders': work_orders,
            'projects': ProjectMaster.objects.all(),  # Provide available projects for filtering
            'status_choices': WorkOrder.STATUS_CHOICES,  # Provide status choices for filtering
        }
        
        return render(request, 'workorder_bulk_upload.html', context)


from django.shortcuts import render, redirect
from django.views import View
from django.utils import timezone
from datetime import datetime, timedelta
from core.models import WorkOrder, ProjectMaster, Employee


@login_required
def worker_work_orders(request):
    """Displays work orders assigned to the logged-in worker."""
    worker_orders = WorkOrder.objects.filter(worker=request.user).order_by('-created_at')

    return render(request, 'workorder/worker_work_orders.html', {
        'worker_orders': worker_orders
    })


@login_required
def complete_or_edit_work_order(request, wo_id):
    # Fetch the work order (ensure it belongs to the logged-in worker)
    work_order = get_object_or_404(WorkOrder, pk=wo_id, worker=request.user)

    # If the work order is already completed, redirect to the work orders list
    if work_order.status == 'completed':
        return redirect('worker_work_orders')

    # Handle form submission
    if request.method == 'POST':
        form = CompleteWorkOrderForm(request.POST, instance=work_order)
        if form.is_valid():
            # If the form is valid, update the status to "completed"
        
            work_order.status = form.cleaned_data.get('status')
            work_order.submitted_date = form.cleaned_data.get('submitted_date')
            work_order.days_taken = form.cleaned_data.get('days_taken')
            work_order.remarks = form.cleaned_data.get('remarks')
            form.save()  # Save the changes
            return redirect('worker_work_orders')  # Redirect to the list after completion
    else:
        # Create a form instance with the work order data
        form = CompleteWorkOrderForm(instance=work_order)

    # Render the form page
    return render(request, 'workorder/complete_work_order.html', {'form': form, 'work_order': work_order})



class DashboardView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        # Superadmin sees all work orders, others see only their assigned work orders
        if request.user.is_superuser:
            work_orders = WorkOrder.objects.all()
        else:
            try:
                work_orders = WorkOrder.objects.filter(user=request.user)  # 🔥 Directly filter by user
            except Employee.DoesNotExist:
                work_orders = WorkOrder.objects.none()

        # Get filters from request
        from_date = request.GET.get('from')
        to_date = request.GET.get('to')
        project_id = request.GET.get('project')  # 🔥 Changed from camp_id to project_id
        today = timezone.now().date()

        # Apply date filters
        if from_date and to_date:
            try:
                from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
                to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
                work_orders = work_orders.filter(requested_date__gte=from_date, requested_date__lte=to_date)
            except ValueError:
                pass

        # Apply project filter
        selected_project = None  # To be passed into the template
        if project_id and project_id != '< Select Project >':
            try:
                project_id = int(project_id)
                work_orders = work_orders.filter(project_id=project_id)
                selected_project = project_id  # 🔥 Store selected project ID
            except ValueError:
                pass

        context = {
            'total_work_order': WorkOrder.objects.count(),
            'valid_badges': 155,
            'total_bog': 11685,
            'available_pp': 60,
            'closed_wo': WorkOrder.objects.filter(status='completed').count(),  # 🔥 Updated status check
            'open_work_orders': work_orders.filter(status='in_progress').count(),  # 🔥 Updated
            'closed_same_day': work_orders.filter(status='completed', days_taken=0).count(),
            'closed_in_1_day': work_orders.filter(status='completed', days_taken=1).count(),
            'closed_in_2_days': work_orders.filter(status='completed', days_taken=2).count(),
            'closed_in_3_days': work_orders.filter(status='completed', days_taken=3).count(),
            'closed_in_4_days': work_orders.filter(status='completed', days_taken=4).count(),
            'closed_in_5_days': work_orders.filter(status='completed', days_taken=5).count(),
            'closed_in_more_than_5_days': work_orders.filter(status='completed', days_taken__gt=5).count(),
            'projects': ProjectMaster.objects.all(),  # 🔥 Load projects
            'selected_project': selected_project,  # 🔥 Pass selected project for the dropdown
            'from_workorder': from_date if from_date else today - timedelta(days=30),
            'to_workorder': to_date if to_date else today,
            'chart_data': self.get_chart_data(work_orders, today),
        }

        return render(request, 'dashboard.html', context)

    
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Get filter parameters from POST data
        from_date = request.POST.get('from_workorder')
        to_date = request.POST.get('to_workorder')
        project_id = request.POST.get('project-select')  # 🔥 Updated field name
        
        # Get all work orders
        if request.user.is_superuser:
            work_orders = WorkOrder.objects.all()
        else:
            try:
                work_orders = WorkOrder.objects.filter(user=request.user)
            except Employee.DoesNotExist:
                work_orders = WorkOrder.objects.none()
        
        today = timezone.now().date()
        
        # Apply filters
        if from_date and to_date:
            try:
                from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
                to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
                work_orders = work_orders.filter(requested_date__gte=from_date, requested_date__lte=to_date)
            except ValueError:
                pass
                
        selected_project = None  # To be passed into the template
        if project_id and project_id != '< Select Project >':
            try:
                project_id = int(project_id)
                work_orders = work_orders.filter(project_id=project_id)
                selected_project = project_id
            except ValueError:
                pass
        
        context = {
            'total_work_order': WorkOrder.objects.count(),
            'valid_badges': 155,
            'total_bog': 11685,
            'available_pp': 60,
            'closed_wo': WorkOrder.objects.filter(status='completed').count(),
            'open_work_orders': work_orders.filter(status='in_progress').count(),
            'closed_same_day': work_orders.filter(status='completed', days_taken=0).count(),
            'closed_in_1_day': work_orders.filter(status='completed', days_taken=1).count(),
            'closed_in_2_days': work_orders.filter(status='completed', days_taken=2).count(),
            'closed_in_3_days': work_orders.filter(status='completed', days_taken=3).count(),
            'closed_in_4_days': work_orders.filter(status='completed', days_taken=4).count(),
            'closed_in_5_days': work_orders.filter(status='completed', days_taken=5).count(),
            'closed_in_more_than_5_days': work_orders.filter(status='completed', days_taken__gt=5).count(),
            'projects': ProjectMaster.objects.all(),
            'selected_project': selected_project,  # 🔥 Pass selected project for the dropdown
            'from_workorder': from_date,
            'to_workorder': to_date,
            'chart_data': self.get_chart_data(work_orders, today)
        }
        return render(request, 'dashboard.html', context)
    
    def get_chart_data(self, work_orders, today):
        months = []
        labels = []
        
        for i in range(5, -1, -1):
            month_date = today - timedelta(days=30 * i)
            month_name = month_date.strftime('%b')
            
            months.append(month_date)
            labels.append(month_name)
        
        open_data = []
        closed_same_day_data = []
        one_day_data = []
        two_day_data = []
        three_day_data = []
        four_day_data = []
        five_day_data = []
        more_than_five_data = []
        
        for month_date in months:
            month_start = datetime(month_date.year, month_date.month, 1).date()
            if month_date.month == 12:
                next_month = datetime(month_date.year + 1, 1, 1).date()
            else:
                next_month = datetime(month_date.year, month_date.month + 1, 1).date()
            
            month_orders = work_orders.filter(requested_date__gte=month_start, requested_date__lt=next_month)
            total_orders = month_orders.count() or 1  

            open_data.append(month_orders.filter(status='in_progress').count() / total_orders)
            closed_same_day_data.append(month_orders.filter(status='completed', days_taken=0).count() / total_orders)
            one_day_data.append(month_orders.filter(status='completed', days_taken=1).count() / total_orders)
            two_day_data.append(month_orders.filter(status='completed', days_taken=2).count() / total_orders)
            three_day_data.append(month_orders.filter(status='completed', days_taken=3).count() / total_orders)
            four_day_data.append(month_orders.filter(status='completed', days_taken=4).count() / total_orders)
            five_day_data.append(month_orders.filter(status='completed', days_taken=5).count() / total_orders)
            more_than_five_data.append(month_orders.filter(status='completed', days_taken__gt=5).count() / total_orders)
        
        return {
            'labels': labels,
            'datasets': [
                {'label': 'Work Orders In Progress', 'data': open_data, 'borderColor': '#FF6384'},
                {'label': 'Completed Same Day', 'data': closed_same_day_data, 'borderColor': '#36A2EB'},
                {'label': 'Completed in 1 Day', 'data': one_day_data, 'borderColor': '#FFCE56'},
            ]
        }


class WorkOrderReportView(View):
    """
    View for the work order report page
    """
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        camp_id = request.GET.get('camp', '')
        from_date_str = request.GET.get('from_date', '')
        to_date_str = request.GET.get('to_date', '')

        today = timezone.now().date()
        from_date = datetime.datetime.strptime(from_date_str, '%Y-%m-%d').date() if from_date_str else today - timedelta(days=30)
        to_date = datetime.datetime.strptime(to_date_str, '%Y-%m-%d').date() if to_date_str else today

        work_order_data = {
            'open_work_orders': 0,
            'closed_same_day': 0,
            'closed_one_day': 0,
            'closed_two_day': 0,
            'closed_three_day': 0,
            'closed_four_day': 0,
            'closed_five_day': 0,
            'closed_more_than_five': 0,
            'total_work_orders': 0,
            'completion_rate': 0,
        }

        camps = [
            {'id': 1, 'name': 'Camp A'},
            {'id': 2, 'name': 'Camp B'},
            {'id': 3, 'name': 'Camp C'},
        ]

        context = {
            'camps': camps,
            'selected_camp': camp_id,
            'from_date': from_date,
            'to_date': to_date,
            **work_order_data
        }

        return render(request, 'work_order_report.html', context)


class DownloadWorkOrderExcelView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Fetch the latest 20 work orders
        work_orders = WorkOrder.objects.all().order_by('-wo_id')[:20]
        
        # Create a workbook and worksheet
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = "Work Orders"
        
        # Define headers from model fields
        headers = [
            'wo_id', 'wo_numeric_no', 'wo_no', 'employee_id', 'phone_no',
            'camp_id', 'camp_name', 'building_id', 'project_id', 'building_code',
            'apartment_id', 'apt_area', 'work_order_job_type_id', 'wo_description',
            'requested_date', 'submitted_date', 'status', 'status_date',
            'days_taken', 'remarks', 'created_at', 'updated_at'
        ]
        
        # Add headers to worksheet
        for col_num, header in enumerate(headers, 1):
            worksheet.cell(row=1, column=col_num, value=header)
        
        # Populate work order data
        for row_num, work_order in enumerate(work_orders, 2):
            data = [
                work_order.wo_id, work_order.wo_numeric_no, work_order.wo_no,
                work_order.employee_id, work_order.phone_no, work_order.camp_id,
                work_order.camp_name, work_order.building_id, work_order.project_id,
                work_order.building_code, work_order.apartment_id, work_order.apt_area,
                work_order.work_order_job_type_id, work_order.wo_description,
                work_order.requested_date, work_order.submitted_date, work_order.status,
                work_order.status_date, work_order.days_taken, work_order.remarks,
                work_order.created_at.replace(tzinfo=None) if work_order.created_at else None,
                work_order.updated_at.replace(tzinfo=None) if work_order.updated_at else None
            ]
            
            for col_num, value in enumerate(data, 1):
                worksheet.cell(row=row_num, column=col_num, value=value)
        
        # Create HTTP response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=work_order_data.xlsx'
        
        # Save workbook to response
        workbook.save(response)
        
        return response

#-----------Manage Employee View----------------
class ManageEmployeeView(View):
    def get(self, request, *args, **kwargs):
        """Displays a list of employees, ordered by the latest employee ID."""
        if not request.user.is_authenticated:
            return redirect('login')

        context = {
            'uploaded_data': Employee.objects.all().order_by('-employee_id')[:20],
            'error_message': None,
            'invalid_data': False,
            'roles': EmployeeFactory.ROLE_DEFAULTS.keys(),  # Added roles for dropdown
        }
        return render(request, 'manage_employee.html', context)

class ViewEmployeeDetails(View):
    def get(self, request, employee_id):
        """Returns JSON details of an employee."""
        employee = get_object_or_404(Employee, employee_id=employee_id)
        data = {
            "employee_id": employee.employee_id,
            "name": employee.name,
            "email": employee.user.email if employee.user else "N/A",
            "assigned_salary": float(employee.assigned_salary),
            "project": employee.project.project_name if employee.project else "N/A",
            "employee_status": "Active" if employee.employee_status else "Inactive",
            "date_of_birth": employee.date_of_birth.strftime("%Y-%m-%d") if employee.date_of_birth else "N/A",
            "passport_no": employee.passport_no if employee.passport_no else "N/A",
            "gender": employee.gender if employee.gender else "N/A",
            "native_license_status": employee.native_license_status if employee.native_license_status else "N/A",
            "recruitment_remarks": employee.recruitment_remarks if employee.recruitment_remarks else "N/A",
            "created_at": employee.created_at.strftime("%Y-%m-%d"),
        }
        return JsonResponse({"employee": data})

class EditEmployeeDetails(View):
    """Handles fetching and updating employee details."""

    def get(self, request, employee_id):
        """Returns JSON details of an employee."""
        employee = get_object_or_404(Employee, employee_id=employee_id)  # Ensure correct lookup
        print(employee.user.email)
        data = {
            "employee_id": employee.employee_id,
            "name": employee.name,
            "email": employee.user.email if employee.user else "N/A",
            "assigned_salary": float(employee.assigned_salary),
            "project": employee.project.project_name if employee.project else "N/A",
            "employee_status": "Active" if employee.employee_status else "Inactive",
            "date_of_birth": employee.date_of_birth.strftime("%Y-%m-%d") if employee.date_of_birth else "N/A",
            "passport_no": employee.passport_no if employee.passport_no else "N/A",
            "gender": employee.gender if employee.gender else "N/A",
            "native_license_status": employee.native_license_status if employee.native_license_status else "N/A",
            "recruitment_remarks": employee.recruitment_remarks if employee.recruitment_remarks else "N/A",
            "created_at": employee.created_at.strftime("%Y-%m-%d"),
        }
        return JsonResponse({"employee": data})

    def post(self, request, employee_id):
        """Updates employee details."""
        employee = get_object_or_404(Employee, id=employee_id)
        data = json.loads(request.body.decode('utf-8'))  # Assume valid JSON
        
        for field, value in data.items():
            if hasattr(employee, field):  # Only update existing fields
                setattr(employee, field, value)

        employee.save()
        return JsonResponse({"success": True, "message": "Employee updated successfully"})

@method_decorator(csrf_exempt, name='dispatch')
class UpdateEmployeeDetails(View):
    def post(self, request, employee_id, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        try:
            employee = Employee.objects.get(EmployeeId=employee_id)
            
            # Update fields from the form
            for field in employee._meta.fields:
                field_name = field.name
                if field_name in request.POST and field_name != 'EmployeeId':
                    value = request.POST.get(field_name)
                    
                    # Handle ForeignKey (project) specifically
                    if field_name == 'project':
                        if value == '' or value is None or value == "null":
                            value = None
                        else:
                            try:
                                value = ProjectMaster.objects.get(project_id=int(value))
                            except (ProjectMaster.DoesNotExist, ValueError):
                                return JsonResponse({'success': False, 'error': 'Invalid project selected.'}, status=400)

                    # Handle other data types
                    elif field.get_internal_type() == 'DateField' and value:
                        try:
                            value = datetime.datetime.strptime(value, '%Y-%m-%d').date()
                        except ValueError:
                            value = None
                    elif field.get_internal_type() == 'TimeField' and value:
                        try:
                            value = datetime.datetime.strptime(value, '%H:%M').time()
                        except ValueError:
                            value = None
                    elif field.get_internal_type() == 'BooleanField':
                        value = value.lower() == 'true'
                    elif field.get_internal_type() == 'DecimalField' and value:
                        try:
                            value = float(value)
                        except ValueError:
                            value = None
                    elif field.get_internal_type() == 'IntegerField' and value:
                        try:
                            value = int(value)
                        except ValueError:
                            value = None
                    
                    setattr(employee, field_name, value)
            
            employee.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Employee updated successfully'
            })
        except Employee.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Employee not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
#-----------Manage employee EnD---------




class RecruitmentSummaryView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        # Get all users for dropdown
        all_users = User.objects.all()

        # Get all projects with associated work order count
        projects_list = ProjectMaster.objects.annotate(
            total_work_orders=Count('work_orders', distinct=True)
        )

        context = {
            'projects_list': projects_list,
            'all_users': all_users,
            'use_chart_js': True
        }
        return render(request, 'recruitment_summary.html', context)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        # Extract filter parameters from request
        selected_projects = request.POST.getlist('projects')
        selected_user_id = request.POST.get('user')
        arrival_from = request.POST.get('arrival_from')
        arrival_to = request.POST.get('arrival_to')

        # Base query filter
        query = Q()

        # Filter by selected user if provided
        if selected_user_id and selected_user_id != "all":
            query &= Q(user_id=selected_user_id)

        # Filter by selected projects if provided
        if selected_projects and 'all' not in selected_projects:
            query &= Q(project_id__in=selected_projects)

        # Filter by date range
        if arrival_from:
            try:
                from_date = datetime.datetime.strptime(arrival_from, '%Y-%m-%d').date()
                query &= Q(requested_date__gte=from_date)
            except ValueError:
                pass

        if arrival_to:
            try:
                to_date = datetime.datetime.strptime(arrival_to, '%Y-%m-%d').date()
                query &= Q(requested_date__lte=to_date)
            except ValueError:
                pass

        # Fetch all users for dropdown
        all_users = User.objects.all()

        # Apply filters and get all projects with work order counts
        projects_list = ProjectMaster.objects.filter(work_orders__in=WorkOrder.objects.filter(query)).annotate(
            total_work_orders=Count('work_orders', distinct=True)
        )

        context = {
            'projects_list': projects_list,
            'all_users': all_users,
            'selected_user_id': selected_user_id,
            'selected_projects': selected_projects,
            'arrival_from': arrival_from,
            'arrival_to': arrival_to,
            'use_chart_js': True,
            'is_filtered': True
        }
        return render(request, 'recruitment_summary.html', context)   
class ExportRecruitmentSummary(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        selected_projects = request.POST.getlist('projects') if request.method == 'POST' else []
        arrival_from = request.POST.get('arrival_from') if request.method == 'POST' else None
        arrival_to = request.POST.get('arrival_to') if request.method == 'POST' else None
        
        # Base query
        query = Q()
        
        # Apply filters
        if selected_projects and 'all' not in selected_projects:
            query &= Q(project_id__in=selected_projects)
            
        if arrival_from:
            try:
                from_date = datetime.datetime.strptime(arrival_from, '%d-%m-%Y').date()
                query &= Q(employees__ArrivalDate__gte=from_date)
            except ValueError:
                pass
                
        if arrival_to:
            try:
                to_date = datetime.datetime.strptime(arrival_to, '%d-%m-%Y').date()
                query &= Q(employees__ArrivalDate__lte=to_date)
            except ValueError:
                pass
        
        # Always filter for arrived employees
        arrival_status_query = Q(employees__ArrivalStatus='Arrived')
        
        # Get filtered projects with count
        if query:
            projects_list = ProjectMaster.objects.filter(query).annotate(
                total_arrived=Count('employees', filter=arrival_status_query, distinct=True)
            )
        else:
            projects_list = ProjectMaster.objects.annotate(
                total_arrived=Count('employees', filter=arrival_status_query, distinct=True)
            )
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Recruitment Summary')
        
        # Add headers
        headers = ['Project', 'Current Status', 'Total Arrived']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)
        
        # Add data
        for row, project in enumerate(projects_list, 1):
            worksheet.write(row, 0, project.project_name)
            worksheet.write(row, 1, 'Active' if project.project_status else 'Inactive')
            worksheet.write(row, 2, project.total_arrived)
        
        workbook.close()
        
        # Create the HttpResponse with the appropriate Excel header
        output.seek(0)
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=recruitment_summary.xlsx'
        
        return response

@login_required
def employee_profile_view(request):
    """
    Allows users to update their own employee profile.
    """
    try:
        employee = request.user.employee  # Get Employee record linked to logged-in User
    except Employee.DoesNotExist:
        messages.error(request, "No associated employee record found.")
        return redirect('signup')

    if request.method == 'POST':
        form = EmployeeProfileForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('employee-profile')  # Reload profile page
    else:
        form = EmployeeProfileForm(instance=employee)

    context = {
        'form': form,
        'employee': employee
    }
    return render(request, 'employee_profile.html', context)
    
class ExcelUploadNewHireView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        # for i in Employee.objects.all():
        #     print(i.EmployeeId)
        context = {
            'uploaded_data': NewHire.objects.all().order_by('-new_hire_id')[:20],
            'error_message': None,
            'invalid_data': False,
        }
        return render(request, 'new_hire_excel_upload.html', context)
    
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        context = {
            'uploaded_data': [],
            'error_message': None,
            'invalid_data': False,
        }
        context['uploaded_data'] = NewHire.objects.all().order_by('-new_hire_id')[:20]
        
        excel_file = request.FILES['excel_file']

        if not excel_file.name.endswith(('.xlsx', '.xls')):
            context['error_message'] = "Please upload a valid Excel file."
            return render(request, 'new_hire_excel_upload.html', context)
        
        try:
            df = pd.read_excel(excel_file)
            required_columns = {"new_hire_id", "employee_id", "work_company_name", "arrived_salary",
                "native_language", "education", "marital_status", "religion",
                "food_type", "home_address", "email_id", "city_of_birth",
                "work_status", "remark", "camp_id"}
            
            # missing_columns = required_columns - set(df.columns)
            # if missing_columns:
            #     return JsonResponse({'error': f'Missing required columns: {", ".join(missing_columns)}'}, status=400)
            
            employees_to_create = []
            new_hires = [
                NewHire(
                    # new_hire_id=row["new_hire_id"],
                    employee_id=Employee.objects.filter(EmployeeId=int(row["employee_id"])).first(),
                    work_company_name=row["work_company_name"],
                    arrived_salary=row["arrived_salary"],
                    native_language=row["native_language"],
                    education=row["education"],
                    marital_status=row["marital_status"],
                    religion=row["religion"],
                    food_type=row["food_type"],
                    home_address=row["home_address"],
                    email_id=row["email_id"],
                    city_of_birth=row["city_of_birth"],
                    work_status=row["work_status"],
                    remark=row["remark"],
                    camp_id=row["camp_id"]
                )
                for _, row in df.iterrows()
            ]
            
            NewHire.objects.bulk_create(new_hires)
            
            context['uploaded_data'] = NewHire.objects.all().order_by('-new_hire_id')[:20]

            # messages.success(request, f"Successfully uploaded {len(df)} employees.")
            
        except Exception as e:
            context['error_message'] = f"Error processing file: {str(e)}"
        
        return render(request, 'new_hire_excel_upload.html', context)
        

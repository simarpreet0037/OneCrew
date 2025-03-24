from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.db import models
from django.views.decorators.http import require_http_methods
from .models import User, JobMaster, ProjectMaster, Employee, NewHire, WorkOrder, Notification
from .forms import EmployeeProfileForm, EditOrCompleteWorkOrderForm
from openpyxl import Workbook
import pandas as pd
import io
import xlsxwriter
import datetime
from datetime import datetime, date, time
import random
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
import json
from decimal import Decimal
from django.contrib.auth.decorators import login_required



class DashboardView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        today = timezone.now().date()
        
        # Determine accessible work orders
        if request.user.is_superuser:
            work_orders = WorkOrder.objects.all()
        else:
            work_orders = WorkOrder.objects.filter(worker=request.user)

        # Filtering
        from_date = request.GET.get('from', (today - timedelta(days=30)).strftime('%Y-%m-%d'))
        to_date = request.GET.get('to', today.strftime('%Y-%m-%d'))
        project_id = request.GET.get('project')
        
        try:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
            work_orders = work_orders.filter(requested_date__range=(from_date, to_date))
        except ValueError:
            pass
        
        selected_project = None
        if project_id:
            try:
                project_id = int(project_id)
                work_orders = work_orders.filter(project_id=project_id)
                selected_project = project_id
            except ValueError:
                pass

        context = {
            'total_work_order': work_orders.count(),
            'closed_wo': work_orders.filter(status='completed').count(),
            'open_work_orders': work_orders.filter(status='in_progress').count(),
            'closed_same_day': work_orders.filter(status='completed', days_taken=0).count(),
            'closed_in_1_day': work_orders.filter(status='completed', days_taken=1).count(),
            'closed_in_2_days': work_orders.filter(status='completed', days_taken=2).count(),
            'closed_in_3_days': work_orders.filter(status='completed', days_taken=3).count(),
            'closed_in_4_days': work_orders.filter(status='completed', days_taken=4).count(),
            'closed_in_5_days': work_orders.filter(status='completed', days_taken=5).count(),
            'closed_in_more_than_5_days': work_orders.filter(status='completed', days_taken__gt=5).count(),
            'projects': ProjectMaster.objects.all(),
            'selected_project': selected_project,
            'from_workorder': from_date,
            'to_workorder': to_date,
            'chart_data': self.get_chart_data(work_orders, today),
        }

        return render(request, 'dashboard.html', context)

    def get_chart_data(self, work_orders, today):
        labels = [(today - timedelta(days=30 * i)).strftime('%b') for i in range(5, -1, -1)]
        chart_data = {
            'labels': labels,
            'datasets': [
                {'label': 'Work Orders In Progress', 'data': [], 'borderColor': '#FF6384'},
                {'label': 'Completed Same Day', 'data': [], 'borderColor': '#36A2EB'},
                {'label': 'Completed in 1 Day', 'data': [], 'borderColor': '#FFCE56'},
            ]
        }
        
        for i in range(5, -1, -1):
            month_start = today - timedelta(days=30 * i)
            month_end = today - timedelta(days=30 * (i - 1)) if i > 0 else today
            
            month_orders = work_orders.filter(requested_date__range=(month_start, month_end))
            total_orders = max(month_orders.count(), 1)
            
            chart_data['datasets'][0]['data'].append(month_orders.filter(status='in_progress').count() / total_orders)
            chart_data['datasets'][1]['data'].append(month_orders.filter(status='completed', days_taken=0).count() / total_orders)
            chart_data['datasets'][2]['data'].append(month_orders.filter(status='completed', days_taken=1).count() / total_orders)
        
        return chart_data

class LoginView(View):
    """
    LoginView handles user authentication.
    
    - If the user is already authenticated, they are redirected to the dashboard.
    - Displays the login page for unauthenticated users.
    - Authenticates users based on their email and password.
    - Redirects authenticated users to the dashboard or shows an error message on failure.
    """
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
    
class LogoutView(View):
    """
    LogoutView handles user logout.
    
    - Logs out the authenticated user.
    - Displays a success message upon successful logout.
    - Redirects the user to the login page.
    """
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
        return redirect('login')

from .forms import SignupForm
from .models import Employee, EmployeeFactory
from OneCrew.settings import SUPERUSER_SECRET_KEY
# --------------------------------------------------
# User Signup View (Creates Employee Profile & Logs In)
# --------------------------------------------------
def signup_view(request):
    """
    Handles user signup:
    - Processes signup form submission.
    - Saves user with a hashed password.
    - Creates an associated Employee profile using EmployeeFactory.
    - Allows superuser creation if the correct secret key is provided.
    - Automatically logs in the user upon successful registration.
    """
    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])

            # Determine if the user should be a superuser
            if form.cleaned_data["secret_key"] == SUPERUSER_SECRET_KEY:
                user.is_staff = True
                user.is_superuser = True

            user.save()

    
            EmployeeFactory.create_employee(user=user)

            login(request, user)  # Automatically log in the user after signup
            messages.success(request, "Your account has been created successfully.")
            return redirect("dashboard")

        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = SignupForm()

    return render(request, "signup.html", {"form": form})
    

    # --------------------------------------------------
# Job Listings and Filtering by Project (With Pagination)
# --------------------------------------------------
@login_required
def job_master(request):
    """
    Displays a list of jobs, optionally filtered by a selected project.
    Includes pagination for better navigation.
    """
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

from .forms import ProjectMasterForm
# --------------------------------------------------
# Create a New Project (Form Handling)
# --------------------------------------------------
@login_required
def create_project(request):
    """
    Handles the creation of a new project.
    Displays a form and saves the project data on form submission.
    """
    if request.method == 'POST':
        form = ProjectMasterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Project created successfully!")
            return redirect('job_master')  # Redirect to job listing page
    else:
        form = ProjectMasterForm()

    return render(request, 'create_project.html', {'form': form})


from .forms import JobMasterForm
# --------------------------------------------------
# Create a New Job (Assigns Creator Automatically)
# --------------------------------------------------
@login_required
def create_job(request):
    """
    Handles job creation. Assigns the currently logged-in user as the creator of the job.
    Displays a form and saves the job data on form submission.
    """
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


from django.shortcuts import render, get_object_or_404, redirect
from .models import WorkOrder, JobMaster, WorkOrderFactory
from .forms import InitiateWorkOrderForm, CompleteWorkOrderForm
from django.contrib.auth.decorators import login_required
# --------------------------------------------------
# Work Order Initiation View (GET: Load Form, POST: Save Work Order)
# --------------------------------------------------
class InitiateWorkOrderView(View):
    """
    Handles the initiation of a Work Order for a given job.
    
    - GET: Loads the Work Order form, pre-filling it with existing data.
    - POST: Saves the updated Work Order with assigned worker information and notifies observers.
    """

    def get(self, request, job_id):
        job = get_object_or_404(JobMaster, job_id=job_id)
        work_order = WorkOrderFactory.create_work_order(job, request.user, address="")
        form = InitiateWorkOrderForm(instance=work_order, user=request.user, job=job)
        return render(request, 'workorder/initiate_work_order.html', {
            'form': form,
            'job': job,
            'work_order': work_order
        })

    def post(self, request, job_id):
        job = get_object_or_404(JobMaster, job_id=job_id)
        work_order = WorkOrder.objects.filter(job=job, user=request.user).last()

        if not work_order:
            return redirect('job_master')  # Ensure we have a work order

        form = InitiateWorkOrderForm(request.POST, instance=work_order, user=request.user, job=job)

        if form.is_valid():
            updated_work_order = form.save(commit=False)
            updated_work_order.worker = form.cleaned_data.get('worker')
            updated_work_order.save()
            
            # Notify observers (including email notification)
            notification_observer = Notification()
            updated_work_order.attach(notification_observer)
            updated_work_order.notify()
            
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

#-----------Manage Employee View----------------#
class DateEncoder(json.JSONEncoder):
    """
    Custom JSON Encoder to handle serialization of:
    - datetime.date and datetime.datetime -> ISO format string
    - datetime.time -> 'HH:MM:SS' string
    - Decimal -> float
    """
    def default(self, obj):
        if isinstance(obj, (datetime,date)):  
            return obj.isoformat()
        if isinstance(obj, time):  # Add `time` handling
            return obj.strftime('%H:%M:%S')  # Format as 'HH:MM:SS'
        if isinstance(obj, Decimal):  
            return float(obj)  
        return super().default(obj)
    
# --------------------------------------------------
# Manage Employee View - Displays a List of Employees
# --------------------------------------------------
class ManageEmployeeView(View):
    """
    Fetches and displays a list of employees with relevant details.
    Includes project assignments and user email information.
    """
    def get(self, request, *args, **kwargs):
        """Displays a list of employees with relevant details."""
        if not request.user.is_authenticated:
            return redirect('login')

        # Fetch employee data and select the important fields along with the email from the related User model
        uploaded_data = Employee.objects.all().select_related('user').order_by('-employee_id')[:20]
        
        # Create a list of dictionaries with relevant data
        employee_data = []
        for employee in uploaded_data:
            employee_data.append({
                'employee_id': employee.employee_id,
                'name': employee.name,
                'assigned_salary': employee.assigned_salary,
                'employee_status': employee.employee_status,
                'project': employee.project.project_name if employee.project else None,  # Project name if available
                'email': employee.user.email if employee.user else None,  # Fetch email from related User model
            })
        
        context = {
            'uploaded_data': employee_data,
            'error_message': None,
            'invalid_data': False,
            'roles': EmployeeFactory.ROLE_DEFAULTS.keys(),  # Added roles for dropdown
        }

        return render(request, 'manage_employee.html', context)
    
# --------------------------------------------------
# View Employee Details - Fetch Employee Information
# --------------------------------------------------
class ViewEmployeeDetails(View):
    """
    Retrieves detailed information about a specific employee.
    Returns data in JSON format, including personal and work-related details.
    """
    def get(self, request, employee_id, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        try:
            employee = Employee.objects.get(employee_id=employee_id)
            # Convert model instance to dictionary, including the email from the related User model
            employee_data = {
                'employee_id': employee.employee_id,
                'name': employee.name,
                'assigned_salary': employee.assigned_salary,
                'employee_status': employee.employee_status,
                'project': employee.project.project_name if employee.project else None,  # Project name
                'email': employee.user.email if employee.user else None,  # Email from related User model
                'gender': employee.gender,
                'date_of_birth': employee.date_of_birth,
                'passport_no': employee.passport_no,
                'native_license_expiry': employee.native_license_expiry,
                'recruitment_remarks': employee.recruitment_remarks,
            }
            return JsonResponse({
                'success': True,
                'employee': employee_data
            }, encoder=DateEncoder)
        except Employee.DoesNotExist:
            return JsonResponse({'error': 'Employee not found'}, status=404)
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=500)
        
# --------------------------------------------------
# Edit Employee Details - Fetch Data for Editing
# --------------------------------------------------
class EditEmployeeDetails(View):
    """
    Retrieves an employee's details for editing.
    Returns data in JSON format with prefilled values.
    """
    def get(self, request, employee_id, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        try:
            employee = Employee.objects.get(employee_id=employee_id)
            # Convert model instance to dictionary, including the email from the related User model
            employee_data = {
                'employee_id': employee.employee_id,
                'name': employee.name,
                'assigned_salary': employee.assigned_salary,
                'employee_status': employee.employee_status,
                'project': employee.project.project_name if employee.project else None,  # Project name
                'email': employee.user.email if employee.user else None,  # Email from related User model
                'gender': employee.gender,
                'date_of_birth': employee.date_of_birth,
                'passport_no': employee.passport_no,
                'native_license_expiry': employee.native_license_expiry,
                'recruitment_remarks': employee.recruitment_remarks,
            }
            
            return JsonResponse({
                'success': True,
                'employee': json.loads(json.dumps(employee_data, cls=DateEncoder))
            }, encoder=DateEncoder)
        except Employee.DoesNotExist:
            return JsonResponse({'error': 'Employee not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
# --------------------------------------------------
# Update Employee Details - Save Changes to Employee Records
# --------------------------------------------------
@method_decorator(csrf_exempt, name='dispatch')
class UpdateEmployeeDetails(View):
    """
    Handles updating an employee's details based on form submission.
    Supports updating fields including email, project assignment, salary, and status.
    """
    def post(self, request, employee_id, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        try:
            employee = Employee.objects.get(employee_id=employee_id)
            # Update fields from the form
            for field in employee._meta.fields:
                field_name = field.name
                if field_name in request.POST and field_name != 'employee_id':
                    value = request.POST.get(field_name)
                    
                    # Handle email separately if required
                    if field_name == 'email' and employee.user:
                        employee.user.email = value
                        employee.user.save()
                    else:
                        # Handle ForeignKey (project) specifically
                        if field_name == 'project':
                            if value == '' or value is None or value == "null":
                                value = None
                            else:
                                try:
                                    value = ProjectMaster.objects.get(project_id=int(value))
                                except (ProjectMaster.DoesNotExist, ValueError):
                                    return JsonResponse({'success': False, 'error': 'Invalid project selected.'}, status=400)

                        # Handle other data types (DateField, TimeField, etc.)
                        if field.get_internal_type() == 'DateField' and value:
                            try:
                                value = datetime.strptime(value, '%Y-%m-%d').date()
                            except ValueError:
                                value = None
                        elif field.get_internal_type() == 'TimeField' and value:
                            try:
                                value = datetime.strptime(value, '%H:%M').time()
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

#-----------Manage employee EnD---------#


# --------------------------------------------------
# Recruitment Summary View (Displays & Filters Work Order Data)
# --------------------------------------------------
class RecruitmentSummaryView(View):
    """
    Displays a summary of recruitment projects and their associated work orders.

    - GET: Fetches and displays all projects with work order counts.
    - POST: Filters projects based on selected users, projects, and date range.
    """
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

# --------------------------------------------------
# All Work Orders View (Displays & Filters Work Orders)
# --------------------------------------------------
class AllWorkOrderView(View):
    """
    Displays a list of all work orders with filtering options.

    - GET: Fetches and displays work orders based on project and status filters.
    """
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
    











@login_required
def employee_profile_view(request):
    """
    Allows users to update their own employee profile, including email and password.
    """
    try:
        employee = request.user.employee  # Get Employee record linked to logged-in User
    except Employee.DoesNotExist:
        messages.error(request, "No associated employee record found.")
        return redirect('signup')

    if request.method == 'POST':
        form = EmployeeProfileForm(request.POST, instance=employee, user=request.user)
        if form.is_valid():
            form.save()

            # If password was changed, log out user and redirect to login page
            if form.cleaned_data.get("password1"):
                messages.success(request, "Profile updated successfully. Please log in again with your new password.")
                return redirect('login')

            messages.success(request, "Profile updated successfully.")
            return redirect('employee-profile')  # Reload profile page
    else:
        form = EmployeeProfileForm(instance=employee, user=request.user)

    context = {
        'form': form,
        'employee': employee
    }
    return render(request, 'employee_profile.html', context)
    


from django.shortcuts import render, redirect
from django.views import View
from django.utils import timezone
from datetime import datetime, timedelta
from dashboard.models import WorkOrder, ProjectMaster, Employee


@login_required
def worker_work_orders(request):
    """Displays work orders assigned to the logged-in worker."""
    worker_orders = WorkOrder.objects.filter(worker=request.user).order_by('-created_at')

    return render(request, 'workorder/worker_work_orders.html', {
        'worker_orders': worker_orders
    })


@login_required
def complete_or_edit_work_order_admin(request, wo_id):
    # Fetch the work order (ensure it belongs to the logged-in worker)
    work_order = get_object_or_404(WorkOrder, pk=wo_id)


    # Handle form submission
    if request.method == 'POST':
        form = CompleteWorkOrderForm(request.POST, instance=work_order)
        if form.is_valid():
            submitted_date = form.cleaned_data.get('submitted_date')
            status = form.cleaned_data.get('status')

            # Only calculate days_taken if the status is 'completed'
            if status == 'completed' and work_order.requested_date:
                work_order.days_taken = (submitted_date - work_order.requested_date).days
            else:
                work_order.days_taken = None  # Reset if status is not 'completed'

            # Save the form with calculated values
            form.save()

            # Notify observers (including email notification)
            notification_observer = Notification()
            work_order.attach(notification_observer)
            work_order.notify()
            return redirect('workorder-list')  # Redirect after saving
    else:
        form = CompleteWorkOrderForm(instance=work_order)

    return render(request, 'workorder/complete_work_order_admin.html', {'form': form, 'work_order': work_order})

@login_required
def edit_or_complete_work_order(request, wo_id):
    # Fetch the work order assigned to the logged-in employee
    work_order = get_object_or_404(WorkOrder, pk=wo_id, worker=request.user)

    # If the work order is already completed, restrict further edits
    if work_order.status == 'completed':
        return redirect('employee_work_orders')

    if request.method == 'POST':
        form = EditOrCompleteWorkOrderForm(request.POST, instance=work_order)

        if form.is_valid():
            work_order.status = form.cleaned_data['status']

            # Calculate days taken only when completed
            if work_order.status == 'completed' and work_order.requested_date:
                work_order.days_taken = (form.cleaned_data['submitted_date'] - work_order.requested_date).days

            work_order.save()
            
             # Notify observers (including email notification)
            notification_observer = Notification()
            work_order.attach(notification_observer)
            work_order.notify()
            return redirect('worker_work_orders')  # Redirect after update

    else:
        form = EditOrCompleteWorkOrderForm(instance=work_order)

    return render(request, 'workorder/edit_or_complete_work_order.html', {'form': form, 'work_order': work_order})
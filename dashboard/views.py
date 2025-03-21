# views.py
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Count, Q
from datetime import datetime, timedelta
from django.views import View
from django.db import models
from .models import ProjectMaster, JobMaster, Employee, NewHire, WorkOrder, User
import pandas as pd

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

class DashboardView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        # Get all work orders
        work_orders = WorkOrder.objects.all()
        
        # Get current date
        today = timezone.now().date()
        
        # Calculate dashboard metrics
        context = {
            # Default values from the screenshot
            'total_occupancy': 0,
            'valid_badges': 155,
            'total_bog': 11685,
            'available_pp': 60,
            
            # Work order metrics
            'closed_wo': work_orders.filter(status='Closed').count(),
            
            # Work order summary data
            'open_work_orders': work_orders.filter(status='Open').count(),
            'closed_same_day': work_orders.filter(
                status='Closed',
                status_date=models.F('requested_date')
            ).count(),
            'closed_in_1_day': work_orders.filter(
                status='Closed',
                days_taken=1
            ).count(),
            'closed_in_2_days': work_orders.filter(
                status='Closed',
                days_taken=2
            ).count(),
            'closed_in_3_days': work_orders.filter(
                status='Closed',
                days_taken=3
            ).count(),
            'closed_in_4_days': work_orders.filter(
                status='Closed',
                days_taken=4
            ).count(),
            'closed_in_5_days': work_orders.filter(
                status='Closed',
                days_taken=5
            ).count(),
            'closed_in_more_than_5_days': work_orders.filter(
                status='Closed',
                days_taken__gt=5
            ).count(),
            
            # Get all camps for filtering
            'camps': self.get_camps(work_orders),
            
            # Get chart data for the last 6 months
            'chart_data': self.get_chart_data(work_orders, today),
        }
        
        context = {
        'total_occupancy': 342,
        'valid_badges': 155,
        'total_bog': 11685,
        'available_pp': 60,
        'closed_wo': 127,
        
        # Work order summary data
        'open_work_orders': 25,
        'closed_same_day': 55,
        'closed_in_1_day': 19,
        'closed_in_2_days': 11,
        'closed_in_3_days': 6,
        'closed_in_4_days': 3,
        'closed_in_5_days': 2,
        'closed_in_more_than_5_days': 1,
        
        # Chart data for JS
        'chart_data': {
            'labels': ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar'],
            'datasets': [
                {
                    'label': 'OpenWorkOrders',
                    'data': [0.35, 0.42, 0.28, 0.31, 0.38, 0.25],
                    'borderColor': '#FF6384'
                },
                {
                    'label': 'ClosedInSameDay',
                    'data': [0.45, 0.38, 0.41, 0.52, 0.48, 0.55],
                    'borderColor': '#36A2EB'
                },
                {
                    'label': 'OneDayWorkOrders',
                    'data': [0.22, 0.25, 0.20, 0.18, 0.21, 0.19],
                    'borderColor': '#FFCE56'
                },
                {
                    'label': 'TwoDayWorkOrders',
                    'data': [0.15, 0.18, 0.22, 0.12, 0.14, 0.11],
                    'borderColor': '#4BC0C0'
                },
                {
                    'label': 'ThreeDayWorkOrders',
                    'data': [0.08, 0.10, 0.12, 0.07, 0.09, 0.06],
                    'borderColor': '#9966FF'
                },
                {
                    'label': 'FourDayWorkOrders',
                    'data': [0.05, 0.07, 0.09, 0.04, 0.06, 0.03],
                    'borderColor': '#FF9F40'
                },
                {
                    'label': 'FiveDayWorkOrders',
                    'data': [0.03, 0.04, 0.06, 0.02, 0.03, 0.02],
                    'borderColor': '#4BC0A0'
                },
                {
                    'label': 'MoreThanFiveDays',
                    'data': [0.02, 0.03, 0.05, 0.01, 0.02, 0.01],
                    'borderColor': '#9900CC'
                }
            ]
        }
    }
        return render(request, 'dashboard.html', context)
    
    def get_camps(self, work_orders):
        # Get unique camps from work orders
        camps = work_orders.values('camp_id', 'camp_name').distinct()
        return [{'id': camp['camp_id'], 'name': camp['camp_name']} for camp in camps]
    
    def get_chart_data(self, work_orders, today):
        # Calculate data for the last 6 months
        months = []
        labels = []
        
        for i in range(5, -1, -1):
            month_date = today - timedelta(days=30 * i)
            month_name = month_date.strftime('%b')
            
            months.append(month_date)
            labels.append(month_name)
        
        # Chart datasets
        datasets = []
        
        # Open work orders by month
        open_data = []
        closed_same_day_data = []
        one_day_data = []
        two_day_data = []
        three_day_data = []
        four_day_data = []
        five_day_data = []
        more_than_five_data = []
        
        for month_date in months:
            month_start = datetime.datetime(month_date.year, month_date.month, 1).date()
            if month_date.month == 12:
                next_month = datetime.datetime(month_date.year + 1, 1, 1).date()
            else:
                next_month = datetime.datetime(month_date.year, month_date.month + 1, 1).date()
            
            # Filter work orders for this month
            month_orders = work_orders.filter(requested_date__gte=month_start, requested_date__lt=next_month)
            
            # Calculate metrics for this month (using sample data similar to screenshot)
            total_orders = month_orders.count() or 1  # Avoid division by zero
            
            open_data.append(month_orders.filter(status='Open').count() / total_orders)
            
            closed_same_day_data.append(
                month_orders.filter(status='Closed', days_taken=0).count() / total_orders
            )
            
            one_day_data.append(
                month_orders.filter(status='Closed', days_taken=1).count() / total_orders
            )
            
            two_day_data.append(
                month_orders.filter(status='Closed', days_taken=2).count() / total_orders
            )
            
            three_day_data.append(
                month_orders.filter(status='Closed', days_taken=3).count() / total_orders
            )
            
            four_day_data.append(
                month_orders.filter(status='Closed', days_taken=4).count() / total_orders
            )
            
            five_day_data.append(
                month_orders.filter(status='Closed', days_taken=5).count() / total_orders
            )
            
            more_than_five_data.append(
                month_orders.filter(status='Closed', days_taken__gt=5).count() / total_orders
            )
        
        chart_data = {
            'labels': labels,
            'datasets': [
                {
                    'label': 'OpenWorkOrders',
                    'data': open_data,
                    'borderColor': 'rgb(255, 99, 132)',
                },
                {
                    'label': 'ClosedInSameDay',
                    'data': closed_same_day_data,
                    'borderColor': 'rgb(54, 162, 235)',
                },
                {
                    'label': 'OneDayWorkOrders',
                    'data': one_day_data,
                    'borderColor': 'rgb(255, 206, 86)',
                },
                {
                    'label': 'TwoDayWorkOrders',
                    'data': two_day_data,
                    'borderColor': 'rgb(75, 192, 192)',
                },
                {
                    'label': 'ThreeDayWorkOrders',
                    'data': three_day_data,
                    'borderColor': 'rgb(153, 102, 255)',
                },
                {
                    'label': 'FourDayWorkOrders',
                    'data': four_day_data,
                    'borderColor': 'rgb(255, 159, 64)',
                },
                {
                    'label': 'FiveDayWorkOrders',
                    'data': five_day_data,
                    'borderColor': 'rgb(0, 128, 0)',
                },
                {
                    'label': 'MoreThanFiveDays',
                    'data': more_than_five_data,
                    'borderColor': 'rgb(128, 0, 128)',
                },
            ]
        }
        
        return chart_data

class NewHireReport(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        work_status_data = NewHire.objects.values('work_status')\
            .annotate(count=Count('work_status'))\
            .order_by('work_status')
        
        # Convert queryset to a format suitable for template and chart
        status_labels = []
        status_counts = []
        table_data = []
        
        for item in work_status_data:
            status = item['work_status'] if item['work_status'] else 'null'
            count = item['count']
            
            status_labels.append(status)
            status_counts.append(count)
            table_data.append({
                'status': status,
                'count': count
            })
        
        companies = NewHire.objects.values_list('work_company_name', flat=True).distinct()
        
        projects_list = ProjectMaster.objects.annotate(
            total_arrived=Count('employees', filter=Q(employees__ArrivalStatus='Arrived'), distinct=True)
        )

        context = {
            'projects_names': projects_list,
            'work_status_data': table_data,
            'status_labels': status_labels,
            'status_counts': status_counts,
            'companies': companies,
            'start_date': '',
            'end_date': '',
            'selected_company': 'All'
        }
        
        return render(request, "new_hire_report.html", context)

    def post(self, request):
        # Get filter parameters
        start_date = request.POST.get('arrival_from', '')
        end_date = request.POST.get('arrival_to', '')
        company = request.POST.get('company', 'All')
        export_format = request.POST.get('export', None)
        
        # Start with all records
        queryset = NewHire.objects.all()
        
        # Apply filters if provided
        # if start_date:
        #     # Assuming you have a field for arrival date in your model
        #     # If not, you may need to adjust this filter
        #     queryset = queryset.filter(created_at__gte=start_date)
        
        # if end_date:
        #     queryset = queryset.filter(created_at__lte=end_date)
        
        if company and company != 'All':
            queryset = queryset.filter(work_company_name=company)
        
        # Get work status counts with applied filters
        work_status_data = queryset.values('work_status')\
            .annotate(count=Count('work_status'))\
            .order_by('work_status')
        
        # Convert queryset to a format suitable for template and chart
        status_labels = []
        status_counts = []
        table_data = []
        
        for item in work_status_data:
            status = item['work_status'] if item['work_status'] else 'null'
            count = item['count']
            
            status_labels.append(status)
            status_counts.append(count)
            table_data.append({
                'status': status,
                'count': count
            })
        
        # Handle export if requested
        if export_format == 'csv':
            return self.export_to_csv(table_data)
        
        # Get unique company names for the dropdown
        companies = NewHire.objects.values_list('work_company_name', flat=True).distinct()
        
        projects_list = ProjectMaster.objects.annotate(
            total_arrived=Count('employees', filter=Q(employees__ArrivalStatus='Arrived'), distinct=True)
        )

        context = {
            'projects_names': projects_list,
            'work_status_data': table_data,
            'status_labels': status_labels,
            'status_counts': status_counts,
            'companies': companies,
            'start_date': start_date,
            'end_date': end_date,
            'selected_company': company
        }
        
        return render(request, "new_hire_report.html", context)
    
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

class UpdateNewHireWorkStatusView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return render(request, "update_work_status.html")

class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
        return redirect('login')

class ManageEmployeeView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        context = {
            'uploaded_data': Employee.objects.all().order_by('-EmployeeId')[:20],
            'error_message': None,
            'invalid_data': False,
        }
        return render(request, 'manage_employee.html', context)

class BulkUploadWorkOrderView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        # for i in Employee.objects.all():
        #     print(i.EmployeeId)
        context = {
            'uploaded_data': WorkOrder.objects.all().order_by('-wo_id')[:20],
            'error_message': None,
            'invalid_data': False,
        }
        return render(request, 'workorder_bulk_upload.html', context)
    
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        context = {
            'uploaded_data': [],
            'error_message': None,
            'invalid_data': False,
        }
        context['uploaded_data'] = WorkOrder.objects.all().order_by('-wo_id')[:20]
        
        excel_file = request.FILES.get('excel_file')
        if not excel_file or not excel_file.name.endswith(('.xlsx', '.xls')):
            context['error_message'] = "Please upload a valid Excel file."
            return render(request, 'workorder_bulk_upload.html', context)
        
        try:
            df = pd.read_excel(excel_file)
            required_columns = {'wo_numeric_no', 'wo_no', 'employee_id', 'phone_no', 'camp_id', 'camp_name',
                                'building_id', 'project_id', 'building_code', 'apartment_id', 'apt_area',
                                'work_order_job_type_id', 'wo_description', 'requested_date', 'submitted_date',
                                'status', 'status_date', 'days_taken', 'remarks'}
            
            missing_columns = required_columns - set(df.columns)
            if missing_columns:
                print(missing_columns)
            #     context['error_message'] = f'Missing required columns: {", ".join(missing_columns)}'
            #     return render(request, 'manage_workorder.html', context)
            
            workorders_to_create = []
            for _, row in df.iterrows():
                # employee_id_value = row.get('EmployeeId')
                # employee_instance = Employee.objects.filter(EmployeeId=int(employee_id_value)) .first() if employee_id_value and str(employee_id_value).isdigit() else None

                workorders_to_create.append(
                    WorkOrder(
                        wo_numeric_no=row.get('WoNumericNo'),
                        wo_no=row.get('WoNo'),
                        employee_id=row.get('EmployeeId'),
                        phone_no=row.get('PhoneNo'),
                        camp_id=row.get('CampId'),
                        camp_name=row.get('CampName'),
                        building_id=row.get('BuildingId'),
                        project_id=row.get('ProjectId'),
                        building_code=row.get('BuildingCode'),
                        apartment_id=row.get('ApartmentId'),
                        apt_area=row.get('AptArea'),
                        work_order_job_type_id=row.get('WorkOrderJobTypeId'),
                        wo_description=row.get('WoDescription'),
                        requested_date=row.get('RequestedDate'),
                        submitted_date=row.get('SubmittedDate'),
                        status=row.get('Status'),
                        status_date=row.get('StatusDate'),
                        days_taken=row.get('DaysTaken'),
                        remarks=row.get('Remarks'),
                    )
                )
            
            WorkOrder.objects.bulk_create(workorders_to_create)
            context['uploaded_data'] = WorkOrder.objects.all().order_by('-wo_id')[:20]
            
        except Exception as e:
            context['error_message'] = f"Error processing file: {str(e)}"
        
        return render(request, 'workorder_bulk_upload.html', context)




  
  
        
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
 
class RecruitmentView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        job_list = JobMaster.objects.all().order_by('job_id')
    
        # Set up pagination
        page_size = request.GET.get('page_size', 10)
        paginator = Paginator(job_list, page_size)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        # Generate page range for display
        page_range = range(1, paginator.num_pages + 1)
        
        context = {
            'jobs': page_obj,
            'paginator': paginator,
            'page_obj': page_obj,
            'page_range': page_range,
            'page_size': int(page_size),
            'total_pages': paginator.num_pages,
        }
        
        return render(request, 'job_master.html', context)

    
class RecruitmentSummaryView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # employees_without_project = Employee.objects.filter(project__isnull=True)

        # # Randomly assign project (either 1 or 2) to them
        # project_choices = [1, 2]
        # for employee in employees_without_project:
        #     random_project_id = random.choice(project_choices)
        #     employee.project = ProjectMaster.objects.get(project_id=random_project_id)
        #     employee.save()

        projects_list = ProjectMaster.objects.annotate(
            total_arrived=Count('employees', filter=Q(employees__ArrivalStatus='Arrived'), distinct=True)
        )

        context = {
            'projects_names': projects_list,
            'projects_list': projects_list,
            'use_chart_js': True 
        }
        return render(request, 'recruitment_summary.html', context)
    
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Get filter parameters from request
        selected_projects = request.POST.getlist('projects')
        arrival_from = request.POST.get('arrival_from')
        arrival_to = request.POST.get('arrival_to')
        
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
        
        # Get all projects for the dropdown
        all_projects = ProjectMaster.objects.all()
        
        # Get filtered projects with count
        if query:
            projects_list = ProjectMaster.objects.filter(query).annotate(
                total_arrived=Count('employees', filter=arrival_status_query, distinct=True)
            )
        else:
            projects_list = ProjectMaster.objects.annotate(
                total_arrived=Count('employees', filter=arrival_status_query, distinct=True)
            )
        
        projects_names = ProjectMaster.objects.annotate(
            total_arrived=Count('employees', filter=Q(employees__ArrivalStatus='Arrived'), distinct=True)
        )
        context = {
            'projects_names': projects_names,
            'projects_list': projects_list,
            'all_projects': all_projects,
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
        
        # Create Excel export (requires xlsxwriter package)
        import xlsxwriter
        import io
        
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

class BulkUploadEmployeeView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        context = {
            'uploaded_data': [],
            'error_message': None,
            'invalid_data': False,
        }
        context['uploaded_data'] = Employee.objects.all().order_by('-EmployeeId')[:20]
        
        excel_file = request.FILES['excel_file']

        if not excel_file.name.endswith(('.xlsx', '.xls')):
            context['error_message'] = "Please upload a valid Excel file."
            return render(request, 'manage_employee.html', context)
        
        # if not excel_file.name.endswith(('.xlsx', '.xls')):
        #     return JsonResponse({'error': 'File is not an Excel format'}, status=400)
    
        try:
            df = pd.read_excel(excel_file)
            required_columns = {'AuthenticationId', 'PoolNo', 'ControlNo', 'Name', 'Gender',
                                'PassportNo', 'PassportPlaceOfIssue', 'DateOfBirth', 'NationalityId',
                                'ProjectId', 'NativeLicenceStatus', 'NativeLicenceIssueDate', 'NativeLicenceExpiryDate',
                                'IndiaLicenceStatus', 'IndiaLicenceIssueDate', 'IndiaLicenceExpiryDate',
                                'TradeCertificateStatus', 'TradeCertificateIssueDate', 'TrainingCertificateStatus',
                                'TrainingCertificateExpiryDate', 'JobTitleId', 'PoolSalary', 'AssignedSalary',
                                'RequestReceivedDate', 'RequiredJoiningDate', 'VacancyTypeId', 'AgencyId',
                                'DepartureLocation', 'NOCGivenForTypingDate', 'NOCTypeAndReceivedDate',
                                'AppSubmitToSponsorshipDate', 'NOCReceivedDate', 'VisaExpiryDate', 'VisaSendToAgencyDate',
                                'ArrivalDate', 'ArrivalTime', 'ArrivalStatus', 'CurrentStatusId', 'JoiningDate',
                                'RecruitmentRemarks', 'ProfilePhoto', 'EmployeeStatus', 'Salary', 'TotalSalary', 'TypeName'}
            
            # missing_columns = required_columns - set(df.columns)
            # if missing_columns:
            #     return JsonResponse({'error': f'Missing required columns: {", ".join(missing_columns)}'}, status=400)
            
            employees_to_create = []
            for _, row in df.iterrows():
                employees_to_create.append(
                    Employee(
                        AuthenticationId=row.get('AuthenticationId', None),
                        PoolNo=row.get('PoolNo', None),
                        ControlNo=row.get('ControlNo', None),
                        Name=row.get('Name', None),
                        Gender=row.get('Gender', None),
                        PassportNo=row.get('PassportNo', None),
                        PassportPlaceOfIssue=row.get('PassportPlaceOfIssue', None),
                        DateOfBirth=row.get('DateOfBirth', None),
                        NationalityId=row.get('NationalityId', None),
                        ProjectId=row.get('ProjectId', None),
                        NativeLicenceStatus=row.get('NativeLicenceStatus', None),
                        NativeLicenceIssueDate=row.get('NativeLicenceIssueDate', None),
                        NativeLicenceExpiryDate=row.get('NativeLicenceExpiryDate', None),
                        IndiaLicenceStatus=row.get('IndiaLicenceStatus', None),
                        IndiaLicenceIssueDate=row.get('IndiaLicenceIssueDate', None),
                        IndiaLicenceExpiryDate=row.get('IndiaLicenceExpiryDate', None),
                        TradeCertificateStatus=row.get('TradeCertificateStatus', None),
                        TradeCertificateIssueDate=row.get('TradeCertificateIssueDate', None),
                        TrainingCertificateStatus=row.get('TrainingCertificateStatus', None),
                        TrainingCertificateExpiryDate=row.get('TrainingCertificateExpiryDate', None),
                        JobTitleId=row.get('JobTitleId', None),
                        PoolSalary=row.get('PoolSalary', None),
                        AssignedSalary=row.get('AssignedSalary', None),
                        RequestReceivedDate=row.get('RequestReceivedDate', None),
                        RequiredJoiningDate=row.get('RequiredJoiningDate', None),
                        VacancyTypeId=row.get('VacancyTypeId', None),
                        AgencyId=row.get('AgencyId', None),
                        DepartureLocation=row.get('DepartureLocation', None),
                        NOCGivenForTypingDate=row.get('NOCGivenForTypingDate', None),
                        NOCTypeAndReceivedDate=row.get('NOCTypeAndReceivedDate', None),
                        AppSubmitToSponsorshipDate=row.get('AppSubmitToSponsorshipDate', None),
                        NOCReceivedDate=row.get('NOCReceivedDate', None),
                        VisaExpiryDate=row.get('VisaExpiryDate', None),
                        VisaSendToAgencyDate=row.get('VisaSendToAgencyDate', None),
                        ArrivalDate=row.get('ArrivalDate', None),
                        ArrivalTime=row.get('ArrivalTime', None),
                        ArrivalStatus=row.get('ArrivalStatus', None),
                        CurrentStatusId=row.get('CurrentStatusId', None),
                        JoiningDate=row.get('JoiningDate', None),
                        RecruitmentRemarks=row.get('RecruitmentRemarks', None),
                        ProfilePhoto=row.get('ProfilePhoto', None),
                        EmployeeStatus=row.get('EmployeeStatus', None),
                        Salary=row.get('Salary', None),
                        TotalSalary=row.get('TotalSalary', None),
                        TypeName=row.get('TypeName', None)
                    )
                )
            
            Employee.objects.bulk_create(employees_to_create)
            # return JsonResponse({'message': f'Successfully added {len(employees_to_create)} employees'}, status=201)
            
            context['uploaded_data'] = Employee.objects.all().order_by('-EmployeeId')[:20]

            # messages.success(request, f"Successfully uploaded {len(df)} employees.")
            
        except Exception as e:
            context['error_message'] = f"Error processing file: {str(e)}"
        
        return render(request, 'manage_employee.html', context)

class DownloadEmployeeExcelView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Fetch the latest 20 employees
        employees = Employee.objects.all().order_by('-EmployeeId')[:20]
        
        # Create a workbook and worksheet
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = "Employees"
        
        # Define headers from model fields
        headers = [
            'EmployeeId', 'AuthenticationId', 'PoolNo', 'ControlNo', 'Name', 'Gender',
            'PassportNo', 'PassportPlaceOfIssue', 'DateOfBirth', 'NationalityId', 'ProjectId',
            'NativeLicenceStatus', 'NativeLicenceIssueDate', 'NativeLicenceExpiryDate',
            'IndiaLicenceStatus', 'IndiaLicenceIssueDate', 'IndiaLicenceExpiryDate',
            'TradeCertificateStatus', 'TradeCertificateIssueDate', 'TrainingCertificateStatus',
            'TrainingCertificateExpiryDate', 'JobTitleId', 'PoolSalary', 'AssignedSalary',
            'RequestReceivedDate', 'RequiredJoiningDate', 'VacancyTypeId', 'AgencyId',
            'DepartureLocation', 'NOCGivenForTypingDate', 'NOCTypeAndReceivedDate',
            'AppSubmitToSponsorshipDate', 'NOCReceivedDate', 'VisaExpiryDate', 'VisaSendToAgencyDate',
            'ArrivalDate', 'ArrivalTime', 'ArrivalStatus', 'CurrentStatusId', 'JoiningDate',
            'RecruitmentRemarks', 'ProfilePhoto', 'EmployeeStatus', 'Salary', 'TotalSalary',
            'TypeName', 'created_at', 'updated_at'
        ]
        
        # Add headers to worksheet
        for col_num, header in enumerate(headers, 1):
            worksheet.cell(row=1, column=col_num, value=header)
        
        # Populate employee data
        for row_num, employee in enumerate(employees, 2):
            data = [
                employee.EmployeeId, employee.AuthenticationId, employee.PoolNo, employee.ControlNo, employee.Name, employee.Gender,
                employee.PassportNo, employee.PassportPlaceOfIssue, employee.DateOfBirth, employee.NationalityId, employee.ProjectId,
                employee.NativeLicenceStatus, employee.NativeLicenceIssueDate, employee.NativeLicenceExpiryDate,
                employee.IndiaLicenceStatus, employee.IndiaLicenceIssueDate, employee.IndiaLicenceExpiryDate,
                employee.TradeCertificateStatus, employee.TradeCertificateIssueDate, employee.TrainingCertificateStatus,
                employee.TrainingCertificateExpiryDate, employee.JobTitleId, employee.PoolSalary, employee.AssignedSalary,
                employee.RequestReceivedDate, employee.RequiredJoiningDate, employee.VacancyTypeId, employee.AgencyId,
                employee.DepartureLocation, employee.NOCGivenForTypingDate, employee.NOCTypeAndReceivedDate,
                employee.AppSubmitToSponsorshipDate, employee.NOCReceivedDate, employee.VisaExpiryDate, employee.VisaSendToAgencyDate,
                employee.ArrivalDate, employee.ArrivalTime.replace(tzinfo=None) if employee.ArrivalTime else None, 
                employee.ArrivalStatus, employee.CurrentStatusId, employee.JoiningDate,
                employee.RecruitmentRemarks, employee.ProfilePhoto, employee.EmployeeStatus, employee.Salary, employee.TotalSalary,
                employee.TypeName, 
                employee.created_at.replace(tzinfo=None) if employee.created_at else None, 
                employee.updated_at.replace(tzinfo=None) if employee.updated_at else None
            ]
            
            for col_num, value in enumerate(data, 1):
                worksheet.cell(row=row_num, column=col_num, value=value)
        
        # Create HTTP response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=employee_data.xlsx'
        
        # Save workbook to response
        workbook.save(response)
        
        return response

class CurrentStatusView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        # currentstatus_list = CurrentStatus.objects.all()
        currentstatus_list = []
        return render(request, 'current_status_master.html', {
            'currentstatus_list': currentstatus_list
        })

class NewHireManagementView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Handle search/filter parameters
        search_by = request.GET.get('search_by', '')
        search_term = request.GET.get('search_term', '')
        # nationality = request.GET.get('nationality', '')
        project_id = request.GET.get('project', '')
        # gender = request.GET.get('gender', '')
        work_status = request.GET.get('work_status', '')
        
        # Fetch new hires with filters
        new_hires = NewHire.objects.all()
        
        # Apply filters based on parameters
        if search_term and search_by:
            if search_by == 'pool_no':
                new_hires = new_hires.filter(pool_no__icontains=search_term)
            elif search_by == 'name':
                new_hires = new_hires.filter(name__icontains=search_term)
            elif search_by == 'email':
                new_hires = new_hires.filter(email__icontains=search_term)
        
        # if nationality:
        #     new_hires = new_hires.filter(nationality=nationality)
        
        if project_id:
            new_hires = new_hires.filter(project_id=project_id)
        
        # if gender:
        #     new_hires = new_hires.filter(gender=gender)
        
        if work_status:
            new_hires = new_hires.filter(work_status=work_status)
        
        # Pagination
        paginator = Paginator(new_hires, 10)  # Show 10 records per page
        page = request.GET.get('page')
        new_hires = paginator.get_page(page)
        
        # Get all projects for dropdown
        projects = ProjectMaster.objects.all()
        
        context = {
            'new_hires': new_hires,
            'projects': projects,
        }
        
        return render(request, 'new_hire_management.html', context)

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
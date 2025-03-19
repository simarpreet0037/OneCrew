# views.py
from django.shortcuts import render
from django.db.models import Count, Sum
from django.views import View
from .models import ProjectMaster, JobMaster, Employee, NewHire, WorkOrder, User

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


#Merge here from Views file



def bulk_upload_employee(request):
    if request.method == 'POST':
        form = BulkUploadEmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            upload_option = form.cleaned_data['upload_option']
            
            # Read the Excel file
            df = pd.read_excel(BytesIO(excel_file.read()))
            
            # Process the data
            for index, row in df.iterrows():
                if upload_option == 'New':
                    Employee.objects.create(
                        authentication_id=row['AutheticationId'],
                        pool_no=row['PoolNo'],
                        control_no=row['ControlNo'],
                        name=row['Name'],
                        gender=row['Gender'],
                        passport_no=row['PassportNo'],
                        passport_place_of_issue=row['PassportPlaceOfIssue'],
                        date_of_birth=row['DateOfBirth'],
                        nationality=row['Nationality'],
                        project=row['Project'],
                        native_license_status=row['NativeLicenseStatus'],
                        native_license_issue_date=row['NativeLicenseIssuedDate'],
                        native_license_expiry_date=row['NativeLicenseExpiryDate'],
                        kuwait_license_status=row['KuwaitLicenseStatus'],
                        kuwait_license_issue_date=row['KuwaitLicenseIssuedDate'],
                        kuwait_license_expiry_date=row['KuwaitLicenseExpiryDate'],
                        operator_license_status=row['OperatorLicenseStatus'],
                        operator_license_issue_date=row['OperatorLicenseIssuedDate'],
                        operator_license_expiry_date=row['OperatorLicenseExpiryDate'],
                        trade_certificate_status=row['TradeCertificateStatus'],
                        trade_certificate_issue_date=row['TradeCertificateIssuedDate'],
                        training_certificate_status=row['TrainingCertificateStatus'],
                        training_certificate_issue_date=row['TrainingCertificateIssuedDate'],
                        job_title=row['JobTitle'],
                        pool_salary=row['PoolSalary'],
                        assigned_salary=row['AssignedSalary'],
                        request_received_date=row['RequestReceivedDate'],
                        required_joining_date=row['RequiredJoiningDate'],
                        vacancy_type=row['VacancyType'],
                        agency_name=row['AgencyName'],
                        departure_location=row['DepartureLocation'],
                        noc_given_for_typing_date=row['NocGivenForTypingDate'],
                        noc_typed_and_received_date=row['NocTypedAndReceivedDate'],
                        airlines=row['Airlines'],
                        gp_requested_date=row['GpRequestedDate'],
                        gp_received_date=row['GpReceivedDate'],
                        gp_number=row['GpNumber'],
                        gp_arrival_date=row['GpArrivalDate'],
                        app_submit_to_sponsorship_date=row['AppSubmit'],
                        mosal_file=row['MosalFile'],
                        noc1_received_date=row['Noc1ReceivedDate'],
                        noc1_no=row['Noc1No'],
                        noc2_received_date=row['Noc2ReceivedDate'],
                        noc2_reapply_date=row['Noc2ReApplyDate'],
                        visa_expiry_date=row['VisaExpiryDate'],
                        visa_send_to_agency_date=row['VisaSendToAgencyDate'],
                        arrival_date=row['ArrivalDate'],
                        arrival_time=row['ArrivalTime'],
                        arrival_status=row['ArrivalStatus'],
                        current_status=row['CurrentStatus'],
                        joining_date=row['JoiningDate'],
                        recruitment_remarks=row['RecruitmentRemarks'],
                        profile_photo=row['ProfilePhoto'],
                        employee_status=row['EmployeeStatus'],
                        salary=row['Salary'],
                        allowance=row['Allowance'],
                        total_salary=row['TotalSalary'],
                        type_name=row['Type'],
                        created_by=request.user
                    )
                elif upload_option == 'Update':
                    employee = Employee.objects.filter(passport_no=row['PassportNo']).first()
                    if employee:
                        for field in row.index:
                            setattr(employee, field.lower(), row[field])
                        employee.save()
            
            messages.success(request, 'Employees uploaded successfully.')
            return redirect('uploaded_data_list')
    else:
        form = BulkUploadEmployeeForm()
    
    return render(request, 'recruitment/bulk_upload_employee.html', {'form': form})

def uploaded_data_list(request):
    employees = Employee.objects.all()
    return render(request, 'recruitment/uploaded_data_list.html', {'employees': employees})


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


#Merge here from Views file

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import BulkUploadEmployeeForm
from .models import Employee
import pandas as pd
from io import BytesIO

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


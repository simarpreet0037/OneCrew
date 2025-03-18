# Create your models here.
# models.py
from django.db import models

class ProjectMaster(models.Model):
    ProjectId = models.AutoField(primary_key=True)
    ProjectName = models.CharField(max_length=255)

class JobMaster(models.Model):
    JobId = models.AutoField(primary_key=True)
    JobName = models.CharField(max_length=255)

class CampMaster(models.Model):
    CampId = models.AutoField(primary_key=True)
    CampName = models.CharField(max_length=255)

class ManningReport(models.Model):
    ManningReportId = models.AutoField(primary_key=True)
    ProjectName = models.CharField(max_length=255)
    OnGround = models.IntegerField()
    Backfill = models.IntegerField()
    Additional = models.IntegerField()
    Vacancy = models.IntegerField()
    Total = models.IntegerField()

class WorkOrder(models.Model):
    WorkOrderId = models.AutoField(primary_key=True)
    CampId = models.ForeignKey(CampMaster, on_delete=models.CASCADE)
    OpenWorkOrders = models.IntegerField()
    ClosedInSameDay = models.IntegerField()
    ClosedInOneDay = models.IntegerField()
    ClosedInTwoDay = models.IntegerField()
    ClosedInThreeDay = models.IntegerField()
    ClosedInFourDay = models.IntegerField()
    ClosedInFiveDay = models.IntegerField()
    ClosedInMoreThanFiveDay = models.IntegerField()
    TotalWorkOrders = models.IntegerField()
    CompletionRate = models.FloatField()


#Merge from new hire models file

# newhire/models.py
from django.db import models

class Nationality(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Project(models.Model):
    name = models.CharField(max_length=100)
    company = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Job(models.Model):
    name = models.CharField(max_length=100)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
class Employee(models.Model):
    pool_no = models.CharField(max_length=100)
    control_no = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    passport_no = models.CharField(max_length=100)
    nationality = models.ForeignKey(Nationality, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    arrival_date = models.DateField()
    profile_photo = models.ImageField(upload_to='employee_profiles/', null=True, blank=True)
    arrived_salary = models.DecimalField(max_digits=10, decimal_places=2)
    native_language = models.CharField(max_length=100)
    education = models.CharField(max_length=100)
    marital_status = models.CharField(max_length=20, choices=[('Single', 'Single'), ('Married', 'Married'), ('Divorced', 'Divorced')])
    religion = models.CharField(max_length=50, choices=[('Buddhist', 'Buddhist'), ('Christian', 'Christian'), ('Hindu', 'Hindu'), ('Muslim', 'Muslim'), ('Sikh', 'Sikh')])
    food_type = models.CharField(max_length=20, choices=[('Veg', 'Veg'), ('Non Veg', 'Non Veg')])
    home_address = models.TextField()
    nok_name = models.CharField(max_length=100)
    nok_phone = models.CharField(max_length=20)
    nok_relation = models.CharField(max_length=100)
    email = models.EmailField()
    city_of_birth = models.CharField(max_length=100)
    work_status = models.CharField(max_length=20, choices=[('Assigned', 'Assigned'), ('Not Assigned', 'Not Assigned'), ('Inactive', 'Inactive')])
    remarks = models.TextField()
    camp = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

#Merge from Bulkupload models file

from django.db import models

class Employee(models.Model):
    authentication_id = models.CharField(max_length=100)
    pool_no = models.CharField(max_length=100)
    control_no = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    gender = models.CharField(max_length=10)
    passport_no = models.CharField(max_length=100)
    passport_place_of_issue = models.CharField(max_length=200)
    date_of_birth = models.DateField()
    nationality = models.CharField(max_length=100)
    project = models.CharField(max_length=200)
    native_license_status = models.CharField(max_length=100)
    native_license_issue_date = models.DateField(null=True, blank=True)
    native_license_expiry_date = models.DateField(null=True, blank=True)
    kuwait_license_status = models.CharField(max_length=100)
    kuwait_license_issue_date = models.DateField(null=True, blank=True)
    kuwait_license_expiry_date = models.DateField(null=True, blank=True)
    operator_license_status = models.CharField(max_length=100)
    operator_license_issue_date = models.DateField(null=True, blank=True)
    operator_license_expiry_date = models.DateField(null=True, blank=True)
    trade_certificate_status = models.CharField(max_length=100)
    trade_certificate_issue_date = models.DateField(null=True, blank=True)
    training_certificate_status = models.CharField(max_length=100)
    training_certificate_issue_date = models.DateField(null=True, blank=True)
    job_title = models.CharField(max_length=200)
    pool_salary = models.DecimalField(max_digits=10, decimal_places=2)
    assigned_salary = models.DecimalField(max_digits=10, decimal_places=2)
    request_received_date = models.DateField(null=True, blank=True)
    required_joining_date = models.DateField(null=True, blank=True)
    vacancy_type = models.CharField(max_length=100)
    agency_name = models.CharField(max_length=200)
    departure_location = models.CharField(max_length=200)
    noc_given_for_typing_date = models.DateField(null=True, blank=True)
    noc_typed_and_received_date = models.DateField(null=True, blank=True)
    airlines = models.CharField(max_length=100)
    gp_requested_date = models.DateField(null=True, blank=True)
    gp_received_date = models.DateField(null=True, blank=True)
    gp_number = models.CharField(max_length=100)
    gp_arrival_date = models.DateField(null=True, blank=True)
    app_submit_to_sponsorship_date = models.DateField(null=True, blank=True)
    mosal_file = models.CharField(max_length=100)
    noc1_received_date = models.DateField(null=True, blank=True)
    noc1_no = models.CharField(max_length=100)
    noc2_received_date = models.DateField(null=True, blank=True)
    noc2_reapply_date = models.DateField(null=True, blank=True)
    visa_expiry_date = models.DateField(null=True, blank=True)
    visa_send_to_agency_date = models.DateField(null=True, blank=True)
    arrival_date = models.DateField(null=True, blank=True)
    arrival_time = models.TimeField(null=True, blank=True)
    arrival_status = models.CharField(max_length=100)
    current_status = models.CharField(max_length=100)
    joining_date = models.DateField(null=True, blank=True)
    recruitment_remarks = models.TextField()
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    employee_status = models.BooleanField(default=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    allowance = models.DecimalField(max_digits=10, decimal_places=2)
    total_salary = models.DecimalField(max_digits=10, decimal_places=2)
    type_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


#
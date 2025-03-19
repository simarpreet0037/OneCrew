# Create your models here.
# models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Creates and returns a user with an email and password."""
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Creates and returns a superuser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class ProjectMaster(models.Model):
    project_id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=50)
    project_company = models.CharField(max_length=50)
    project_status = models.BooleanField(default=False)

    def __str__(self):
        return self.project_name

class JobMaster(models.Model):
    job_id = models.AutoField(primary_key=True)
    project = models.ForeignKey(ProjectMaster, on_delete=models.CASCADE)
    job_name = models.CharField(max_length=50)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # Add this
    created_date = models.DateTimeField(auto_now_add=True)  # Add this

    def __str__(self):
        return self.job_name




class WorkOrder(models.Model):
    wo_id = models.AutoField(primary_key=True)
    wo_numeric_no = models.IntegerField(blank=True, null=True)
    wo_no = models.CharField(max_length=50, blank=True, null=True)
    employee_id = models.IntegerField(blank=True, null=True)
    phone_no = models.CharField(max_length=50, blank=True, null=True)
    camp_id = models.IntegerField(blank=True, null=True)
    camp_name = models.CharField(max_length=50, blank=True, null=True)
    building_id = models.IntegerField(blank=True, null=True)
    project_id = models.IntegerField(blank=True, null=True)
    building_code = models.CharField(max_length=50, blank=True, null=True)
    apartment_id = models.IntegerField(blank=True, null=True)
    apt_area = models.CharField(max_length=200, blank=True, null=True)
    work_order_job_type_id = models.IntegerField(blank=True, null=True)
    wo_description = models.TextField(blank=True, null=True)
    requested_date = models.DateField(blank=True, null=True)
    submitted_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    status_date = models.DateField(blank=True, null=True)
    days_taken = models.IntegerField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"WorkOrder {self.wo_no} ({self.status})"

    
class Employee(models.Model):
    EmployeeId = models.AutoField(primary_key=True)
    project = models.ForeignKey(ProjectMaster, on_delete=models.CASCADE, related_name="employees", null=True, blank=True)
    AuthenticationId = models.CharField(max_length=100, null=True, blank=True)
    PoolNo = models.CharField(max_length=50, null=True, blank=True)
    ControlNo = models.CharField(max_length=50, null=True, blank=True)
    Name = models.CharField(max_length=100, null=True, blank=True)
    Gender = models.CharField(max_length=50, null=True, blank=True)
    PassportNo = models.CharField(max_length=50, null=True, blank=True)
    PassportPlaceOfIssue = models.CharField(max_length=50, null=True, blank=True)
    DateOfBirth = models.DateField(null=True, blank=True)
    NationalityId = models.IntegerField(null=True, blank=True)
    ProjectId = models.IntegerField(null=True, blank=True)
    NativeLicenceStatus = models.CharField(max_length=50, null=True, blank=True)
    NativeLicenceIssueDate = models.DateField(null=True, blank=True)
    NativeLicenceExpiryDate = models.DateField(null=True, blank=True)
    IndiaLicenceStatus = models.CharField(max_length=50, null=True, blank=True)
    IndiaLicenceIssueDate = models.DateField(null=True, blank=True)
    IndiaLicenceExpiryDate = models.DateField(null=True, blank=True)
    TradeCertificateStatus = models.CharField(max_length=50, null=True, blank=True)
    TradeCertificateIssueDate = models.DateField(null=True, blank=True)
    TrainingCertificateStatus = models.CharField(max_length=50, null=True, blank=True)
    TrainingCertificateExpiryDate = models.DateField(null=True, blank=True)
    JobTitleId = models.IntegerField(null=True, blank=True)
    PoolSalary = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    AssignedSalary = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    RequestReceivedDate = models.DateField(null=True, blank=True)
    RequiredJoiningDate = models.DateField(null=True, blank=True)
    VacancyTypeId = models.IntegerField(null=True, blank=True)
    AgencyId = models.IntegerField(null=True, blank=True)
    DepartureLocation = models.CharField(max_length=50, null=True, blank=True)
    NOCGivenForTypingDate = models.DateField(null=True, blank=True)
    NOCTypeAndReceivedDate = models.DateField(null=True, blank=True)
    AppSubmitToSponsorshipDate = models.DateField(null=True, blank=True)
    NOCReceivedDate = models.DateField(null=True, blank=True)
    VisaExpiryDate = models.DateField(null=True, blank=True)
    VisaSendToAgencyDate = models.DateField(null=True, blank=True)
    ArrivalDate = models.DateField(null=True, blank=True)
    ArrivalTime = models.TimeField(null=True, blank=True)
    ArrivalStatus = models.CharField(max_length=50, null=True, blank=True)
    CurrentStatusId = models.IntegerField(null=True, blank=True)
    JoiningDate = models.DateField(null=True, blank=True)
    RecruitmentRemarks = models.CharField(max_length=100, null=True, blank=True)
    ProfilePhoto = models.CharField(max_length=500, null=True, blank=True)
    EmployeeStatus = models.BooleanField(null=True, blank=True)
    Salary = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    TotalSalary = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    TypeName = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.Name if self.Name else f"Employee {self.EmployeeId}"

class NewHire(models.Model):
    new_hire_id = models.AutoField(primary_key=True)
    # employee_id = models.IntegerField()
    employee_id = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    # work_company_id = models.IntegerField()
    work_company_name = models.CharField(max_length=100)
    arrived_salary = models.DecimalField(max_digits=18, decimal_places=2)
    # native_language_id = models.IntegerField()
    native_language = models.CharField(max_length=100)
    education = models.CharField(max_length=100)
    marital_status = models.CharField(max_length=50)
    religion = models.CharField(max_length=50)
    food_type = models.CharField(max_length=50)
    home_address = models.CharField(max_length=400)
    email_id = models.EmailField(max_length=50)
    city_of_birth = models.CharField(max_length=50)
    work_status = models.CharField(max_length=50)
    remark = models.CharField(max_length=50)
    camp_id = models.IntegerField()

    def __str__(self):
        return f"{self.new_hire_id} - {self.employee_id}"
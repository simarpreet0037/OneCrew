from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# --------------------- Custom User Model ---------------------
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

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

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

# --------------------- Project Model ---------------------
class ProjectMaster(models.Model):
    project_id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=50)
    project_company = models.CharField(max_length=50)
    project_status = models.BooleanField(default=False)

    def __str__(self):
        return self.project_name

# --------------------- Job Model ---------------------
class JobMaster(models.Model):
    job_id = models.AutoField(primary_key=True)
    project = models.ForeignKey(ProjectMaster, on_delete=models.CASCADE, related_name="jobs")
    job_name = models.CharField(max_length=50)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.job_name

# --------------------- Employee Model ---------------------
class Employee(models.Model):
    employee_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name="employee",
        null=True, 
        blank=True
    )
    project = models.ForeignKey(ProjectMaster, on_delete=models.CASCADE, related_name="employees", null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=50, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    passport_no = models.CharField(max_length=50, null=True, blank=True)
    native_license_status = models.CharField(max_length=50, null=True, blank=True)
    assigned_salary = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    recruitment_remarks = models.CharField(max_length=100, null=True, blank=True)
    employee_status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name if self.name else f"Employee {self.employee_id}"
    
# --------------------- Employee Factory Model ---------------------
class EmployeeFactory:
    """Factory class to create Employee objects with predefined attributes based on role."""

    ROLE_DEFAULTS = {
        "worker": {"assigned_salary": 30000.00, "employee_status": True},
        "manager": {"assigned_salary": 80000.00, "employee_status": True},
        "supervisor": {"assigned_salary": 60000.00, "employee_status": True},
    }

    @staticmethod
    def create_employee(user, role="worker", name="New Employee", **kwargs):
        """Creates an Employee with default attributes based on the role."""
        if role not in EmployeeFactory.ROLE_DEFAULTS:
            raise ValueError(f"Invalid role: {role}. Choose from {list(EmployeeFactory.ROLE_DEFAULTS.keys())}")

        # Merge default values with user-provided kwargs
        employee_data = {**EmployeeFactory.ROLE_DEFAULTS[role], "user": user, "name": name, **kwargs}

        return Employee.objects.create(**employee_data)

# --------------------- Work Order Model ---------------------
class WorkOrder(models.Model):
    STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    wo_id = models.AutoField(primary_key=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    days_taken = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="work_orders")
    project = models.ForeignKey(ProjectMaster, on_delete=models.CASCADE, related_name="work_orders", blank=True, null=True)
    job = models.ForeignKey(JobMaster, on_delete=models.CASCADE, related_name="work_orders", blank=True, null=True)
    worker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="worker_work_orders")
    wo_description = models.TextField(blank=True, null=True)
    requested_date = models.DateField(blank=True, null=True)
    submitted_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated')
    status_date = models.DateField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"WorkOrder {self.wo_no} ({self.get_status_display()})"
    
class WorkOrderFactory:
    @staticmethod
    def create_work_order(job, user, address=""):
        """
        Factory method to create a work order with consistent initialization.
        The only dynamic field at creation is `address`, the rest are prefilled.
        """
        return WorkOrder.objects.create(
            project=job.project,  # Ensure the project is assigned
            job=job,  # Ensure the job is assigned
            user=user,  # Ensure the user is assigned
            wo_description=f"Work order for {job.job_name}",
            requested_date=job.created_date,
            address=address,  # Dynamically set address
            days_taken=None,
            worker=None,
            submitted_date=None,
            status='initiated',
            remarks='',
        )

# --------------------- New Hire Model ---------------------
class NewHire(models.Model):
    employee_id = models.IntegerField()
    new_hire_id = models.AutoField(primary_key=True)
    employee_fk = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    work_company_name = models.CharField(max_length=100)
    arrived_salary = models.DecimalField(max_digits=18, decimal_places=2)
    native_language = models.CharField(max_length=100)
    education = models.CharField(max_length=100)
    marital_status = models.CharField(max_length=50)
    religion = models.CharField(max_length=50)
    food_type = models.CharField(max_length=50)
    home_address = models.CharField(max_length=400)
    email_id = models.EmailField(max_length=50)
    city_of_birth = models.CharField(max_length=50)
    work_status = models.CharField(max_length=50)
    remark = models.TextField()
    camp_id = models.IntegerField()

    def __str__(self):
        return f"{self.new_hire_id} - {self.employee}"
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin



from django.db import models
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from email.mime.image import MIMEImage
import os
import json
from abc import ABC, abstractmethod



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
    native_license_expiry = models.DateField(null=True, blank=True)
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

# =============================
# Abstract Observer Class
# =============================

class Observer(ABC):
    """Abstract Observer class that defines the update method."""
    
    @abstractmethod
    def update(self, work_order):
        pass

# =============================
# WorkOrder Model (Observable)
# =============================

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
    project = models.ForeignKey("ProjectMaster", on_delete=models.CASCADE, related_name="work_orders", blank=True, null=True)
    job = models.ForeignKey("JobMaster", on_delete=models.CASCADE, related_name="work_orders", blank=True, null=True)
    worker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="worker_work_orders")
    wo_description = models.TextField(blank=True, null=True)
    requested_date = models.DateField(blank=True, null=True)
    submitted_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated')
    status_date = models.DateField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    _observers = []  # List to store observers

    def __str__(self):
        return f"WorkOrder {self.wo_id} ({self.get_status_display()})"

    # Attach an observer
    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    # Detach an observer
    def detach(self, observer):
        if observer in self._observers:
            self._observers.remove(observer)

    # Notify all observers
    def notify(self):
        for observer in self._observers:
            observer.update(self)

    def save(self, *args, **kwargs):
        """
        Override save method to notify observers whenever a WorkOrder is updated.
        """
        super().save(*args, **kwargs)  # Save the object first
        self.notify()  # Notify observers after save





# =============================
# Email Notification Observer
# =============================

class Notification(Observer):
    """Observer that sends an email when a WorkOrder is updated."""

    _last_notified_states = {}  # Dictionary to store last notified state per WorkOrder

    def update(self, work_order):
        work_order_id = work_order.wo_id
        
        # Get last notified state
        last_state = self._last_notified_states.get(work_order_id, {})

        # Extract the current state
        current_state = {
            "title": work_order.wo_description,
            "address": work_order.address,
            "status": work_order.status,
            "assigned_to": work_order.worker.employee.name if work_order.worker else None,
            "email": work_order.worker.email if work_order.worker else None  # Fetching email from worker
}

        # Check if WorkOrder has changed
        if last_state != current_state:
            print(f"Changes detected in WorkOrder {work_order.wo_id}. Sending email notification.")

            subject = f"Work Order Updated: {work_order.project}".replace("\r", "").replace("\n", "")
            html_content = render_to_string('email/email_template.html', {'work_order': work_order})
            text_content = strip_tags(html_content)

            if work_order.worker and work_order.worker.email:
                email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [work_order.worker.email])
                email.attach_alternative(html_content, "text/html")

                # Attach footer banner image as inline image
                image_path = os.path.join(settings.STATICFILES_DIRS[0], "dashboard/footer_banner.jpg")

                try:
                    with open(image_path, 'rb') as img:
                        mime_image = MIMEImage(img.read(), _subtype="jpg")
                        mime_image.add_header('Content-ID', '<footer_banner>')
                        mime_image.add_header("Content-Disposition", "inline", filename="footer_banner.jpg")
                        email.attach(mime_image)
                except FileNotFoundError:
                    print("Warning: Footer banner image not found!")

                email.send()

            # Update the last notified state
            self._last_notified_states[work_order_id] = current_state
        else:
            print(f"No significant changes detected for WorkOrder {work_order.wo_id}. No email sent.")

# =============================
# Dashboard Notification Observer
# =============================
from django.http import StreamingHttpResponse,JsonResponse
import json
import time
class DashNotification(Observer):
    """Stores the latest WorkOrder update per user for AJAX requests."""
    
    _latest_updates = {}  # Stores the latest update per user
    
    @staticmethod
    def update(work_order):
        """Update the latest work order change per user."""
        if not work_order.worker:
            return

        user_email = work_order.worker.email  # Identifying user by email
        current_state = {
            "work_order_id": work_order.wo_id,
            "status": work_order.get_status_display(),
            "job_name": work_order.job.job_name if work_order.job else "No Job",
            "wo_description": work_order.wo_description,
            "remarks": work_order.remarks,
            "address": work_order.address,
            "assigned_by": work_order.user.email if work_order.user else "Admin",
            "submitted_date": work_order.submitted_date.strftime('%Y-%m-%d') if work_order.submitted_date else "Pending",
        }

        # Store the latest update per user
        DashNotification._latest_updates[user_email] = current_state

from django.contrib.auth.decorators import login_required
@login_required
def get_latest_work_order(request):
    """Fetch the most recent work order assigned to the logged-in user."""
    user = request.user

    # Get the most recent work order assigned to the user (sorted by created_at)
    latest_work_order = WorkOrder.objects.filter(worker=user).order_by('-created_at').first()

    if latest_work_order:
        work_order_data = {
            "work_order_id": latest_work_order.wo_id,
            "status": latest_work_order.get_status_display(),
            "job_name": latest_work_order.job.job_name if latest_work_order.job else "No Job",
            "wo_description": latest_work_order.wo_description,
            "remarks": latest_work_order.remarks,
            "address": latest_work_order.address,
            "assigned_by": latest_work_order.user.email if latest_work_order.user else "Admin",
            "submitted_date": latest_work_order.submitted_date.strftime('%Y-%m-%d') if latest_work_order.submitted_date else "Pending",
        }
        return JsonResponse(work_order_data)
    
    return JsonResponse({"message": "No work orders found"})
    
# =============================
# WorkOrder Factory (Auto-Attaching Observers)
# =============================

class WorkOrderFactory:
    @staticmethod
    def create_work_order(job, user, address=""):
        """
        Factory method to create a work order with consistent initialization.
        """
        work_order = WorkOrder.objects.create(
            project=job.project,
            job=job,
            user=user,
            wo_description=f"Work order for {job.job_name}",
            requested_date=job.created_date,
            address=address,
            days_taken=None,
            worker=None,
            submitted_date=None,
            status='initiated',
            remarks='',
        )

        # Attach Observers
        notification_observer = Notification()
        dash_notification_observer = DashNotification()

        work_order.attach(notification_observer)  # Attach email notifications
        work_order.attach(dash_notification_observer)  # Attach JSON notifications

        return work_order
    


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
    


class BaseUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    user_type = models.CharField(max_length=20, default="generic")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.user_type.capitalize()} - {self.email}"
    

class AdminUser(BaseUser):
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.user_type = "admin"
        self.is_staff = True
        super().save(*args, **kwargs)


class WorkerUser(BaseUser):
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.user_type = "customer"
        self.is_staff = False
        super().save(*args, **kwargs)

class UserFactory:
    @staticmethod
    def create_user(user_type: str, email: str, password: str, **extra_fields) -> BaseUser:
        if user_type == "admin":
            user = AdminUser(email=email, **extra_fields)
        elif user_type == "customer":
            user = CustomerUser(email=email, **extra_fields)
        else:
            user = BaseUser(email=email, **extra_fields)

        user.set_password(password)
        user.save()
        return user
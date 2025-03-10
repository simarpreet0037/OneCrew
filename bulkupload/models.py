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

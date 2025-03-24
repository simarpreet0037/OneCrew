from .models import Employee, NewHire
from dashboard.models import JobMaster, ProjectMaster, WorkOrder

class EmployeeUploadForm(forms.Form):
    excel_file = forms.FileField(
        label='Select a Valid Excel File To Upload:',
        widget=forms.FileInput(attrs={'accept': '.xlsx, .xls'}),
    )
    
from django import forms
from .models import Employee

#User = get_user_model()

class EmployeeProfileForm(forms.ModelForm):
    """
    Form for users to update their own employee profile, including email and password.
    """
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(
        required=False, 
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter new password'})
    )
    password2 = forms.CharField(
        required=False, 
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'})
    )

    class Meta:
        model = Employee
        fields = [
            'name', 'gender', 'date_of_birth', 'passport_no',
            'native_license_expiry', 'recruitment_remarks'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'native_license_expiry': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Retrieve user instance
        super(EmployeeProfileForm, self).__init__(*args, **kwargs)

        if user:
            self.fields['email'].initial = user.email  # Prepopulate email field

        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['gender'].widget.attrs.update({'class': 'form-select'})
        self.fields['passport_no'].widget.attrs.update({'class': 'form-control'})
        self.fields['recruitment_remarks'].widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.exclude(pk=self.instance.user.pk).filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        employee = super().save(commit=False)
        user = employee.user

        # Update email
        user.email = self.cleaned_data["email"]
        user.save()

        # Update password if provided
        password1 = self.cleaned_data.get("password1")
        if password1:
            user.set_password(password1)
            user.save()

        if commit:
            employee.save()

        return employee
class JobMasterForm(forms.ModelForm):
    project = forms.ModelChoiceField(
        queryset=ProjectMaster.objects.all(),
        empty_label="Select a Project",
        required=True
    )

    class Meta:
        model = JobMaster
        fields = ['job_name', 'project']


# create a project
from django import forms
from dashboard.models import ProjectMaster

class ProjectMasterForm(forms.ModelForm):
    class Meta:
        model = ProjectMaster
        fields = ['project_name', 'project_company', 'project_status']

class InitiateWorkOrderForm(forms.ModelForm):
    class Meta:
        model = WorkOrder
        fields = ['worker', 'address', 'wo_description', 'requested_date']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Get the logged-in user
        job = kwargs.pop('job', None)  # Get the job passed to the form
        super(InitiateWorkOrderForm, self).__init__(*args, **kwargs)

        if user:
            self.instance.user = user  # Auto-assign manager (current user)
        
        if job:
            self.instance.project = job.project  # Assign the project from the job
            self.instance.job = job  # Assign the job


class CompleteWorkOrderForm(forms.ModelForm):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.HiddenInput(),  # Hide the default dropdown
        required=True
    )

    class Meta:
        model = WorkOrder
        fields = ['worker', 'submitted_date', 'status', 'remarks']

        widgets = {
            'worker': forms.Select(attrs={'class': 'form-select'}),
            'submitted_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


# forms.py for sign-up
from django import forms
from django.contrib.auth import get_user_model
from OneCrew.settings import SIGNUP_SECRET_KEY

User = get_user_model()

class SignupForm(forms.ModelForm):
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"placeholder": "Enter your email"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Enter your password"}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Confirm your password"}))
    secret_key = forms.CharField(label="Secret Key", widget=forms.TextInput(attrs={"placeholder": "Enter the secret key"}))

    class Meta:
        model = User
        fields = ["email"]

    def clean_email(self):
        """Ensure email is unique"""
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        """Ensure passwords match and validate secret key"""
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        secret_key = cleaned_data.get("secret_key")

        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")

        # Validate the secret key
        if secret_key != SIGNUP_SECRET_KEY:
            self.add_error("secret_key", "Invalid secret key. Please contact the administrator.")

        return cleaned_data
    

class EditOrCompleteWorkOrderForm(forms.ModelForm):
    submitted_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True
    )

    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'toggle-switch'}),
        required=True
    )

    class Meta:
        model = WorkOrder
        fields = ['submitted_date', 'status', 'remarks']  # Worker field removed

        widgets = {
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_submitted_date(self):
        submitted_date = self.cleaned_data.get('submitted_date')

        # Ensure submitted date is not before requested date
        if self.instance and self.instance.requested_date:
            if submitted_date < self.instance.requested_date:
                raise forms.ValidationError("Submitted date cannot be before the requested date.")
        
        return submitted_date
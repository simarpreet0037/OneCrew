# forms from bul upload

from django import forms
from .models import Employee

class BulkUploadEmployeeForm(forms.Form):
    excel_file = forms.FileField(label='Select a Valid Excel File To Upload')
    upload_option = forms.ChoiceField(choices=[('New', 'New Employee'), ('Update', 'Update Employee')], label='Upload Option')

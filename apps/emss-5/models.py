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
    profile_photo = models.ImageField(upload_to='employee_profiles/')

    def __str__(self):
        return self.name

class NewHire(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    work_company = models.CharField(max_length=100)
    arrived_salary = models.DecimalField(max_digits=10, decimal_places=2)
    native_language = models.CharField(max_length=100)
    education = models.CharField(max_length=100)
    marital_status = models.CharField(max_length=50, choices=[('Single', 'Single'), ('Married', 'Married'), ('Divorced', 'Divorced')])
    religion = models.CharField(max_length=50, choices=[('Buddhist', 'Buddhist'), ('Christian', 'Christian'), ('Hindu', 'Hindu'), ('Muslim', 'Muslim'), ('Sikh', 'Sikh')])
    food_type = models.CharField(max_length=50, choices=[('Veg', 'Veg'), ('Non Veg', 'Non Veg')])
    home_address = models.TextField()
    nok_name = models.CharField(max_length=100)
    nok_phone = models.CharField(max_length=20)
    nok_relation = models.CharField(max_length=100)
    email = models.EmailField()
    city_of_birth = models.CharField(max_length=100)
    work_status = models.CharField(max_length=50, choices=[('Assigned', 'Assigned'), ('Not Assigned', 'Not Assigned'), ('Inactive', 'Inactive')])
    remarks = models.TextField()
    camp = models.CharField(max_length=100)

    def __str__(self):
        return self.employee.name
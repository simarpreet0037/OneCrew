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
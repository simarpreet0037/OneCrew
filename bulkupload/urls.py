from django.urls import path
from . import views

urlpatterns = [
    path('bulk-upload/', views.bulk_upload_employee, name='bulk_upload_employee'),
    path('uploaded-data-list/', views.uploaded_data_list, name='uploaded_data_list'),
]

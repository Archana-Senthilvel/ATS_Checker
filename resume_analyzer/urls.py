from django.urls import path
from . import views

app_name = 'resume_analyzer'

urlpatterns = [
    path('', views.upload_resume, name='upload'),
    path('report/<int:analysis_id>/', views.download_report, name='download_report'),
]
from django.contrib import admin
from .models import ResumeAnalysis

@admin.register(ResumeAnalysis)
class ResumeAnalysisAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'overall_score')
    list_filter = ('created_at',)
    search_fields = ('job_description', 'analysis_result')
    readonly_fields = ('created_at',)
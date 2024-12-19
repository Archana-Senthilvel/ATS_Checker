from django.db import models
from django.core.validators import FileExtensionValidator

class ResumeAnalysis(models.Model):
    resume_file = models.FileField(
        upload_to='resumes/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    job_description = models.TextField()
    analysis_result = models.TextField(null=True, blank=True)
    overall_score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis {self.id} - {self.created_at}"
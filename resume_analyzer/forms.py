from django import forms
from .models import ResumeAnalysis

class ResumeAnalysisForm(forms.ModelForm):
    class Meta:
        model = ResumeAnalysis
        fields = ['resume_file', 'job_description']
        widgets = {
            'job_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Paste the job description here...'
            }),
            'resume_file': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }
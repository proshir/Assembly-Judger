from django import forms
from .models import Problem, Submission

class ProblemForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ['name', 'description', 'test_file', 'timeout']

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['problem', 'code_file']
from django import forms
from .models import Problem, Submission

class ProblemForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ['name', 'description', 'test_file', 'timeout']

    def clean_test_file(self):
        uploaded_file = self.cleaned_data['test_file']

        if uploaded_file and not uploaded_file.name.endswith('.zip'):
            raise forms.ValidationError("Only zip files are allowed.")
                
        return uploaded_file

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['problem', 'code_file']

class EditProblemForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ['description', 'test_file', 'timeout']

    def clean_test_file(self):
        uploaded_file = self.cleaned_data['test_file']
        self.instance.new_test_file_uploaded = False
        if uploaded_file:
            if not uploaded_file.name.endswith('.zip'):
                raise forms.ValidationError("Only zip files are allowed.")
            if self.instance.test_file != uploaded_file:
                self.instance.new_test_file_uploaded = True

        return uploaded_file
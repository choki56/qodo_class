from django import forms
from django.contrib.auth.models import User
from .models import Employee, LeaveRequest, Department

class EmployeeForm(forms.ModelForm):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = Employee
        fields = ['department', 'title', 'phone', 'start_date']

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class DirectorySearchForm(forms.Form):
    q = forms.CharField(required=False, label='Search')
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False)

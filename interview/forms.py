from django import forms
from .models import ActionInterview


class ActionInterviewForm(forms.ModelForm):
    class Meta:
        model = ActionInterview
        exclude = ('action', )
        # fields = '__all__'

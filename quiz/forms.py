from django import forms

from quiz.models import Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['company', 'title']

    def __init__(self, *args, **kwargs):
        member = kwargs.pop('member')
        super().__init__(*args, **kwargs)
        self.fields['company'].queryset = member.companies

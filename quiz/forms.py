from django import forms

from quiz.models import Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['title', 'parent_category']

    def __init__(self, *args, **kwargs):
        employer = kwargs.pop('employer')
        super().__init__(*args, **kwargs)
        self.fields['parent_category'].queryset = Category.objects.filter(employer=employer)

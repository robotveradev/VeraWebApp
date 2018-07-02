from django import forms

from pipeline.models import Action


class ActionChangeForm(forms.ModelForm):
    fee = forms.IntegerField(required=False)
    approvable = forms.BooleanField(required=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        instance = getattr(self, 'instance', None)
        if instance.action_type.must_approvable:
            self.fields['approvable'].widget.attrs['disabled'] = True

    class Meta:
        model = Action
        fields = ('action_type', )

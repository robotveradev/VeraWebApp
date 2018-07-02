from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import ugettext_lazy as _

from country_codes import codes
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields


class CustomSignupForm(SignupForm):
    phone_number = forms.IntegerField(required=True)
    email = forms.EmailField(widget=forms.TextInput(
        attrs={'type': 'email',
               'placeholder': _('E-mail address')}))
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())
    country_code = forms.ChoiceField(
        choices=[[i['dialling_code'], '{} ({})'.format(i['country_name'], i['dialling_code'])] for i in
                 codes])

    MIN_LENGTH = 4

    class Meta:
        model = CustomUser
        fields = ['username', 'country_code', 'phone_number', 'password1', 'password2', ]

    def clean_username(self):
        username = self.data.get('username')
        return username

    def clean_password1(self):
        password = self.data.get('password1')
        validate_password(password)
        if password != self.data.get('password2'):
            raise forms.ValidationError(_("Passwords do not match"))
        return password

    def clean_phone_number(self):
        phone_number = self.data.get('phone_number')
        if CustomUser.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError(
                _("Another user with this phone number already exists"))
        return phone_number

    def save(self, *args, **kwargs):
        user = super().save(*args, **kwargs)
        user.set_password(self.cleaned_data['password1'])
        print('Saving user with country_code', user.country_code)
        user.save()
        return user


class SendPhoneVerificationForm(forms.Form):
    phone_number = forms.IntegerField(required=True)

    country_code = forms.ChoiceField(
        choices=[[i['dialling_code'], '{} ({})'.format(i['country_name'], i['dialling_code'])] for i in
                 codes])
    via = forms.ChoiceField(choices=[['sms', 'sms'], ['call', 'call']])

    def clean_phone_number(self):
        phone_number = self.data.get('phone_number')
        initial_phone = self.initial.get('phone_number')
        if int(initial_phone) != int(phone_number):
            if CustomUser.objects.filter(phone_number=phone_number).exists():
                raise forms.ValidationError(
                    _("Another user with this phone number already exists"))
        return phone_number

    class Meta:
        fields = ['phone_number', 'country_code', 'via', ]


class PhoneVerificationForm(forms.Form):
    one_time_password = forms.CharField()

    class Meta:
        fields = ['one_time_password']


class CustomSocialSignupForm(SocialSignupForm):
    phone_number = forms.IntegerField(required=True)
    country_code = forms.ChoiceField(
        choices=[[i['dialling_code'], '{} ({})'.format(i['country_name'], i['dialling_code'])] for i in
                 codes])

    MIN_LENGTH = 4

    def clean_phone_number(self):
        phone_number = self.data.get('phone_number')
        if CustomUser.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError(
                _("Another user with this phone number already exists"))
        return phone_number

    def save(self, *args, **kwargs):
        user = super().save(*args, **kwargs)
        print('Saving user with country_code', user.country_code)
        user.save()
        return user

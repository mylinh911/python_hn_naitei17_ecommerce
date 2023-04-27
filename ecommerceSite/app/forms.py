from django import forms
from django.core.exceptions import ValidationError
from .models import Customer

class CustomerForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirm password')

    def clean_user_name(self):
        user_name = self.cleaned_data.get('user_name')

        if Customer.objects.filter(user_name=user_name).exists():
            raise ValidationError('Username already exists')

        return user_name

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')

        if password and password2 and password != password2:
            raise forms.ValidationError('Passwords do not match')

    class Meta:
        model = Customer
        fields = ['user_name', 'password', 'password2', 'email', 'full_name', 'address', 'phone']


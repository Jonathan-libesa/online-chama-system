from django import forms
from django.contrib.auth.hashers import make_password
from .models import *

class FormSettings(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormSettings, self).__init__(*args, **kwargs)
        # Here make some changes such as:
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'

                # Check if the 'is_email_verified' field is in the form
        if 'is_email_verified' in self.fields:
            self.fields['is_email_verified'].widget.attrs['class'] = 'form-check-input'


class UserForm(FormSettings):
    username=forms.CharField(required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)

    widget = {
        'password': forms.PasswordInput(),
    }

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        if kwargs.get('instance'):
            instance = kwargs.get('instance').__dict__
            self.fields['password'].required = False
            for field in UserForm.Meta.fields:
                self.fields[field].initial = instance.get(field)
            if self.instance.pk is not None:
                self.fields['password'].widget.attrs['placeholder'] = "Fill this only if you wish to update password"
        else:
            self.fields['first_name'].required = True
            self.fields['last_name'].required = True

    def clean_email(self, *args, **kwargs):
        formEmail = self.cleaned_data['email'].lower()
        if self.instance.pk is None:  # Insert
            if User.objects.filter(email=formEmail).exists():
                raise forms.ValidationError(
                    "The given email is already registered")
        else:  # Update
            dbEmail = self.Meta.model.objects.get(
                id=self.instance.pk).email.lower()
            if dbEmail != formEmail:  # There has been changes
                if User.objects.filter(email=formEmail).exists():
                    raise forms.ValidationError(
                        "The given email is already registered")
        return formEmail

    def clean_password(self):
        password = self.cleaned_data.get("password", None)
        if self.instance.pk is not None:
            if not password:
                # return None
                return self.instance.password

        return make_password(password)

    class Meta:
        model = User
        fields = ['username','email', 'first_name', 'last_name', 'password', ]
        

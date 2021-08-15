from django import forms
from django.contrib.auth.models import User
from .models import Trader


class LoginForm(forms.ModelForm):
    username = forms.CharField(label='')
    password = forms.CharField(widget=forms.PasswordInput, label='')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs = {'class': 'form-control', 'style': 'background: #f7f7ff;',
                                                'placeholder': 'Username'}
        self.fields['password'].widget.attrs = {'class': 'form-control', 'style': 'background: #f7f7ff;',
                                                'placeholder': 'Password'}

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']

        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError('Incorrect username or password.')
        user = User.objects.filter(username=username).first()
        if user:
            if not user.check_password(password):
                raise forms.ValidationError('The password you entered is incorrect.')
            elif user.is_active is False:
                raise forms.ValidationError('This account has been blocked.')
        return self.cleaned_data

    class Meta:
        model = User
        fields = ['username', 'password']


class RegisterForm(forms.ModelForm):
    first_name = forms.CharField(required=True, label='')
    last_name = forms.CharField(required=True, label='')
    email = forms.EmailField(required=True, label='')
    username = forms.CharField(required=True, label='')
    password = forms.CharField(required=True, widget=forms.PasswordInput, label='')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs = {'class': 'form-control', 'style': 'background: #f7f7ff;',
                                                  'placeholder': 'First Name'}
        self.fields['last_name'].widget.attrs = {'class': 'form-control', 'style': 'background: #f7f7ff;',
                                                 'placeholder': 'Last Name'}
        self.fields['email'].widget.attrs = {'class': 'form-control', 'style': 'background: #f7f7ff;',
                                             'placeholder': 'Email'}
        self.fields['username'].widget.attrs = {'class': 'form-control', 'style': 'background: #f7f7ff;',
                                                'placeholder': 'Username'}
        self.fields['password'].widget.attrs = {'class': 'form-control', 'style': 'background: #f7f7ff;',
                                                'placeholder': 'Password'}

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This Email cannot be used.')
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This Username cannot be used.')
        return username

    def clean(self):
        return self.cleaned_data

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'email']


class ChangePasswordForm(forms.ModelForm):
    old_password = forms.CharField(required=True, widget=forms.PasswordInput, label='')
    password = forms.CharField(required=True, widget=forms.PasswordInput, label='')
    repeat_password = forms.CharField(required=True, widget=forms.PasswordInput, label='')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs = {'class': 'form-control', 'style': 'height: 30px;',
                                                    'placeholder': 'Enter Old Password'}
        self.fields['password'].widget.attrs = {'class': 'form-control', 'style': 'height: 30px;',
                                                'placeholder': 'Enter New Password'}
        self.fields['repeat_password'].widget.attrs = {'class': 'form-control', 'style': 'height: 30px;',
                                                       'placeholder': 'Confirm Password'}

    def clean(self):
        password = self.cleaned_data['password']
        repeat_password = self.cleaned_data['repeat_password']
        if password != repeat_password:
            raise forms.ValidationError("Password change error. Passwords don't match.")
        return self.cleaned_data

    class Meta:
        model = User
        fields = ['old_password', 'password', 'repeat_password']


class VerificationForm(forms.ModelForm):
    front_file = forms.FileField(required=True, label='', )
    back_file = forms.FileField(required=True, label='')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['front_file'].widget.attrs = {'class': 'custom-file-input', 'style': 'background:#f7f7ff;',
                                                  'name': 'id_front_file', 'id': 'id_front_file', 'accept': '.jpg,.png'}
        self.fields['back_file'].widget.attrs = {'class': 'custom-file-input', 'style': 'background:#f7f7ff;',
                                                 'name': 'id_front_file', 'id': 'id_front_file', 'accept': '.jpg,.png'}

    def clean(self):
        return self.cleaned_data

    class Meta:
        model = User
        fields = ['front_file', 'back_file']

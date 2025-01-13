from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(max_length=63, label='user')
    password = forms.CharField(max_length=63, widget=forms.PasswordInput, label='Password')
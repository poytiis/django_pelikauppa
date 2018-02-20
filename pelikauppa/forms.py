from django import forms
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from pelikauppa.models import Profile, Game

class UserForm(forms.ModelForm):
    username = forms.CharField(label='Käyttäjätunnus')
    password = forms.CharField(widget=forms.PasswordInput, label='Salasana')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Vahvista salasana')
    email = forms.EmailField(required=True, label='Sähköposti')

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class UserProfileForm(forms.ModelForm):
    is_developer = forms.BooleanField(label='Rekisteröidy kehittäjänä:', required=False)

    class Meta:
        model = Profile
        exclude = ['user']

class GameForm(forms.ModelForm):
    name = forms.CharField(label='Pelin nimi', required=True)
    url = forms.URLField(label='Pelin URL', required=True)
    price = forms.DecimalField(label='Pelin hinta', max_digits=5, decimal_places=2, min_value=0)

    class Meta:
        model = Game
        exclude = ['developer']

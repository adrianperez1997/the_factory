from django import forms
from myApp.models import Group, Key

class MachineForm(forms.Form):
    name=forms.CharField(label='Machine name:')
    ip =forms.CharField(label='Hostname:', help_text='You can specify a different port example.com:22')
    user =forms.CharField(label='Username:')
    #port =forms.IntegerField()

    choices = []
    key = Key.objects.all()

    for k in key:
        choices.append((k.name, k.name))

    keys = forms.ChoiceField(choices=choices)
    choices = []
    groups = Group.objects.all()

    for g in groups:
        choices.append((g.name, g.name))

    group=forms.ChoiceField(choices=choices)
    #key =forms.CharField()

class KeyForm(forms.Form):
    name=forms.CharField(label='Key name:')

class ViewKeyForm(forms.Form):
    key=forms.FilePathField(path='keys/public')


class GroupForm(forms.Form):
    name=forms.CharField(label='Group name:')


class PrepareForm(forms.Form):
    option = forms.ChoiceField(label="Prepare with: ",choices=[('docker','Docker Server')])
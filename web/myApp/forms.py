from django import forms
from myApp.models import Group

class MachineForm(forms.Form):
    name=forms.CharField(label='Machine name:')
    ip =forms.CharField(label='Hostname:', help_text='You can specify a different port example.com:22')
    user =forms.CharField(label='Username:')
    #port =forms.IntegerField()
    keys=forms.FilePathField(path='keys/public/')
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


class PrepareForm(forms.Form):
    option = forms.ChoiceField(label="Prepare with: ",choices=[('docker','Docker Server')])
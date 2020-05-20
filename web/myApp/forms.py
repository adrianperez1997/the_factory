from django import forms

class MachineForm(forms.Form):
    name=forms.CharField(label='Machine name:')
    ip =forms.CharField(label='Hostname:', help_text='You can specify a different port example.com:22')
    user =forms.CharField(label='Username:')
    #port =forms.IntegerField()
    keys=forms.FilePathField(path='keys/public/')
    group=forms.ChoiceField(choices=[('default', 'default2'),('mygroup','mygroup')])
    #key =forms.CharField()

class KeyForm(forms.Form):
    name=forms.CharField(label='Key name:')

class ViewKeyForm(forms.Form):
    key=forms.FilePathField(path='keys/public')
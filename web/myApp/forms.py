from django import forms

class MachineForm(forms.Form):
    name=forms.CharField()
    ip =forms.CharField()
    port =forms.IntegerField()
    user =forms.CharField()
    key =forms.CharField()
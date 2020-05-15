from django.shortcuts import render
from myApp.models import Machines
from myApp.forms import MachineForm

# Create your views here.
def saludo2(request):

    return render(request, 'miplantilla.html',{"lista": ['hola','saludo2']})

def new_machine(request, name, ip, key, user, port=22):

    m1 = Machines(name=name, ip=ip, key=key, user=user, port=port)
    m1.save()
    return render(request, 'miplantilla.html',{"lista": [name,ip]})

def machines(request):

    if request.GET["Nombre"]:
        machines = Machines.objects.filter(name__icontains=request.GET["Nombre"])
    else:
        machines = Machines.objects.all( )

    return render(request, 'miplantilla.html',{"lista": machines})

def form(request):
    if request.method=="POST":
        miform = MachineForm(request.POST)

        if miform.is_valid():
            data = miform.cleaned_data
            return render(request, 'miplantilla.html',{"lista": [data]})

    else:
        miform=MachineForm()

    return render(request, 'form.html', {'form':miform})

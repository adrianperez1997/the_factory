from django.shortcuts import render
from myApp.models import Machines
from myApp.forms import MachineForm, KeyForm, ViewKeyForm
from myApp.controller import add_machine, add_to_inventory, run_playbook, new_key

import ansible_runner
import yaml
# Create your views here.

def home(request):
    machines = Machines.objects.all( )

    dict = []
    for m in machines:
        dict.append({'name': m.name, 'ip':m.ip, 'port':m.port})

    return render(request, 'home.html',{"machines":machines, "aux":"algo"})
def machines(request):


    machines = Machines.objects.all( )

    dict=[]
    for m in machines:

        dict.append({'name': m.name, 'ip':m.ip, 'port':m.port, 'status':m.status, 'cores':m.cores,
                              'distribution':m.distribution, 'ram':m.ram, 'version':m.version, 'group':m.group})

    return render(request, 'miplantilla.html',{"machines":machines})

def form(request):
    msg = ''
    keyfile = 'keys/miclave'
    if request.method=="POST":
        k = KeyForm(request.POST)
        vk = ViewKeyForm(request.POST)

        try:
            miform = MachineForm(request.POST)

            # Si no pongo esto no funciona, informagia...
            print(miform)

            data = miform.cleaned_data
            ip = data['ip']
            port = 22
            if ':' in data['ip']:
                a = str(data['ip']).split(':')
                ip = a[0]
                port = a[1]

            # keyfile = data['keys']
            msg = add_machine(name=data['name'], ip=ip, key=data['keys'], port=port, user=data['user'],
                              group=data['group'])

        except:
            miform = MachineForm()

        if k.is_valid():
            datak = k.cleaned_data

            new_key(datak['name'])
        if vk.is_valid():
            datavk = vk.cleaned_data

            keyfile= datavk['key']

        #keyfile = '/keys/miclave'
    else:
        k = KeyForm()
        vk = ViewKeyForm(request.GET)
        miform=MachineForm()


    f =open(keyfile,'r')
    key = f.read()
    f.close()
    machines = Machines.objects.all()
    dict = []
    for m in machines:
        dict.append({'name': m.name, 'ip':m.ip, 'port':m.port, 'status':m.status, 'cores':m.cores, 'distribution':m.distribution,
                     'ram':m.ram, 'version':m.version, 'group':m.group})
    return render(request, 'form.html',{"machines": machines,'msg':msg, 'form':miform,'key_form':k, 'view_key_form': vk,
                                        'key':key})


def test(request):
    miform = MachineForm(request.POST)

    # Si no pongo esto no funciona, informagia...
    print(miform)

    data = miform.cleaned_data
    machines = Machines.objects.all()

    #add_to_inventory(data['name'], data['ip'], data['port'], data['key'], data['user'])
    msg = ''
    #run_playbook(data['name'], 'data/info2.yaml', event_handler=test_event_handler)

    return render(request, 'form.html',{'form':miform, 'msg': msg, 'lista': machines})

def setup(request):
    miform = MachineForm(request.POST)

    # Si no pongo esto no funciona, informagia...
    print(miform)

    data = miform.cleaned_data
    machines = Machines.objects.all()

    #add_to_inventory(data['name'], data['ip'], data['port'], data['key'], data['user'])
    msg = '' #run_playbook(data['name'], 'data/docker.yaml')

    return render(request, 'form.html',{'form':miform, 'msg': msg, 'lista': machines})


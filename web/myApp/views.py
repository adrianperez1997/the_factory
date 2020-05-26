from django.shortcuts import render
from myApp.models import Machines, Group, Key
from myApp.forms import MachineForm, KeyForm, ViewKeyForm, PrepareForm, GroupForm, EditMachineForm
from myApp.controller import add_machine, add_to_inventory, run_playbook, new_key, edit_machine, debug, delete_machine, test_machine

import ansible_runner
import yaml
# Create your views here.

def home(request):
    k = Key(name='name')
    k.save()
    groups = Group.objects.all()
    main = []
    for g in groups:
        machines = Machines.objects.filter(group_id=g.name)
        main.append({'name': g.name, 'machines': machines})

    return render(request, 'home.html',{"groups":main})


def machine_new(request):
    msg = ''
    if request.method == "POST":
        try:
            miform = MachineForm(request.POST)

            # Si no pongo esto no funciona, informagia...
            print(miform)
            if miform.is_valid():
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

    else:
        vk = ViewKeyForm()
        miform=MachineForm()

    return new_machine(request, new_form=miform, msg=msg)

def machine_new_key(request):
    if request.method=="POST":
        try:
            k = KeyForm(request.POST)
            if k.is_valid():
                datak = k.cleaned_data
                new_key(datak['name'])
        except:
            k = KeyForm()
    else:
        k = KeyForm()

    return new_machine(request, key_form=k)

def machine_view_key(request):
    if request.method == "POST":
        try:
            vk = ViewKeyForm(request.POST)
            if vk.is_valid():
                datavk = vk.cleaned_data
                keyfile = datavk['key']

        except:
            vk = ViewKeyForm()

    else:
        vk = ViewKeyForm()
    return new_machine(request, view_key_form=vk, keyfile=keyfile)

def new_machine(request, msg='', key_form= KeyForm(), new_form=MachineForm(), view_key_form=ViewKeyForm(), keyfile='keys/public/default.pub'):

    f =open(keyfile,'r')
    key = f.read()
    f.close()

    groups = Group.objects.all()
    main = []
    for g in groups:
        machines = Machines.objects.filter(group_id=g.name)
        main.append({'name': g.name, 'machines': machines})

    return render(request, 'new_machine.html',{"groups": main,'msg':msg, 'form':new_form,'key_form':key_form,
                                        'view_key_form': view_key_form, 'key':key})

def new_group(request):
    msg = ''
    if request.method=="GET":
        form = GroupForm()
    elif request.method=="POST":

        try:
            form = GroupForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                name = data['name']

                if not Group.objects.filter(name=name):
                    g = Group(name=name)
                    g.save()
                else:
                    msg='Invalid name'

        except:
            form = GroupForm(request.POST)
            msg='Error'



    groups = Group.objects.all()
    main = []
    for g in groups:
        machines = Machines.objects.filter(group_id=g.name)
        main.append({'name': g.name, 'machines': machines})

    return render(request, 'new_group.html',{'groups':main,'form':form, 'msg':msg})














def machine_delete(request):
    if request.method=="GET":
        delete_machine(request.GET["name"])

    return machine(request)


def machine_test(request):
    if request.method=="GET":
        test_machine(request.GET["name"])

    return machine(request)




def machine_edit(request):
    msg = ''
    if request.method == "GET":
        try:
            miform = EditMachineForm(request.GET)
            if miform.is_valid():
                data = miform.cleaned_data

                ip = data['ip']
                port = 22
                if ':' in data['ip']:
                    a = str(data['ip']).split(':')
                    ip = a[0]
                    port = a[1]
                edit_machine(name=request.GET['name'], ip=ip, key=data['keys'], port=port, user=data['user'])
                debug('fuera\n')
            else:
                debug('not valid')
                # keyfile = data['keys']


        except:
            miform = EditMachineForm()

    else:
        miform=EditMachineForm()

    return machine(request, edit_form=miform, msg=msg)



def test(request):
    main=[]

    machines = Machines.objects.filter(group_id=request.GET['name'])
    main.append({'name': request.GET['name'], 'machines': machines})

    if request.method=="GET":
        p = PrepareForm()
    elif request.method=="POST":
        p = PrepareForm(request.POST)


    return render(request, 'group.html',{"p_form":p,"groups":main})


def machine(request, msg='', edit_form=EditMachineForm()):
    if request.method=="GET":
        main=[]
        machines = Machines.objects.filter(name=request.GET['name'])
        n = 'default'
        for m in machines:
            n = m.group_id
        main.append({'name': n, 'machines': machines})


        return render(request, 'machine.html',{"edit_form":edit_form,"groups":main})

def setup(request):
    miform = MachineForm(request.POST)

    # Si no pongo esto no funciona, informagia...
    print(miform)

    data = miform.cleaned_data
    machines = Machines.objects.all()

    #add_to_inventory(data['name'], data['ip'], data['port'], data['key'], data['user'])
    msg = '' #run_playbook(data['name'], 'data/docker.yaml')

    return render(request, 'new_machine.html',{'form':miform, 'msg': msg, 'lista': machines})


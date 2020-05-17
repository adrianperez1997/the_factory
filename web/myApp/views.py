from django.shortcuts import render
from myApp.models import Machines
from myApp.forms import MachineForm
import ansible_runner
import yaml

# Create your views here.

def machines(request):


    machines = Machines.objects.all( )

    dict = []
    for m in machines:
        dict.append({'name': m.name, 'ip':m.ip, 'port':m.port})

    return render(request, 'miplantilla.html',{"machines":machines})

def form(request):
    if request.method=="POST":
        miform = MachineForm(request.POST)

        #Si no pongo esto no funciona, informagia...
        print(miform)

        data = miform.cleaned_data
        if not Machines.objects.filter(name=data['name']):
            m1 = Machines(name=data['name'], ip=data['ip'], key=data['key'], user=data['user'], port=data['port'])
            m1.save()

        machines = Machines.objects.all()
        return render(request, 'form.html',{"lista": machines, 'form':miform})

    else:
        miform=MachineForm()

    machines = Machines.objects.all()
    return render(request, 'form.html', {'form':miform, 'lista': machines})

def test(request):
    miform = MachineForm(request.POST)

    # Si no pongo esto no funciona, informagia...
    print(miform)

    data = miform.cleaned_data
    machines = Machines.objects.all()

    add_virtual(data['name'], data['ip'], data['port'], data['key'], data['user'])
    msg = ''
    try:
        with open('data/info.yaml') as f:
            o = yaml.load(f, Loader=yaml.FullLoader)
            o[-1]['hosts'] = data['name']
            s = open('data/info.yaml', 'w')
            yaml.dump(o, s)
            s.close()
            f.close()
    except:
        msg = 'error opening info.yaml\n'

    r = ansible_runner.run(private_data_dir='.', inventory='data/inventory.yaml', playbook='data/info.yaml')


    if r.stats['failures'] != {}:
        msg = msg + 'FAILED' + str(r.stats['failures']) + '\n'

    if r.stats['dark'] != {}:
        msg = msg + 'DARK' + str(r.stats['dark']) + '\n'

    if r.stats['skipped'] != {}:
        msg = msg + 'FAILED' + str(r.stats['skipped']) + '\n'

    if r.stats['ok'] != {}:
        msg = msg + 'OK' + str(r.stats['ok']) + '\n'

    if r.stats['processed'] != {}:
        msg = msg + 'PROCESSED' + str(r.stats['processed']) + '\n'


    return render(request, 'form.html',{'form':miform, 'msg': msg, 'lista': machines})


def add_virtual(name, ip, port, key, user):
    try:
        with open('data/inventory.yaml') as f:
            o = yaml.load(f, Loader=yaml.FullLoader)
            if name in o['all']['hosts']:
                print('Escoje otro nombre')
    except FileNotFoundError:
        o = {'all': {'hosts': {}, 'children': {'info': {'hosts': {}}}}}
    finally:
        o['all']['hosts'].update({name:{'ansible_host': ip,
                                   'ansible_port': port,
                                   'ansible_user': user,
                                   'ansible_ssh_private_key_file': key,
                                   'ansible_ssh_extra_args': '-o StrictHostKeyChecking=no'}})

        try:
            o['all']['children']['info']['hosts'].update({name:None})
        except KeyError:
            print('keyerror')
            o['all']['children'].update({'info':{'hosts':{name:None}}})
        s = open('data/inventory.yaml', 'w')
        yaml.dump(o, s)
        s.close()

    return 0
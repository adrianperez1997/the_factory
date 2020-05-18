from django.shortcuts import render
from myApp.models import Machines
from myApp.forms import MachineForm
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
            m1 = Machines(name=data['name'], ip=data['ip'], key=data['key'], user=data['user'], port=data['port'], setup=False)
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
    msg = run_playbook(data['name'], 'data/info2.yaml', event_handler=test_event_handler)

    return render(request, 'form.html',{'form':miform, 'msg': msg, 'lista': machines})

def setup(request):
    miform = MachineForm(request.POST)

    # Si no pongo esto no funciona, informagia...
    print(miform)

    data = miform.cleaned_data
    machines = Machines.objects.all()

    add_virtual(data['name'], data['ip'], data['port'], data['key'], data['user'])
    msg = run_playbook(data['name'], 'data/docker.yaml')

    return render(request, 'form.html',{'form':miform, 'msg': msg, 'lista': machines})

def add_virtual(name, ip, port, key, user):
    try:
        with open('data/inventory.yaml') as f:
            o = yaml.load(f, Loader=yaml.FullLoader)
            if name in o['all']['hosts']:
                print('Escoje otro nombre')
    except FileNotFoundError:
        o = {'all': {'hosts': {}, 'children': {'virtual': {'hosts': {}}}}}
    finally:
        o['all']['hosts'].update({name:{'ansible_host': ip,
                                   'ansible_port': port,
                                   'ansible_user': user,
                                   'ansible_ssh_private_key_file': key,
                                   'ansible_ssh_extra_args': '-o StrictHostKeyChecking=no'}})

        try:
            o['all']['children']['virtual']['hosts'].update({name:None})
        except KeyError:
            print('keyerror')
            o['all']['children'].update({'virtual':{'hosts':{name:None}}})
        s = open('data/inventory.yaml', 'w')
        yaml.dump(o, s)
        s.close()

    return 0

def general_status_handler(status, runner_config=None):
    f = open('data/debug.txt','a')
    f.write('status: '+str(status)+ '\n')
    f.close()
    print('status: '+str(status))
    return status

def general_event_handler(event):
    f = open('data/debug.txt','a')
    f.write('event: '+str(event)+ '\n')
    print('event: '+str(event))
    try:
        f.write('DISTRIBUCION: ' + str(event['event_data']['res']['ansible_facts']['ansible_distribution']) + '\n')
    except:
        f.write('Algo fallo \n')
    finally:
        f.close()

    return event

def test_event_handler(event):
    f = open('data/debug.txt','a')
    f.write('event: '+str(event)+ '\n')
    print('event: '+str(event))
    try:
        f.write('DISTRIBUCION: ' + str(event['event_data']['res']['ansible_facts']['ansible_distribution']) + '\n')
        f.write('Version: ' + str(event['event_data']['res']['ansible_facts']['ansible_distribution_release']) + '\n')
        f.write('Cpu cores: ' + str(event['event_data']['res']['ansible_facts']['ansible_processor_cores']) + '\n')
        f.write('RAM: ' + str(event['event_data']['res']['ansible_facts']['ansible_memtotal_mb']) + '\n')
        f.write('Swap: ' + str(event['event_data']['res']['ansible_facts']['ansible_memory_mb.swap.total']) + '\n')
    except:
        pass
    finally:
        f.close()

    return event

def run_playbook(machine_name, playbook, private_data_dir='.', inventory='data/inventory.yaml', ident='00001',event_handler=general_event_handler, status_handler=general_status_handler, json_mode=True):
    msg = ''
    try:
        with open(playbook) as f:
            o = yaml.load(f, Loader=yaml.FullLoader)
            o[-1]['hosts'] = machine_name
            s = open(playbook, 'w')
            yaml.dump(o, s)
            s.close()
            f.close()
    except:
        msg = 'error opening ' + playbook +'\n'

    r = ansible_runner.run(private_data_dir=private_data_dir, inventory=inventory, ident=ident,event_handler=event_handler, status_handler=status_handler,playbook=playbook, json_mode=json_mode)

    if r.stats['failures'] != {}:
        msg = msg + 'FAILED' + str(r.stats['failures']) + '\n'

    if r.stats['dark'] != {}:
        msg = msg + 'DARK' + str(r.stats['dark']) + '\n'

    if r.stats['skipped'] != {}:
        msg = msg + 'SKIPPED' + str(r.stats['skipped']) + '\n'

    if r.stats['ok'] != {}:
        msg = msg + 'OK' + str(r.stats['ok']) + '\n'

    if r.stats['processed'] != {}:
        msg = msg + 'PROCESSED' + str(r.stats['processed']) + '\n'

    return msg


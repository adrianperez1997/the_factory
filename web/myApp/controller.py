import ansible_runner
import yaml
from myApp.models import Machines, Group
import subprocess

def add_machine(name, ip, key, user, group,port=22):
    """
    comprueba name valid
    add inventory
    add ddbb

    :return:
    """
    if not Machines.objects.filter(name=name):
        add_to_inventory(name, ip, port, key, user, 'data/inventory.yaml', group)
        g = Group(name=group)
        g.save()
        m1 = Machines(name=name,ip=ip,port=port, key=key,user=user, group=g, status='gathering info')
        m1.save()
        msg = run_playbook(name, 'data/info2.yaml', event_handler=gather_facts_event_handler)
        return 'running'
    else:
        return 'Invalid name'


def new_key(name):
    keyname = 'keys/'+name
    passphrase= ""
    subprocess.run([ "ssh-keygen", "-b", "2048", "-t", "rsa", "-f",keyname, "-q","-N",passphrase])
    pub_key=keyname + '.pub'
    subprocess.run([ "cp", pub_key,"keys/public/"])


def add_to_inventory(name, ip, port, key, user, inventory, group):
    try:
        with open(inventory) as f:
            o = yaml.load(f, Loader=yaml.FullLoader)
            if name in o['all']['hosts']:
                return -1
    except FileNotFoundError:
        o = {'all': {'hosts': {}, 'children': {group: {'hosts': {}}}}}
    finally:
        o['all']['hosts'].update({name:{'ansible_host': ip,
                                   'ansible_port': port,
                                   'ansible_user': user,
                                   'ansible_ssh_private_key_file': key,
                                   'ansible_ssh_extra_args': '-o StrictHostKeyChecking=no'}})

        try:
            o['all']['children'][group]['hosts'].update({name:None})
        except KeyError:
            o['all']['children'].update({group:{'hosts':{name:None}}})
        s = open(inventory, 'w')
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
    f.close()

    return event

def gather_facts_event_handler(event):
    f = open('data/debug.txt','a')
    f.write('event: '+str(event)+ '\n')
    print('event: '+str(event))
    if event['event']=='runner_on_ok':
        try:
            dist = str(event['event_data']['res']['ansible_facts']['ansible_distribution'])
            version = str(event['event_data']['res']['ansible_facts']['ansible_distribution_release'])
            cores = int(event['event_data']['res']['ansible_facts']['ansible_processor_cores'])
            ram = int(event['event_data']['res']['ansible_facts']['ansible_memtotal_mb'])
            Machines.objects.filter(name=event['event_data']['host']).update(cores=cores,version=version,
                                                                             distribution=dist, ram=ram, status='ready')
            #m1 = Machines(name=event['event_data']['host'],cores=cores,version=version, distribution=dist, ram=ram)
            #m1.save()
        except:
            pass

    f.close()

    return event

def run_playbook(machine_name, playbook, private_data_dir='.', inventory='data/inventory.yaml', ident='00001',event_handler=general_event_handler, status_handler=general_status_handler, json_mode=True):
    try:
        with open(playbook) as f:
            o = yaml.load(f, Loader=yaml.FullLoader)
            o[-1]['hosts'] = machine_name
            s = open(playbook, 'w')
            yaml.dump(o, s)
            s.close()
            f.close()
    except:
        pass

    return ansible_runner.run_async(private_data_dir=private_data_dir, inventory=inventory, ident=ident,event_handler=event_handler, status_handler=status_handler,playbook=playbook, json_mode=json_mode)


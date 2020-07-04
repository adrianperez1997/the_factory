import ansible_runner
import yaml
from myApp.models import Machines, Group, Key, Run
import subprocess
import logging

logging.basicConfig(filename='data/debug.log', format='%(asctime)s - %(levelname)s: %(funcName)s - %(message)s', datefmt='[%d/%b/%y %H:%M:%S]')



def run_group(name, option, machines_names):
    machines = Machines.objects.filter(group_id=name)
    #machines.update(status='Preparing...')
    run = Run(group_id=name)
    run.save()

    inventory_filename = 'data/cache/inventory_' + str(run.ident) + '.yaml'
    for m in machines:
        if m.name in machines_names:
            m.status = 'Preparing...'
            add_to_inventory(name=m.name, port=m.port, ip=m.ip, key=m.key.private_file, group=m.group_id,
                             user=m.user, inventory=inventory_filename)
            run.machines.add(m)

    if option == 'docker':
        run.playbook='data/docker.yaml'
        run_playbook(name, 'data/docker.yaml', inventory=inventory_filename, ident=str(run.ident), event_handler=docker_event_handler2)

    elif option == 'monitor':
        run.playbook='data/monitor-server.yaml'

        run_playbook(name, 'data/monitor-server.yaml', inventory=inventory_filename, ident=str(run.ident),
                     event_handler=monitor_server_event_handler)

    elif option == 'monitor-agent':
        machines =  Machines.objects.filter(group_id=name, monitor='server')
        if machines:
            for m in machines:
                run.playbook='data/monitor-agent.yaml'
                import configparser
                config = configparser.ConfigParser()
                config.read_file(open('/data/telegraf-agent.conf'))
                config['[outputs.influxdb']['urls'] = "['http://" + m.ip + ":8086']"
                config.write(open('/data/telegraf-agent.conf', 'w'))
                run_playbook(name, 'data/monitor-agent.yaml', inventory=inventory_filename, ident=str(run.ident),
                             event_handler=docker_event_handler2)

    elif option == 'compose':
        run.playbook='data/compose.yaml'
        run_playbook(name, 'data/compose.yaml', inventory=inventory_filename, ident=str(run.ident),
                     event_handler=docker_event_handler2)


def delete_machine(name):
    machine = Machines.objects.filter(name=name)
    delete_from_inventory(name=name, inventory='data/inventory.yaml')
    machine.delete()

def test_machine(name):
    machine = Machines.objects.filter(name=name)
    machine.update(status='gathering info')
    run_playbook(name, 'data/info2.yaml', event_handler=gather_facts_event_handler)

def edit_machine(name, ip=None, key=None, user=None,port=22):
    try:
        machine = Machines.objects.filter(name=name)
        keys = Key.objects.filter(name=key)
        for k in keys:
            keyfile=k.private_file

        if ip and user:
            machine.update(ip=ip, key=key, user=user, port=port)
            r = edit_inventory(name=name, inventory='data/inventory.yaml',ip=ip, key=keyfile, port=port, user=user)
        elif ip:
            machine.update(ip=ip, key=key, port=port)
            r = edit_inventory(name=name,inventory='data/inventory.yaml', ip=ip, key=keyfile, port=port)
        elif user:
            machine.update(key=key, user=user)
            r = edit_inventory(name=name, inventory='data/inventory.yaml', key=keyfile, user=user)
        else:
            machine.update(key=key)
            r = edit_inventory(name=name, inventory='data/inventory.yaml', key=keyfile)

    except:
        return -1

    return 0

def add_machine(name, ip, key, user, group,port=22):
    """
    comprueba name valid
    add inventory
    add ddbb

    :return:
    """
    if not Machines.objects.filter(name=name):
        key_file = '/keys/private/miclave'
        try:
            k = Key.objects.filter(name=key)
            for key in k:
                key_file=key.private_file

        except:
            key_file='/keys/private/miclave'

        add_to_inventory(name, ip, port,key_file, user, 'data/inventory.yaml', group)

        m1 = Machines(name=name,ip=ip,port=port, key=key,user=user, group_id=group, status='gathering info')
        m1.save()
        run_playbook(name, 'data/info2.yaml', event_handler=gather_facts_event_handler)
        return 'running'
    else:
        return 'Invalid name'

def debug(msg):
    f = open('data/debug.txt', 'a')
    f.write(msg + '\n')
    f.close()

def generate_key(name):
    debug('Entra?')
    if not Key.objects.filter(name=name):
        debug('Entra?')
        keyname = 'keys/'+name
        passphrase= ""
        subprocess.run([ "ssh-keygen", "-b", "2048", "-t", "rsa", "-f",keyname, "-q","-N",passphrase])
        subprocess.run(["mv", keyname, "/keys/private/"])
        pub_key=keyname + '.pub'
        subprocess.run(["mv", pub_key,"/keys/public/"])

        public_file = '/keys/public/' + name + '.pub'
        private_file = '/keys/private/' + name
        public = open(public_file, 'r').read()
        private = open(private_file, 'r').read()

        k = Key(name=name, public_file=public_file, private_file=private_file,
                public=public, private=private)
        k.save()

def edit_inventory(name, inventory, ip=None, port=None, key=None, user=None):
    try:
        with open(inventory) as f:
            o = yaml.load(f, Loader=yaml.FullLoader)
            f.close()
            if name in o['all']['hosts']:
                args = {}
                if ip:
                    args.update({'ansible_host': ip})
                    args.update({'ansible_port': port})
                if key:
                    args.update({'ansible_ssh_private_key_file': key})
                if user:
                    args.update({'ansible_user': user})
                o['all']['hosts'][name].update(args)

                s = open(inventory, 'w')
                yaml.dump(o, s)
                s.close()
            else:
                return -1
    except FileNotFoundError:
        return -1
    return 0

def delete_from_inventory(name, inventory):
    try:
        with open(inventory) as f:
            o = yaml.load(f, Loader=yaml.FullLoader)
            f.close()
            if name in o['all']['hosts']:
                o['all']['hosts'].pop(name)

                s = open(inventory, 'w')
                yaml.dump(o, s)
                s.close()
            else:
                return -1
    except FileNotFoundError:
        return -1
    return 0

def add_to_inventory(name, ip, port, key, user, inventory, group):
    o={}
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

def rewrite_inventory():
    machines = Machines.objects.all()
    for m in machines:
        #k = Key.objects.filter(name=m.key)
        add_to_inventory(name=m.name, ip=m.ip, port=m.port, key=m.key.private_file, user=m.user,
                         inventory='data/inventory.yaml', group=m.group_id)

def general_status_handler(status, runner_config=None):
    logging.info(status['status'])
    try:
        Run.objects.filter(ident=int(status['runner_ident'])).update(status=status['status'])
    except:
        logging.error('Not run instance found')

    f = open('data/debug.txt','a')
    f.write('status: '+str(status['status'])+ '\n')
    f.close()
    print('status: '+str(status))
    return status

def general_event_handler(event):
    logging.info(event['stdout'])
    f = open('data/debug.txt','a')
    f.write('event: '+str(event)+ '\n')
    print('event: '+str(event))
    f.close()

    return event

def docker_event_handler2(event):
    try:
        logging.info(str(event['stdout']))
        r = Run.objects.filter(ident=int(event['runner_ident']))
        stdout = ''
        for run in r:
            stdout = run.stdout + event['stdout']
        Run.objects.filter(ident=int(event['runner_ident'])).update(stdout=stdout)

    except Exception as e:
        logging.error('Error: '+ str(e))

    try:
        Machines.objects.filter(name=event['event_data']['host']).update(event=event['event'])
    except Exception as e:
        logging.error('Error: '+str(e))

    if event['event'] == 'runner_on_ok':
        try:
            Machines.objects.filter(name=event['event_data']['host']).update(status='running')

        except Exception as e:
            logging.error('Error: '+ e)

    if event['event'] == 'runner_on_start':
        try:
            Machines.objects.filter(name=event['event_data']['host']).update(status='running')

        except Exception as e:
            logging.error('Error: '+ e)

    elif event['event'] == 'playbook_on_stats':

        if event['event_data']['ok'] != {}:
            for ok in event['event_data']['ok'].keys():
                try:
                    Machines.objects.filter(name=ok).update(status='ok')
                except Exception as e:
                    logging.error('Error: ' + e)

        if event['event_data']['dark'] != {}:
            for dark in event['event_data']['dark'].keys():
                try:
                    Machines.objects.filter(name=dark).update(status='unreachable')
                except Exception as e:
                    logging.error('Error: ' + e)

        if event['event_data']['failures'] != {}:
            for failures in event['event_data']['failures'].keys():
                try:
                    Machines.objects.filter(name=failures).update(status='fails')
                except Exception as e:
                    logging.error('Error: ' + e)



        f = open('data/debug.txt', 'a')
        f.write('FINAL: ' + str(event) + '\n')
        f.close()


def monitor_server_event_handler(event):
    try:
        logging.info(str(event['stdout']))
        r = Run.objects.filter(ident=int(event['runner_ident']))
        stdout = ''
        for run in r:
            stdout = run.stdout + event['stdout']
        Run.objects.filter(ident=int(event['runner_ident'])).update(stdout=stdout)

    except Exception as e:
        logging.error('Error: '+ str(e))

    try:
        Machines.objects.filter(name=event['event_data']['host']).update(event=event['event'])
    except Exception as e:
        logging.error('Error: '+str(e))

    if event['event'] == 'runner_on_ok':
        try:
            Machines.objects.filter(name=event['event_data']['host']).update(status='running')

        except Exception as e:
            logging.error('Error: '+ e)

    if event['event'] == 'runner_on_start':
        try:
            Machines.objects.filter(name=event['event_data']['host']).update(status='running')

        except Exception as e:
            logging.error('Error: '+ e)

    elif event['event'] == 'playbook_on_stats':

        if event['event_data']['ok'] != {}:
            for ok in event['event_data']['ok'].keys():
                try:
                    Machines.objects.filter(name=ok).update(status='ok', monitor='server')
                except Exception as e:
                    logging.error('Error: ' + e)

        if event['event_data']['dark'] != {}:
            for dark in event['event_data']['dark'].keys():
                try:
                    Machines.objects.filter(name=dark).update(status='unreachable')
                except Exception as e:
                    logging.error('Error: ' + e)

        if event['event_data']['failures'] != {}:
            for failures in event['event_data']['failures'].keys():
                try:
                    Machines.objects.filter(name=failures).update(status='fails')
                except Exception as e:
                    logging.error('Error: ' + e)




def docker_event_handler(event):
    logging.info(str(event['stdout']))
    f = open('data/debug.txt', 'a')
    f.write('event: ' + str(event['stdout']) + '\n')
    f.close()
    print('event: ' + str(event))
    if event['event'] == 'runner_on_ok':
        try:
            dist = str(event['event_data']['res']['ansible_facts']['ansible_distribution'])
            version = str(event['event_data']['res']['ansible_facts']['ansible_distribution_release'])
            cores = int(event['event_data']['res']['ansible_facts']['ansible_processor_cores'])
            ram = int(event['event_data']['res']['ansible_facts']['ansible_memtotal_mb'])
            Machines.objects.filter(name=event['event_data']['host']).update(status='ok')
            # m1 = Machines(name=event['event_data']['host'],cores=cores,version=version, distribution=dist, ram=ram)
            # m1.save()
        except:
            pass
    elif event['event'] == 'runner_on_unreachable':
        try:
            Machines.objects.filter(name=event['event_data']['host']).update(status='unreachable')
        except:
            pass
    elif event['event'] == 'runner_on_failure':
        try:
            Machines.objects.filter(name=event['event_data']['host']).update(status='failure')
        except:
            pass
    elif event['event'] == 'playbook_on_stats':
        try:
            f = open('data/debug.txt', 'a')
            f.write('FINAL: ' + str(event['stdout']) + '\n')
            f.close()
        except:
            pass

    return event

def gather_facts_event_handler(event):
    logging.info(str(event['stdout']))
    f = open('data/debug.txt','a')
    f.write('event: '+str(event['stdout'])+ '\n')
    f.close()
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
    elif event['event']=='runner_on_unreachable':
        try:
            Machines.objects.filter(name=event['event_data']['host']).update(status='unreachable')
        except:
            pass

    elif event['event'] == 'playbook_on_stats':
        try:
            f = open('data/debug.txt', 'a')
            f.write('FINAL: ' + str(event['stdout']) + '\n')
            f.close()
        except:
            pass
    return event

def run_playbook(group_name, playbook, private_data_dir='.', inventory='data/inventory.yaml', ident='default_ident', event_handler=general_event_handler, status_handler=general_status_handler, json_mode=True):
    try:
        with open(playbook) as f:
            o = yaml.load(f, Loader=yaml.FullLoader)
            o[-1]['hosts'] = group_name
            s = open(playbook, 'w')
            yaml.dump(o, s)
            s.close()
            f.close()
    except:
        pass

    return ansible_runner.run_async(private_data_dir=private_data_dir, inventory=inventory, ident=ident,event_handler=event_handler, status_handler=status_handler,playbook=playbook, json_mode=json_mode)


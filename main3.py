import subprocess
import yaml

def setup(ip, port, key, user):
    o = {'all':{'hosts':{'fisica':{'ansible_host': ip,
                             'ansible_port': port,
                             'ansible_user': user,
                             'ansible_ssh_private_key_file':key,
                             'ansible_ssh_extra_args': '-o StrictHostKeyChecking=no'}}}}
    stream = open('prueba.yaml','w')
    yaml.dump(o,stream)

#setup('172.28.191.232', 22, '/keys/miclave', 'vagrant')
#r = subprocess.run(['ansible','-m','ping','-i','prueba.yaml','fisica'])
#r = subprocess.run(['ansible-playbook','setup.yml'])
#print(r)


def add_fisica(name, ip, port, key, user):
    try:
        with open('inventory.yaml') as f:
            o = yaml.load(f, Loader=yaml.FullLoader)
            if name in o['all']['hosts']:
                print('Escoje otro nombre')
    except FileNotFoundError:
        o={'all':{'hosts':{},'children':{'fisica':{'hosts':{name:{}}}}}}
    finally:
        o['all']['hosts'].update({name:{'ansible_host': ip,
                    'ansible_port': port,
                    'ansible_user': user,
                    'ansible_ssh_private_key_file': key,
                    'ansible_ssh_extra_args': '-o StrictHostKeyChecking=no'}})

        try:
            o['all']['children']['fisica']['hosts'].update({name:None})
        except KeyError:
            print('keyerror')
            o['all']['children'].update({'fisica':{'hosts':{name}}})

        s = open('inventory.yaml','w')
        yaml.dump(o,s)

    return 0

def add_virtual(name, ip, port, key, user):
    try:
        with open('inventory.yaml') as f:
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
        s = open('inventory.yaml', 'w')
        yaml.dump(o, s)

    return 0
    #r = subprocess.run(['ansible', '-m', 'ping', '-i', 'inventory.yaml', 'fisica'])

add_fisica('fisica1','172.28.123.153', 22, '/keys/miclave', 'vagrant')
add_fisica('fisica2','172.28.191.232', 22, '/keys/miclave', 'vagrant')
add_fisica('fisica3','172.28.14.233', 22, '/keys/miclave', 'vagrant')
add_fisica('fisica4','172.28.226.252', 22, '/keys/miclave', 'vagrant')
add_virtual('virtual1','178.62.6.15', 22, '/keys/miclave', 'root')
r = subprocess.run(['ansible', '-m', 'ping', '-i', 'inventory.yaml', 'virtual'])
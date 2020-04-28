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
        with open('prueba.yaml') as f:
            o = yaml.load(f, Loader=yaml.FullLoader)
            if name in o['all']['hosts']:
                print('Escoje otro nombre')
    except FileNotFoundError:
        o={'all':{'hosts':{},'children':{'fisica':{'hosts':{}}}}}
    finally:
        o['all']['hosts'][name]={'ansible_host': ip,
                    'ansible_port': port,
                    'ansible_user': user,
                    'ansible_ssh_private_key_file': key,
                    'ansible_ssh_extra_args': '-o StrictHostKeyChecking=no'}

        o['all']['children']['fisica']['hosts'][name]= None
        s = open('prueba.yaml','w')
        yaml.dump(o,s)

    #r = subprocess.run(['ansible', '-m', 'ping', '-i', 'prueba.yaml', 'fisica'])

add_fisica('fisica1','172.28.123.153', 22, '/keys/miclave', 'vagrant')
add_fisica('fisica2','172.28.191.232', 22, '/keys/miclave', 'vagrant')
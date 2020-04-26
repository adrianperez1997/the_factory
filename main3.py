import subprocess

r = subprocess.run(['ansible','-m','ping','fisica'])
print(r)
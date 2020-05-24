from django.db import models


class Group(models.Model):
    name=models.CharField(max_length=50, unique=True, primary_key=True, default='general')
    status=models.CharField(max_length=50, default='default')
    ram=models.IntegerField(default=0)
    cores=models.IntegerField(default=0)

# Create your models here.
class Machines(models.Model):
    name=models.CharField(max_length=50, unique=True, primary_key=True)
    ip=models.URLField(default='localhost')
    port=models.IntegerField(blank=True, default=22)
    key=models.CharField(max_length=250)
    user=models.CharField(max_length=50)
    setup=models.BooleanField(default=False)
    group=models.ForeignKey(Group, on_delete=models.CASCADE, default='default')
    cores=models.IntegerField(default=0)
    distribution=models.CharField(default='', max_length=50)
    version=models.CharField(default='', max_length=50)
    ram=models.IntegerField(default=0)
    status=models.CharField(default='default', max_length=50)

    def __str__(self):
        return 'Machine: ' + self.name + ' IP: ' + self.ip

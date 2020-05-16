from django.db import models

# Create your models here.
class Machines(models.Model):
    name=models.CharField(max_length=50, unique=True, primary_key=True)
    ip=models.CharField(max_length=15)
    port=models.IntegerField(blank=True, default=22)
    key=models.CharField(max_length=250)
    user=models.CharField(max_length=50)

    def __str__(self):
        return 'Machine: ' + self.name + ' IP: ' + self.ip

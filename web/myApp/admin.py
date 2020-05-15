from django.contrib import admin
from myApp.models import Machines
# Register your models here.
class machinesAdmin(admin.ModelAdmin):
    list_display=("name", "ip")
    search_fields = ("name", "ip", "user")

admin.site.register(Machines, machinesAdmin)
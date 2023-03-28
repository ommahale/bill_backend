from django.contrib import admin
from .models import BillUnit,BillMeter,Bill,Threshold,FaultBill
# Register your models here.
admin.site.register(FaultBill)
admin.site.register(BillUnit)
admin.site.register(BillMeter)
admin.site.register(Bill)

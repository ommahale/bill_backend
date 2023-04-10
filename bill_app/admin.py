from django.contrib import admin
from .models import BillUnit,BillMeter,Bill,Threshold,FaultBill,Voucher,RecieptFile,Category
# Register your models here.
admin.site.register(FaultBill)
admin.site.register(BillUnit)
admin.site.register(BillMeter)
admin.site.register(Bill)
admin.site.register(Threshold)
admin.site.register(Voucher)
admin.site.register(RecieptFile)
admin.site.register(Category)

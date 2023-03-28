from django.db import models
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

class BaseModel(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class BillUnit(BaseModel):
    unit_number=models.IntegerField()
class BillMeter(BaseModel):
    consumer_no=models.CharField(max_length=100)
    billing_unit=models.ForeignKey(BillUnit,on_delete=models.CASCADE)

class Bill(BaseModel):
    bill_no=models.CharField(max_length=100)
    bill_date=models.DateField()
    bill_amount=models.FloatField()
    bill_meter=models.ForeignKey(BillMeter,on_delete=models.CASCADE)
    due_date=models.DateField()
    incentive_due_date=models.DateField()
    incentive_amount=models.FloatField()
    is_paid=models.BooleanField(default=False)
    units_consumed=models.FloatField()
    bill_desc=models.CharField(max_length=100)
    connection_category = models.CharField(max_length=50,default='')
    connection_type = models.CharField(max_length=50,default="")
    region = models.CharField(max_length=50,default='')
    electrical_duty = models.FloatField(default=0)


class Threshold(BaseModel):
    threshold=models.FloatField()

class FaultBill(BaseModel):
    bill=models.ForeignKey(Bill,on_delete=models.CASCADE)
    fault_reason=models.CharField(max_length=100)

@receiver(post_save, sender=Bill)
def handleFault(sender, *args, **kwargs):
    if sender.electrical_duty > 0:
        FaultBill.objects.create(bill=sender,fault_reason="Electrical Duty is greater than 0")
    








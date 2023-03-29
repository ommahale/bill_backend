from django.db import models
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime
# Create your models here.

class BaseModel(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class BillUnit(BaseModel):
    unit_number=models.IntegerField()
    def __str__(self):
        return str(self.unit_number)
class BillMeter(BaseModel):
    consumer_no=models.CharField(max_length=100)
    billing_unit=models.ForeignKey(BillUnit,on_delete=models.CASCADE)
    def __str__(self):
        return self.consumer_no

class Bill(BaseModel):
    bill_date=models.DateField()
    amount=models.FloatField()
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
    @property
    def savings(self):
        return self.amount-self.incentive_amount
    @property
    def is_valid_for_incentive(self):
        if datetime.now().date() > self.incentive_due_date:
            return False
        return True
    def __str__(self):
        return self.bill_meter+" "+str(self.bill_date)


class Threshold(BaseModel):
    threshold=models.FloatField()

class FaultBill(BaseModel):
    bill=models.OneToOneField(Bill,on_delete=models.CASCADE,related_name="fault_bill")
    fault_reason=models.CharField(max_length=100)

class Voucher(BaseModel):
    bills = models.ManyToManyField(Bill)
    amount = models.FloatField()
    incentive_amount = models.FloatField(default=amount)
    unit = models.IntegerField()
    voucher_desc = models.CharField(max_length=50)
    voucher_date = models.DateField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    last_bill_date = models.DateField()
    last_bill_date = models.DateField()
    @property
    def savings(self):
        return self.amount-self.incentive_amount
    def __str__(self):
        return self.voucher_no
class RecieptFile(BaseModel):
    bill = models.OneToOneField(Bill,on_delete=models.CASCADE,related_name="reciept_file")
    reciept_file = models.FileField(upload_to='reciept_files/',blank=True,null=True)
    @property
    def pathToFile(self):
        return self.reciept_file.url
    def __str__(self):
        return self.bill.bill_meter.consumer_no+" "+str(self.bill.bill_date)
    


@receiver(post_save, sender=Bill)
def handleFault(sender,instance, **kwargs):
    if sender.electrical_duty > 0:
        FaultBill.objects.create(bill=sender,fault_reason="Electrical Duty is greater than 0")
        instance.has_fault = True
    else :
        objs=sender.objects.filter(bill_meter=instance.bill_meter).order_by('-bill_date')
        threshold=Threshold.objects.first()
        if len(objs) > 12:
            if (objs[0].units_consumed - objs[1].units_consumed > threshold.threshold*objs[0].units_consumed) or (objs[0].units_consumed - objs[11].units_consumed > threshold.threshold*objs[0].units_consumed):
                FaultBill.objects.create(bill=sender,fault_reason="Units consumed is greater than threshold")
                instance.has_fault = True
        if len(objs) > 1:
            if (objs[0].units_consumed - objs[1].units_consumed > threshold.threshold*objs[0].units_consumed):
                FaultBill.objects.create(bill=sender,fault_reason="Units consumed is greater than threshold")
                instance.has_fault = True

        
    








from django.db import models
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime
# Create your models here.

class BaseModel(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class BaseModelBigAuto(models.Model):
    uid = models.BigAutoField(primary_key=True, editable=False)
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
    has_fault=models.BooleanField(default=False)
    @property
    def savings(self):
        return self.amount-self.incentive_amount
    @property
    def is_valid_for_incentive(self):
        date=datetime.datetime.strptime(str(self.incentive_due_date),"%Y-%m-%d").date()
        # print(datetime.datetime.now().date() > date)
        if (datetime.datetime.now().date() >= date):
            return False
        return True
    def __str__(self):
        return self.bill_meter.consumer_no+" "+str(self.bill_date)


class Threshold(BaseModel):
    threshold=models.FloatField()

class FaultBill(BaseModel):
    bill=models.OneToOneField(Bill,on_delete=models.CASCADE,related_name="fault_bill")
    fault_reason=models.CharField(max_length=100)

class Voucher(BaseModelBigAuto):
    bills = models.ManyToManyField(Bill)
    uid = models.UUIDField(default=uuid.uuid4, editable=False)
    voucher_no = models.BigAutoField(primary_key=True)
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
    @property
    def total_amount(self):
        bills=self.bills.all()
        total_amount=0
        for bill in bills:
            if bill.is_valid_for_incentive:
                total_amount+=bill.incentive_amount
            else:
                total_amount+=bill.amount
        return total_amount
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
def handleFault(sender,instance,*args, **kwargs):
    if instance.electrical_duty > 0:
        print(instance.has_fault)
        bill=Bill.objects.get(uid=instance.uid)
        post_save.disconnect(handleFault,sender=sender)
        bill.has_fault=True
        bill.save()
        post_save.connect(handleFault,sender=sender)
        FaultBill.objects.create(bill=instance,fault_reason="Electrical Duty is greater than 0")
    else :
        objs=sender.objects.filter(bill_meter=instance.bill_meter).order_by('-bill_date')
        threshold=Threshold.objects.first()
        current_bill=objs.first()
        if len(objs) >= 12:
            prev_month_bill=objs[1]
            prev_year_bill=objs[11]
            if (current_bill.units_consumed - prev_month_bill.units_consumed > threshold.threshold*prev_month_bill.units_consumed) or (current_bill.units_consumed - prev_year_bill.units_consumed > threshold.threshold*prev_year_bill.units_consumed):
                print("Fault")
                FaultBill.objects.create(bill=instance,fault_reason="Units consumed is greater than threshold")
                post_save.disconnect(handleFault,sender=sender)
                bill.has_fault=True
                bill.save()
                post_save.connect(handleFault,sender=sender)
                return
        if len(objs) > 1:
            print("Fault")
            prev_month_bill=objs[1]
            if (current_bill.units_consumed - prev_month_bill.units_consumed > threshold.threshold*prev_month_bill.units_consumed):
                FaultBill.objects.create(bill=instance,fault_reason="Units consumed is greater than threshold")
                bill=Bill.objects.get(uid=instance.uid)
                post_save.disconnect(handleFault,sender=sender)
                bill.has_fault=True
                bill.save()
                post_save.connect(handleFault,sender=sender)
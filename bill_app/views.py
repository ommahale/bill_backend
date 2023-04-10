from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from . import models
from . import serializers
from .utils import apiKalwa
import datetime
# Create your views here.

class BillListApiView(ListAPIView):
    queryset=models.Bill.objects.all().order_by('-bill_date')
    serializer_class=serializers.BillSerializer
    def get_queryset(self):
        id=self.request.query_params.get('id',None)
        if id is not None:
            return models.Bill.objects.filter(uid=id).order_by('-bill_date')
        return models.Bill.objects.all().order_by('-bill_date')

class BillUnitListApiView(ListAPIView):
    queryset=models.BillUnit.objects.all()
    serializer_class=serializers.BillUnitSerializer

class FaultBillListApiView(ListAPIView):
    queryset=models.FaultBill.objects.all()
    serializer_class=serializers.FaultBillSerializer

class BillMeterListApiView(ListAPIView):
    queryset=models.BillMeter.objects.all()
    serializer_class=serializers.BillMeterSerializer

class AmountAnalyticsApiView(APIView):
    def get(self, request,bill_meter_id):
        meter_data=models.BillMeter.objects.get(uid=bill_meter_id)
        bills_data=models.Bill.objects.filter(bill_meter=meter_data).order_by('-bill_date')
        meter=serializers.BillMeterSerializer(meter_data).data
        data={}
        data['meter']=meter
        data['percentage_change']=(bills_data[0].amount-bills_data.last().amount)*100/bills_data.last().amount
        if len(bills_data)>1:
            data['monthly change']=(bills_data[0].amount-bills_data[1].amount)*100/bills_data[1].amount
        if len(bills_data)>=12:
            data['yearly change']=(bills_data[0].amount-bills_data[11].amount)*100/bills_data[11].amount
        return Response(data)

class CreateVoucherView(APIView):
    def post(self,request):
        try:
            amount=0
            incentive_amount=0
            data=request.data['bills']
            voucher=models.Voucher.objects.create()
            for bill in data:
                bill=models.Bill.objects.get(uid=bill['uid'])
                if bill is None:
                    return Response({"status":"bill {uid} not found".format(uid=bill['uid'])},status=status.HTTP_404_NOT_FOUND)
                if bill.has_fault:
                    voucher.fault_bills.add(bill)
                    bill.status="fault"
                bill.is_paid=True
                bill.save()
                amount+=bill.payable_amount
                if bill.is_valid_for_incentive:
                    incentive_amount+=bill.incentive_amount
                voucher.bills.add(bill)
                bill.status="pending"
            voucher.amount=amount
            voucher.incentive_amount=incentive_amount
            voucher.save()
            return Response({"status":"vocher created","uid":voucher.uid},status=status.HTTP_201_CREATED)
        except(ValueError):
            return Response({"status":"Invalid format"},status=status.HTTP_400_BAD_REQUEST)

class VoucherListApiView(ListAPIView):
    queryset=models.Voucher.objects.all()
    serializer_class=serializers.VoucherSerializer

class TestView(APIView):
    def get(self,request):
        fetch_DB_data()
        return Response({"status":"data"})
    
def fetchCycle():
    print("fetching.....")
    apiKalwa.getData()
    bills=apiKalwa.bills
    send_alert=False
    for bill in bills:
        bu=models.BillUnit.objects.get_or_create(unit_number=bill['bill_unit'])[0]
        bm=models.BillMeter.objects.get_or_create(consumer_no=bill['consumer_number'],billing_unit=bu)[0]
        category_data=models.Category.objects.get_or_create(
            connection_category=bill['connection_category'],
            connection_type=bill['connection_category'][:2],
        )[0]
        bill_db=models.Bill.objects.get_or_create(
            bill_date=datetime.datetime.strptime(bill['billDate'], '%d-%b-%y'),
            bill_meter=bm,
            amount=bill['amount'],
            incentive_amount=bill['incentive_amount'],
            due_date=datetime.datetime.strptime(bill['last_date'], '%d-%b-%y'),
            incentive_due_date=datetime.datetime.strptime(bill['incentive_date'], '%d-%b-%y'),
            units_consumed=float(bill['units_consumed'].replace(',','')),
            bill_desc=bill['bill_description'],
            connection=category_data,
            region='Kalwa',
            electrical_duty=bill['electrical_duty'],
            penalty_amount=bill['penalty_amount'],
            current_reading=bill['current_reading'],
            consumer_name=bill['consumer_name'],
        )
        if bill_db[0].has_fault:
            send_alert=True
    
    print("fetch cycle completed")

def fetch_DB_data():
    data=None
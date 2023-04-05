from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from . import models
from . import serializers
from .utils import apiKalwa
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
                if bill.has_fault:
                    continue
                bill.is_paid=True
                bill.save()
                amount+=bill.amount
                incentive_amount+=bill.incentive_amount
                voucher.bills.add(bill)
            voucher.amount=amount
            voucher.incentive_amount=incentive_amount
            voucher.save()
            return Response({"status":"vocher created","uid":voucher.uid})
        except(ValueError):
            return Response({"status":"Invalid format"})

class VoucherListApiView(ListAPIView):
    queryset=models.Voucher.objects.all()
    serializer_class=serializers.VoucherSerializer

class TestView(APIView):
    def get(self,request):
        # apiKalwa.getData()
        data=apiKalwa.username
        print(data)
        return Response({"status":data})
    
def fetchCycle():
    print("fetching")
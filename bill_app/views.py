from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from . import models
from . import serializers
from .utils import apiKalwa,getData
from rest_framework.permissions import IsAuthenticated
import datetime
from drf_yasg.utils import swagger_auto_schema
from django.template.loader import get_template
# Create your views here.
class BillListApiView(ListAPIView):
    queryset=models.Bill.objects.prefetch_related("bill_meter__billing_unit").all().order_by('-bill_date')
    serializer_class=serializers.BillSerializer
    # permission_classes=[IsAuthenticated]
    def get_queryset(self):
        id=self.request.query_params.get('id',None)
        if id is not None:
            return models.Bill.objects.filter(uid=id).prefetch_related("bill_meter__billing_unit").order_by('-bill_date')
        return models.Bill.objects.prefetch_related("bill_meter__billing_unit").all().order_by('-bill_date')

class BillUnitListApiView(ListAPIView):
    # permission_classes=[IsAuthenticated]
    queryset=models.BillUnit.objects.all()
    serializer_class=serializers.BillUnitSerializer

class FaultBillListApiView(ListAPIView):
    # permission_classes=[IsAuthenticated]
    queryset=models.FaultBill.objects.all().prefetch_related("bill__bill_meter__billing_unit").order_by('-bill__bill_date')
    serializer_class=serializers.FaultBillSerializer

class BillMeterListApiView(ListAPIView):
    # permission_classes=[IsAuthenticated]
    queryset=models.BillMeter.objects.all()
    serializer_class=serializers.BillMeterSerializer

class AmountAnalyticsApiView(APIView):
    def get(self, request,bill_meter_id):
        meter_data=models.BillMeter.objects.get(uid=bill_meter_id)
        bills_data=models.Bill.objects.filter(bill_meter=meter_data).order_by('-bill_date')
        meter=serializers.BillMeterSerializer(meter_data).data
        data={}
        data['meter']=meter
        data['percentage_change_amount']=(bills_data[0].amount-bills_data.last().amount)*100/bills_data.last().amount
        if len(bills_data)>1:
            data['monthly_change_amount']=(bills_data[0].amount-bills_data[1].amount)*100/bills_data[1].amount
        if len(bills_data)>=12:
            data['yearly_change_amount']=(bills_data[0].amount-bills_data[11].amount)*100/bills_data[11].amount
        data['percentage_change_unit']=(bills_data[0].units_consumed-bills_data.last().units_consumed)*100/bills_data.last().units_consumed
        if len(bills_data)>1:
            data['monthly_change_unit']=(bills_data[0].units_consumed-bills_data[1].units_consumed)*100/bills_data[1].units_consumed
        if len(bills_data)>=12:
            data['yearly_change_unit']=(bills_data[0].units_consumed-bills_data[11].units_consumed)*100/bills_data[11].units_consumed
        return Response(data)

class CreateVoucherView(APIView):
    @swagger_auto_schema(request_body=serializers.CreateVoucherSerializer)
    def post(self,request):
        try:
            amount=0
            incentive_amount=0
            data=request.data['bills']
            voucher=models.Voucher.objects.create()
            for bill in data:
                print(bill['uid'])
                bill=models.Bill.objects.get(uid=bill['uid'])
                if bill is None:
                    return Response({"status":"bill {uid} not found".format(uid=bill['uid'])},status=status.HTTP_404_NOT_FOUND)
                if bill.has_fault:
                    fault_bill=models.FaultBill.objects.get(bill=bill)
                    voucher.fault_bills.add(fault_bill)
                    print(serializers.FaultBillSerializer(fault_bill).data)
                    bill.status="fault"
                else:
                    voucher.bills.add(bill)
                    bill.status="pending"
                bill.save()
                amount+=bill.payable_amount
                if bill.is_valid_for_incentive:
                    incentive_amount+=bill.incentive_amount
            voucher.amount=amount
            voucher.incentive_amount=incentive_amount
            unit=request.data['unit']
            voucher.unit=int(unit)
            voucher.save()
            return Response({"status":"vocher created","uid":voucher.uid},status=status.HTTP_201_CREATED)
        except(ValueError):
            return Response({"status":"Invalid format"},status=status.HTTP_400_BAD_REQUEST)

class VoucherListApiView(ListAPIView):
    # permission_classes=[IsAuthenticated]
    queryset=models.Voucher.objects.all()
    serializer_class=serializers.VoucherSerializer

class VoucherDetailApiView(APIView):
    def get(self,request,uid):
        voucher=models.Voucher.objects.get(uid=uid)
        data=serializers.VoucherSerializer(voucher).data
        return Response(data)

class CategoryListApiView(ListAPIView):
    # permission_classes=[IsAuthenticated]
    queryset=models.Category.objects.all()
    serializer_class=serializers.CategoryBillsSerializer

class RefreshFault(APIView):
    def get(self,request):
        # fetch_DB_data()
        # fetchCycle()
        bills=models.Bill.objects.all()
        models.FaultBill.objects.all().delete()
        for bill in bills:
            bill.save()
        return Response({"status":"data"})

class TestView(APIView):
    def get(self,request):
        fetchCycle()
        # fetch_DB_data()
        return Response({"status":"data"})

def fetchCycle():
    print("fetching.....")
    try:
        apiKalwa.getData()
    except(AttributeError,ConnectionAbortedError):
        return Response({'error':'connection error'})
    bills=apiKalwa.bills
    send_alert=False
    fault_bills_count=0
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
        if bill_db[0].has_fault and bill_db[1]:
            send_alert=True
            fault_bills_count+=1
    
    print("fetch cycle completed")
    apiKalwa.bills=[]
    if send_alert:
        print('fault bills found:')
        print(fault_bills_count)

def fetch_DB_data():
    bills=getData()
    for bill in bills:
        bu=models.BillUnit.objects.get_or_create(unit_number=bill['billing_unit'])[0]
        bm=models.BillMeter.objects.get_or_create(consumer_no=bill['consumer_no'],billing_unit=bu)[0]
        category_data=models.Category.objects.get_or_create(
            connection_category=bill['connection_category'],
            connection_type=bill['connection_type'][:2],
        )[0]
        try:
            bill_db=models.Bill.objects.get(
                bill_date=datetime.datetime.strptime(bill['bill_date'], '%d-%b-%y'),
                bill_meter=bm,
                amount=bill['amount'],
                incentive_amount=bill['incentive_amount'],
                due_date=datetime.datetime.strptime(bill['due_date'], '%d-%b-%y'),
                incentive_due_date=datetime.datetime.strptime(bill['incentive_due_date'], '%d-%b-%y'),
                units_consumed=float(bill['unit_consumed']),
                bill_desc=bill['bill_desc'],
                connection=category_data,
                region='Kalwa',
                electrical_duty=bill['electrical_duty'],
                penalty_amount=bill['amount'],
                consumer_name=bill['consumer_name'],
            )
        except(models.Bill.DoesNotExist):
            models.Bill.objects.create(
            bill_date=datetime.datetime.strptime(bill['bill_date'], '%d-%b-%y'),
            bill_meter=bm,
            amount=bill['amount'],
            incentive_amount=bill['incentive_amount'],
            due_date=datetime.datetime.strptime(bill['due_date'], '%d-%b-%y'),
            incentive_due_date=datetime.datetime.strptime(bill['incentive_due_date'], '%d-%b-%y'),
            units_consumed=float(bill['unit_consumed']),
            bill_desc=bill['bill_desc'],
            connection=category_data,
            region='Kalwa',
            electrical_duty=bill['electrical_duty'],
            penalty_amount=bill['amount'],
            current_reading='NaN',
            consumer_name=bill['consumer_name'],
        )

class pdfAPI(APIView):
    def get(self,request,uid):
        template=get_template('template.html')
        data=models.Voucher.objects.get(uid=uid)
        serialzer=serializers.VoucherSerializer(data)
        context=serialzer.data
        # print(context)
        context["amt_1"]=100000
        context["amt_2"]=90000
        context["amt_3"]=50000
        context["amt_4"]=context["amt_3"]+context["amount"]
        context["amt_5"]=context["amt_2"]-(context["amount"]+context["amt_3"])
        for i in range(len(context['bills'])):
            context['bills'][i]['sr_no']=i+1
        context['voucher_datef']=datetime.datetime.strptime(str(context['voucher_date']),'%Y-%m-%d').strftime('%d/%m/%Y')
        html=template.render(context)
        return HttpResponse(html)

class ThresholdListView(ListAPIView):
    queryset=models.Threshold.objects.all()
    serializer_class=serializers.ThresholdSerializer
# fetchCycle()
# apiKalwa.getData()
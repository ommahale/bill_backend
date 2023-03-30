from django.shortcuts import render
from rest_framework.generics import ListAPIView
from . import models
from . import serializers
# Create your views here.

class BillListApiView(ListAPIView):
    queryset=models.Bill.objects.all()
    serializer_class=serializers.BillSerializer

class BillUnitListApiView(ListAPIView):
    queryset=models.BillUnit.objects.all()
    serializer_class=serializers.BillUnitSerializer
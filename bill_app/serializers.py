from rest_framework import serializers
from .models import Bill, BillMeter, BillUnit, FaultBill, Threshold, Voucher

class BillSerializer(serializers.ModelSerializer):
    class Meta:
        depth=2
        model = Bill
        fields = (
                  'uid', 
                  'bill_date', 
                  'amount', 
                  'due_date', 
                  'incentive_due_date', 
                  'incentive_amount', 
                  'is_paid', 
                  'units_consumed', 
                  'bill_desc', 
                  'connection_category', 
                  'connection_type', 
                  'region', 
                  'electrical_duty', 
                  'savings', 
                  'is_valid_for_incentive', 
                  'bill_meter', 
                  'fault_bill',
                  )

class BillMeterSerializer(serializers.ModelSerializer):
    class Meta:
        depth=2
        model = BillMeter
        fields = (
            'uid', 
            'consumer_no', 
            'billing_unit', 
            'bill_set'
            )

class BillUnitSerializer(serializers.ModelSerializer):
    class Meta:
        depth=2
        model = BillUnit
        fields = (
            'uid', 
            'unit_number', 
            'billmeter_set'
            )

class FaultBillSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaultBill
        fields = (
            'uid', 
            'fault_reason', 
            'bill'
            )
class ThresholdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Threshold
        fields = (
            'uid', 
            'threshold'
            )
class VoucherSerializer(serializers.ModelSerializer):
    class Meta:
        depth=2
        model = Voucher
        fields = (
            'uid', 
            'bills', 
            'voucher_no', 
            'amount', 
            'incentive_amount', 
            'unit', 
            'voucher_desc', 
            'voucher_date', 
            'is_paid', 
            'last_bill_date',
            'savings',
            'total_amount'
            )
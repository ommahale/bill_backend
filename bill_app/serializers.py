from rest_framework import serializers
from .models import Bill, BillMeter, BillUnit, FaultBill, Threshold, Voucher, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
                'uid', 
                'connection_type',
                'connection_category',

                )


        
class BillSerializer(serializers.ModelSerializer):
    consumer_no=serializers.SlugRelatedField(slug_field='consumer_no',read_only=True,source='bill_meter')
    connection_category=serializers.SlugRelatedField(slug_field='connection_category',read_only=True,source='connection')
    connection_type=serializers.SlugRelatedField(slug_field='connection_type', read_only=True,source='connection')
    billing_unit=serializers.SlugRelatedField(slug_field='unit_number',read_only=True,source='bill_meter.billing_unit')
    bill_date=serializers.DateField(format="%d/%m/%Y")
    due_date=serializers.DateField(format="%d/%m/%Y")
    incentive_due_date=serializers.DateField(format="%d/%m/%Y")
    class Meta:
        depth=1
        model = Bill
        fields = (
                  'uid', 
                  'consumer_no',
                  'billing_unit',
                  'bill_date', 
                  'amount', 
                  'due_date', 
                  'incentive_due_date', 
                  'incentive_amount',
                  'connection_category',
                  'connection_type',
                  'units_consumed', 
                  'bill_desc',
                  'region', 
                  'electrical_duty', 
                  'savings', 
                  'is_valid_for_incentive', 
                  'is_valid_for_penalty',
                  'has_fault',
                  'penalty_amount',
                  'current_reading',
                  'consumer_name',
                  'payable_amount',
                  'status',
                  )
        
class BillExcludeMeterSerializer(serializers.ModelSerializer):
    bill_date=serializers.DateField(format="%d/%m/%Y")
    due_date=serializers.DateField(format="%d/%m/%Y")
    incentive_due_date=serializers.DateField(format="%d/%m/%Y")
    connection_category=serializers.SlugRelatedField(slug_field='connection_category',read_only=True,source='connection')
    connection_type=serializers.SlugRelatedField(slug_field='connection_type', read_only=True,source='connection')
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
                  'connection_category',
                  'connection_type', 
                  'units_consumed', 
                  'bill_desc',
                  'region', 
                  'electrical_duty', 
                  'savings', 
                  'is_valid_for_incentive', 
                  'is_valid_for_penalty',
                  'has_fault',
                  'penalty_amount',
                  'current_reading',
                  'consumer_name',
                  'payable_amount',
                  'status',
                  )

class BillMeterSerializer(serializers.ModelSerializer):
    bill_set = BillExcludeMeterSerializer(many=True, read_only=True)
    class Meta:
        depth=2
        model = BillMeter
        fields = (
                'uid', 
                'consumer_no', 
                'billing_unit', 
                'bill_set'
                )
        
class BillMeterLowSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillMeter
        fields = (
                'uid', 
                'consumer_no',
                )

class VoucherBillUidSerializer(serializers.ModelSerializer):
    uid=serializers.CharField(read_only=False)
    class Meta:
        model = Bill
        fields = (
                'uid', 
                )

class CreateVoucherSerializer(serializers.ModelSerializer):
    bills=VoucherBillUidSerializer(many=True, read_only=False)
    unit=serializers.IntegerField(read_only=False)
    class Meta:
        model = Voucher
        fields = (
            'bills',
            'unit',
        )


class BillUnitSerializer(serializers.ModelSerializer):
    billmeter_set = BillMeterLowSerializer(many=True, read_only=True)
    class Meta:
        depth=2
        model = BillUnit
        fields = (
                'uid', 
                'unit_number', 
                'billmeter_set'
                )
class FaultBillSerializer(serializers.ModelSerializer):
    bill=BillSerializer(many=False, read_only=True)
    class Meta:
        model = FaultBill
        fields = (
                'uid', 
                'fault_reason', 
                'bill'
                )

class FaultBillDeepSerializer(serializers.ModelSerializer):
    bill = BillSerializer(many=False, read_only=True)
    class Meta:
        depth=2
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
    bills = BillSerializer(many=True, read_only=True)
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
                'last_bill_date',
                'savings',
                'total_amount',
                'fault_bills',
                'cleared_bills',
                )

class CategoryBillsSerializer(serializers.ModelSerializer):
    bills = BillSerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = (
                'uid', 
                'connection_type',
                'connection_category',
                'bills',
                )
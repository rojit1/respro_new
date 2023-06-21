from datetime import datetime
from api.serializers.bill import (
    BillDetailSerializer,
    BillItemSerializer,
    PaymentTypeSerializer,
    BillSerializer,
    TablReturnEntrySerializer,
    TblSalesEntrySerializer,
    TblTaxEntrySerializer,
    TblTaxEntryVoidSerializer,
    BillCheckSumSerializer
)
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response


from bill.models import Bill, PaymentType, TablReturnEntry, TblSalesEntry, TblTaxEntry, ConflictBillNumber
from organization.models import Branch, Organization
from product.models import BranchStockTracking
from django.shortcuts import get_object_or_404


class PaymentTypeList(ListAPIView):
    serializer_class = PaymentTypeSerializer
    queryset = PaymentType.objects.active()


class BillInfo(APIView):
    def get(self, request):
        branch_code = self.request.query_params.get("branch_code")
        terminal = self.request.query_params.get("terminal")
        branch_and_terminal = f"{branch_code}-{terminal}"
        if not branch_code or not terminal:
            return Response({"result": "Please enter branch code and terminal"},400)
        branch = get_object_or_404(Branch, branch_code=branch_code)
        current_fiscal_year = Organization.objects.last().current_fiscal_year
        last_bill_number = Bill.objects.filter(terminal=terminal, fiscal_year = current_fiscal_year, branch=branch).order_by('-bill_count_number').first()
        if last_bill_number:
            return Response({"result": last_bill_number.invoice_number})
        return Response({"result": 0})


class BillAPI(ModelViewSet):
    serializer_class = BillSerializer
    queryset = Bill.objects.active()

    def get_queryset(self, *args, **kwargs):
        queryset = Bill.objects.filter(
            is_deleted=False, status=True, agent=self.request.user
        )
        return queryset

    def get_serializer_class(self):
        detail_actions = ["retrieve", "list"]
        if self.action in detail_actions:
            return BillDetailSerializer
        return super().get_serializer_class()


class TblTaxEntryAPI(ModelViewSet):
    pagination_class = None
    serializer_class = TblTaxEntrySerializer
    queryset = TblTaxEntry.objects.all()

class TblTaxEntryUpdateView(APIView):
    
    def patch(self, request, bill_no):
        serializer = TblTaxEntryVoidSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        trans_date = serializer.validated_data.get('trans_date')

        try:
            bill_date = trans_date[:10]
            bill_date = datetime.strptime(bill_date, "%Y-%m-%d").date()
        except Exception:
            return Response({'message':'Date time format incorrect'}, status=400)
            

        instance = TblTaxEntry.objects.filter(bill_no=bill_no, bill_date=bill_date)

        if not instance:
            return Response({'message':'No data available with provided details'}, status=404)
        instance = instance.first()

        is_active_data = serializer.validated_data.get("is_active")
        reason = serializer.validated_data.get("reason")


        if is_active_data == "no":
            miti = ""
            quantity = 1
            try:
                print("TRY VITRA XU MA\n\n")
                obj = TblSalesEntry.objects.get(
                    bill_no=instance.bill_no, customer_pan=instance.customer_pan
                )
                print(obj)

                obj = Bill.objects.get(
                    invoice_number=instance.bill_no,
                    customer_tax_number=instance.customer_pan,
                )
                obj.status = False
                obj.save()
                # obj.save()

                print(obj)
                miti = obj.transaction_miti
                quantity = obj.bill_items.count()

                return_entry = TablReturnEntry(
                    bill_date=instance.bill_date,
                    bill_no=instance.bill_no,
                    customer_name=instance.customer_name,
                    customer_pan=instance.customer_pan,
                    amount=instance.amount,
                    NoTaxSales=0,
                    ZeroTaxSales=0,
                    taxable_amount=instance.taxable_amount,
                    tax_amount=instance.tax_amount,
                    miti=miti,
                    ServicedItem="Goods",
                    quantity=quantity,
                    reason=reason,
                )
                print(return_entry)
                return_entry.save()

            except:
                print("exception")
        instance.save()


        return Response({'message':'Successful'})


class TblSalesEntryAPI(ModelViewSet):
    serializer_class = TblSalesEntrySerializer
    queryset = TblSalesEntry.objects.all()


class TablReturnEntryAPI(ModelViewSet):
    serializer_class = TablReturnEntrySerializer
    queryset = TablReturnEntry.objects.all()


class BulkBillCreateView(APIView):

    def post(self, request):
        bills = request.data.get('bills', [])
        if not bills:
            return Response({'details':"Bills is required"}, status=400)
        conflict_invoices = []
        for bill in bills:
            serializer = BillSerializer(data=bill, context={'request':request})
            if serializer.is_valid():
                serializer.save()
            else:
                conflict_invoices.append(bill['invoice_number'])
                ConflictBillNumber.objects.create(invoice_number=bill['invoice_number'])
        if conflict_invoices:
            return Response({'details': conflict_invoices}, status=409)

        return Response({'details': 'Bills Created'}, status=201)


from datetime import date
class BillCheckSumView(APIView):

    def post(self, request):
        fiscal_year = Organization.objects.last().current_fiscal_year

        bills = request.data.get('bills', [])
        if not bills:
            return Response({'details':"Bills is required"}, status=400)
        new_invoice_list:list = []
        for bill in bills:
            invoice_num = bill.get('invoice_number', None)
            fiscal_year = bill.get('fiscal_year', fiscal_year)

            if not Bill.objects.filter(invoice_number=invoice_num, fiscal_year=fiscal_year).exists():
                if bill.get('payment_mode').lower() == "complimentary":
                    if Bill.objects.filter(fiscal_year=fiscal_year, transaction_date_time=bill.get('transaction_date_time')).exists():
                        continue
                new_invoice_list.append(invoice_num)
                serializer = BillSerializer(data=bill, context={'request':request})
                serializer.is_valid(raise_exception=True)
                try:
                    serializer.save()
                except Exception as e:
                    pass
        return Response({'details': 'ok', 'created_invoices':new_invoice_list})
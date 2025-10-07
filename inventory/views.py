from functools import reduce
from datetime import date
from django.db.models import Sum
from django.contrib.auth.models import Group
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from inventory.models import (
    Purchase,
    PurchaseItem,
    Product,
    SaleInvoice,
    SaleInvoiceItem,
    Provider,
)
from inventory.serializers import (
    PurchaseSerializer,
    PurchaseItemSerializer,
    PurchaseWithDetailSerializer,
    ProductSerializer,
    ProviderSerializer,
    SaleInvoiceWithDetailSerializer,
)
from inventory.filters import (
    PurchaseItemFilter,
    PurchaseFilter,
    SaleInvoiceFilter,
    ProductFilter,
)
from customers.models import Customer


class PurchaseViewSet(ModelViewSet):
    queryset = Purchase.objects.all()
    filterset_class = PurchaseFilter

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return PurchaseWithDetailSerializer
        return PurchaseSerializer


class SaleInvoiceViewSet(ModelViewSet):
    queryset = SaleInvoice.objects.all()
    filterset_class = SaleInvoiceFilter
    serializer_class = SaleInvoiceWithDetailSerializer


class PurchaseItemListView(generics.ListAPIView):
    queryset = PurchaseItem.objects.all()
    serializer_class = PurchaseItemSerializer
    filterset_class = PurchaseItemFilter


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_class = ProductFilter


class ProviderListView(generics.ListAPIView):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer


class NewPurchaseAPIView(APIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        purchaseList = request.data["purchaseList"]
        providerId = request.data["providerId"]
        provider = Provider.objects.get(pk=providerId)
        total = reduce(
            lambda x, y: x + (float(y["price"]) * float(y["quantity"])), purchaseList, 0
        )
        newPurchase = Purchase.objects.create(
            user=user,
            total=total,
            provider=provider,
        )
        for purchaseItem in purchaseList:
            quantity = float(purchaseItem["quantity"])
            product = Product.objects.get(pk=purchaseItem["productId"])
            product.increment_stock(int(quantity))
            PurchaseItem.objects.create(
                purchase=newPurchase,
                product=product,
                expiration_date=(
                    purchaseItem["expirationDate"]
                    if purchaseItem["expirationDate"]
                    else None
                ),
                price=float(purchaseItem["price"]),
                quantity=quantity,
                subtotal=float(quantity * float(purchaseItem["price"])),
            )
        return Response({"status": 200})


class VoidPurchase(APIView):
    def post(self, request):
        admin_group = Group.objects.get(name="administradores")
        user_groups = request.user.groups.all()

        if admin_group not in user_groups:
            return Response(status=403)
        purchase_id = request.data["purchaseId"]
        purchase = Purchase.objects.get(pk=purchase_id)
        purchase.void_purchase()
        return Response({"status": 200})


class NewSaleAPIView(APIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        saleList = request.data["saleList"]
        totalSale = 0
        customerId = request.data["customerId"]
        saleType = request.data["saleType"]
        customer = (
            Customer.objects.get(pk=customerId) if customerId is not None else None
        )
        for sale in saleList:
            soldProduct = Product.objects.get(pk=sale["productId"])
            subTotal = float(soldProduct.sale_price) * float(sale["quantity"])
            totalSale += subTotal

        newSaleInvoice = SaleInvoice.objects.create(
            user=user, customer=customer, total=totalSale, sale_type=saleType
        )

        for sale in saleList:
            product = Product.objects.get(pk=sale["productId"])
            product.decrement_stock(sale["quantity"])
            SaleInvoiceItem.objects.create(
                sale_invoice=newSaleInvoice,
                product=product,
                quantity=float(sale["quantity"]),
                subtotal=float(sale["quantity"] * product.sale_price),
                sale_price=product.sale_price,
            )

        return Response({"status": 200, "saleId": newSaleInvoice.id})


class VoidSale(APIView):
    def post(self, request):
        admin_group = Group.objects.get(name="administradores")
        user_groups = request.user.groups.all()

        if admin_group not in user_groups:
            return Response(status=403)
        sale_id = request.data["saleId"]
        sale = SaleInvoice.objects.get(pk=sale_id)
        sale.void_sale()
        return Response({"status": 200})


class Dashboard(APIView):
    def getAdminData(self, start_date, end_date):
        sales = SaleInvoice.objects.filter(
            sale_date__date__range=[start_date, end_date], voided=False
        )
        sales_total = sales.aggregate(total_sum=Sum("total", default=0))
        purchases = Purchase.objects.filter(
            purchase_date__date__range=[start_date, end_date], voided=False
        )
        purchases_total = purchases.aggregate(total_sum=Sum("total", default=0))
        customers_count = Customer.objects.count()
        sale_items_sum = SaleInvoiceItem.objects.filter(
            sale_invoice__sale_date__date__range=[start_date, end_date],
            sale_invoice__voided=False,
        ).aggregate(quantity_sum=Sum("quantity", default=0))
        sales_serializer = SaleInvoiceWithDetailSerializer(sales, many=True)

        data = {
            "sales_count": sales.count(),
            "sales_total": sales_total["total_sum"],
            "purchases_count": purchases.count(),
            "purchases_total": purchases_total["total_sum"],
            "sale_items_sum": sale_items_sum["quantity_sum"],
            "customers_count": customers_count,
            "sales": sales_serializer.data,
        }
        return Response({"data": data})

    def getSalesData(self, start_date, end_date, user):
        sales = SaleInvoice.objects.filter(
            sale_date__date__range=[start_date, end_date], voided=False, user=user
        )
        sales_total = sales.aggregate(total_sum=Sum("total", default=0))
        purchases = Purchase.objects.filter(
            purchase_date__date__range=[start_date, end_date], voided=False, user=user
        )
        purchases_total = purchases.aggregate(total_sum=Sum("total", default=0))
        customers_count = Customer.objects.count()
        sale_items_sum = SaleInvoiceItem.objects.filter(
            sale_invoice__sale_date__date__range=[start_date, end_date],
            sale_invoice__voided=False,
            sale_invoice__user=user,
        ).aggregate(quantity_sum=Sum("quantity", default=0))
        sales_serializer = SaleInvoiceWithDetailSerializer(sales, many=True)

        data = {
            "sales_count": sales.count(),
            "sales_total": sales_total["total_sum"],
            "purchases_count": purchases.count(),
            "purchases_total": purchases_total["total_sum"],
            "sale_items_sum": sale_items_sum["quantity_sum"],
            "customers_count": customers_count,
            "sales": sales_serializer.data,
        }
        return Response({"data": data})

    def post(self, request):
        print(request.data)
        user = request.user
        admin_group = Group.objects.get(name="administradores")
        sales_group = Group.objects.get(name="vendedores")
        user_groups = user.groups.all()

        # --- handle custom date range ---
        start_date = request.data.get("start_date")
        end_date = request.data.get("end_date")

        # fallback: default to today if not provided
        if not start_date or not end_date:
            today = date.today()
            start_date = today
            end_date = today

        if admin_group in user_groups:
            return self.getAdminData(start_date, end_date)

        if sales_group in user_groups:
            return self.getSalesData(start_date, end_date, user)

        return Response({"error": "User group not recognized"}, status=403)

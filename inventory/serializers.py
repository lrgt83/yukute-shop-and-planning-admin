from rest_framework import serializers
from inventory.models import Product, Purchase, PurchaseItem, Provider, SaleInvoice, SaleInvoiceItem
from users.serializers import UserSerializer
from customers.serializers import CustomerSerializer


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        depth = 1


class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = "__all__"


class PurchaseItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = PurchaseItem
        fields = "__all__"


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = "__all__"


class PurchaseWithDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    purchase_items = PurchaseItemSerializer(many=True)
    provider = ProviderSerializer()

    class Meta:
        model = Purchase
        fields = "__all__"


class SaleInvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleInvoiceItem
        exclude = ["sale_invoice"]
        depth = 2


class SaleInvoiceWithDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    customer = CustomerSerializer()
    sale_invoice_items = SaleInvoiceItemSerializer(many=True)
    class Meta:
        model = SaleInvoice
        fields = "__all__"

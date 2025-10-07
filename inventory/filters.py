from django_filters import rest_framework as filters, DateFromToRangeFilter
from inventory.models import PurchaseItem, Purchase, SaleInvoice, Product


class PurchaseFilter(filters.FilterSet):
    purchase_date = DateFromToRangeFilter()

    class Meta:
        model = Purchase
        fields = {
            'user__username': ["icontains"],
            'voided': ["exact",]
        }


class SaleInvoiceFilter(filters.FilterSet):
    sale_date = DateFromToRangeFilter()

    class Meta:
        model = SaleInvoice
        fields = {
            'user__username': ["icontains"],
            'voided': ["exact",],
            'customer__nit': ["icontains"],
            'customer__first_name': ["icontains"],
            'customer__last_name': ["icontains"],
        }


class PurchaseItemFilter(filters.FilterSet):
    expiration_date = DateFromToRangeFilter()

    class Meta:
        model = PurchaseItem
        fields = {
            'product__name': ["icontains"],
            'product__description': ["icontains"],
            'product__category__name': ["icontains"],
            'product__category__description': ["icontains"],
            'product__brand__name': ["icontains"],
            'product__brand__description': ["icontains"],
        }


class ProductFilter(filters.FilterSet):
    class Meta:
        model = Product
        fields = {
            'name': ["icontains"],
            'description': ["icontains"],
            'category__name': ["icontains"],
            'category__description': ["icontains"],
            'brand__name': ["icontains"],
            'brand__description': ["icontains"],
        }

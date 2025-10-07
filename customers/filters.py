from django_filters import rest_framework as filters
from customers.models import Customer


class CustomerFilter(filters.FilterSet):
  class Meta:
    model = Customer
    fields = {
      'nit': ["icontains"],
      'first_name': ["icontains"],
      'last_name': ["icontains"],
      'address': ["icontains"],
    }
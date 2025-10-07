from django.urls import path
from customers import views

app_name = 'customers'

urlpatterns = [
    path('', views.CustomerListView.as_view(), name='customers'),
]

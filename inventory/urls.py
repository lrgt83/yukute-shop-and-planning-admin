from django.urls import path, include
from rest_framework import routers

from inventory import views

app_name = 'inventory'

router = routers.DefaultRouter()

router.register('purchases', views.PurchaseViewSet, basename='purchases')
router.register('sales', views.SaleInvoiceViewSet, basename='sales')

urlpatterns = [
    path('', include(router.urls)),
    path('products/', views.ProductListView.as_view(), name='products'),
    path('purchase-items/', views.PurchaseItemListView.as_view(),
         name='purchase_item_list'),
    path('new-purchase/', views.NewPurchaseAPIView.as_view(), name='new-purchase'),
    path('new-sale/', views.NewSaleAPIView.as_view(), name='new-sale'),
    path('providers/', views.ProviderListView.as_view(), name='providers'),
    path('void-purchase/', views.VoidPurchase.as_view(), name='void-purchase'),
    path('void-sale/', views.VoidSale.as_view(), name='void-sale'),
    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),
]

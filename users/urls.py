from django.urls import path
from users import views

app_name = 'users'

urlpatterns = [
    path('users/', views.UsersListView.as_view(), name='users-list'),
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/verify/', views.CustomTokenVerifyView.as_view(), name='token_verify'),
]

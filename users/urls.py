from django.urls import path
from . import views

urlpatterns=[
    path('sales/', views.sales_data, name='sales_data'),
    path('categories/', views.category_data, name='category_data'),
    path('scatter/', views.scatter_data, name='scatter_data'),
    path('signup/', views.signup, name='signup'),
    path('get/', views.get_all, name='get_all'),
    path('login/', views.login, name='login'),
    path('update/', views.update_password, name='update_password')
]
from django.urls import path
from .views import ProductListCreateView, ProductDetailView

urlpatterns = [
    path('products/', ProductListCreateView.as_view(), name="products-list"), 
    path('products/<int:id>/', ProductDetailView.as_view(), name='product-detail'),
]


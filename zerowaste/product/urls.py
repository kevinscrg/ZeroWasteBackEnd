from django.urls import path
from .views import ProductListCreateView, ProductDetailView, UserProductListView, UserProductListDetailView

urlpatterns = [
    path('products/', ProductListCreateView.as_view(), name="products-list"), 
    path('products/<int:id>/', ProductDetailView.as_view(), name='product-detail'),
    path('user-product-lists/', UserProductListView.as_view(), name='user-product-list'),           # List or create lists
    path('user-product-lists/<int:pk>/', UserProductListDetailView.as_view(), name='user-product-list-detail'),  # Retrieve, update, or delete a specific list
]


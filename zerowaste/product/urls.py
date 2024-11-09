from django.urls import path
from .views import ProductListCreateView, ProductDetailView, UserProductListView, UploadReceiptImageView

urlpatterns = [
    path('products/', ProductListCreateView.as_view(), name="products-list"), 
    path('products/<int:id>/', ProductDetailView.as_view(), name='product-detail'),
    path('user-product-list/', UserProductListView.as_view(), name='user-product-list'), 
    path('upload-receipt/', UploadReceiptImageView.as_view(), name='upload-receipt'),
]


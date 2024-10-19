from django.urls import path
from .views import ProductListCreateView, ProductDetailView

urlpatterns = [
    path('', ProductListCreateView.as_view(), name="products-list"),
    path('<int:id>/', ProductDetailView.as_view(), name='product-detail'),
]


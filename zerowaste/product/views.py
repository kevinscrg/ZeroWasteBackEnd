from django.shortcuts import render

from rest_framework import generics
from .models import Product
from .serializers import ProductSerializer

#Handles GET and POST
class ProductListCreateView(generics.ListCreateAPIView):
    """
    View to list and create products.
    """
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    
    
    # Will implement later -> adding authentication and filtering the data based on the authenticated user
    
    # permission_classes = (permissions.IsAuthenticated,)

    # def perform_create(self, serializer):
    #     return serializer.save(owner=self.request.user)

    # def get_queryset(self):
    #     return self.queryset.filter(owner=self.request.user)
    
    
    
#Handles GET, PUT, PATCH, DELETE
class ProductDetailView(generics.RetrieveUpdateDestroyAPIView): 
    """
    View to retrieve, update, or delete a product.
    """
    serializer_class = ProductSerializer
    # permission_classes = (permissions.IsAuthenticated,)
    queryset = Product.objects.all()

    lookup_field = "id"
    
    # Will implement later -> adding authentication and filtering the data based on the authenticated user
    
    # def get_queryset(self):
    #     return self.queryset.filter(owner=self.request.user) 
    
    
    
    
    


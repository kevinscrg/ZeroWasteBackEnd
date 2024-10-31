
from rest_framework import generics, status  # type: ignore
from rest_framework.views import APIView # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework.permissions import IsAuthenticated # type: ignore

from .models import Product
from .serializers import DeleteProductSerializer, ProductSerializer, UserProductListSerializer, UpdateProductSerializer

#Handles GET and POST
class ProductListCreateView(generics.ListCreateAPIView):
    """
    View to list and create products.
    """
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    

    
    
#Handles GET, PUT, PATCH, DELETE
class ProductDetailView(generics.RetrieveUpdateDestroyAPIView): 
    """
    View to retrieve, update, or delete a product.
    """
    serializer_class = UpdateProductSerializer
    # permission_classes = (permissions.IsAuthenticated,)
    queryset = Product.objects.all()

    lookup_field = "id"


#? -------------------------------------------------------------------------


class UserProductListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_product_lists = request.user.product_list
        serializer = UserProductListSerializer(user_product_lists)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            user_product_lists = request.user.product_list
            user_product_lists.products.add(serializer.save())
            user_product_lists.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        user_product_lists = request.user.product_list
        serializer = UpdateProductSerializer(data=request.data)
        if serializer.is_valid():
            product_to_update = user_product_lists.products.get(id=serializer.validated_data['id'])
            product_to_update.name = serializer.validated_data['name']
            product_to_update.best_before = serializer.validated_data['best_before']
            product_to_update.consumption_days = serializer.validated_data['consumption_days']
            product_to_update.opened = serializer.validated_data['opened']
            product_to_update.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user_product_lists = request.user.product_list
        serializer = DeleteProductSerializer(data=request.data)
        if serializer.is_valid():
            product_to_delete = user_product_lists.products.get(id=serializer.validated_data['id'])
            user_product_lists.products.remove(product_to_delete)
            product_to_delete.delete()
            user_product_lists.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
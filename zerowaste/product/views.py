
from rest_framework import generics, status
from .models import Product
from .serializers import ProductSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import UserProductList
from .serializers import UserProductListSerializer
from rest_framework.permissions import IsAuthenticated

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
    

class UserProductListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_product_lists = UserProductList.objects.filter(owner=request.user)
        serializer = UserProductListSerializer(user_product_lists, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserProductListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)  # Set the owner to the authenticated user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProductListDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            user_product_list = UserProductList.objects.get(pk=pk, owner=request.user)
        except UserProductList.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = UserProductListSerializer(user_product_list)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            user_product_list = UserProductList.objects.get(pk=pk, owner=request.user)
        except UserProductList.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = UserProductListSerializer(user_product_list, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            user_product_list = UserProductList.objects.get(pk=pk, owner=request.user)
            user_product_list.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except UserProductList.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
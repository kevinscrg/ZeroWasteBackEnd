
from rest_framework import generics, status
from .models import Product
from .serializers import ProductSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserProductListSerializer
from rest_framework.permissions import IsAuthenticated

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
    serializer_class = ProductSerializer
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
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

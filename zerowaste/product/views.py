
import asyncio
from concurrent.futures import ThreadPoolExecutor
from rest_framework import generics, status  # type: ignore
from rest_framework.views import APIView # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework.permissions import IsAuthenticated # type: ignore
from django.core.files.storage import default_storage
from django.conf import settings
from django.shortcuts import get_object_or_404
from .services.receipt_processing import ReceiptProcessingAI
from .models import Product,UserProductList
from .serializers import DeleteProductSerializer, CreateProductSerializer, UserProductListSerializer, ProductSerializer, ReceiptImageUploadSerializer
from django.utils import timezone
import os

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
        serializer = CreateProductSerializer(data=request.data)
        if serializer.is_valid():
            user_product_lists = request.user.product_list
            user_product_lists.products.add(serializer.save())
            user_product_lists.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        user_product_lists = request.user.product_list
        serializer = ProductSerializer(data=request.data)  
        if serializer.is_valid():
            product_to_update = user_product_lists.products.get(id=serializer.validated_data['id'])
            product_to_update.name = serializer.validated_data['name'] if 'name' in serializer.validated_data else product_to_update.name
            product_to_update.best_before = serializer.validated_data['best_before'] if 'best_before' in serializer.validated_data else product_to_update.best_before
            product_to_update.consumption_days = serializer.validated_data['consumption_days'] if 'consumption_days' in serializer.validated_data else product_to_update.consumption_days
            product_to_update.opened = serializer.validated_data['opened'] if 'opened' in serializer.validated_data else product_to_update.opened
            product_to_update.save()
            return Response(ProductSerializer(product_to_update).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user_product_lists = request.user.product_list
        serializer = DeleteProductSerializer(data=request.data)
        if serializer.is_valid():
            product_to_delete = get_object_or_404(user_product_lists.products, id=serializer.validated_data['id'])
            user_product_lists.products.remove(product_to_delete)
            product_to_delete.delete()
            user_product_lists.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UploadReceiptImageView(APIView):
    def post(self, request):
        """
        Handle receipt image upload, process with OCR, and return product list.
        Optionally, save these products to the user's product list.
        """
        serializer = ReceiptImageUploadSerializer(data=request.data)
        if serializer.is_valid():
            image_file = serializer.validated_data['image']

            # Define directory path
            directory_path = os.path.join(settings.MEDIA_ROOT, 'food-item-tickets')

            # Create directory if not exists
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)

            # Define file path and save image
            file_path = os.path.join(directory_path, image_file.name)
            with open(file_path, 'wb') as f:
                for chunk in image_file.chunks():
                    f.write(chunk)

            # Initialize OCR service and run process_receipt
            ocr_service = ReceiptProcessingAI()

            # Run process_receipt asynchronously but wait for the result
            products = asyncio.run(ocr_service.process_receipt(file_path))

            # Get user and their product list
            user = request.user
            user_product_list = user.product_list
            product_objects = []

            # Loop through products and add them to user product list
            for product_name in products:
                product, created = Product.objects.get_or_create(
                    name=product_name,
                    defaults={
                        'best_before': None,
                        'consumption_days': None,
                        'opened': None
                    }
                )
                user_product_list.products.add(product)
                product_objects.append(product)

            # Save user's product list and clean up uploaded file
            user_product_list.save()
            os.remove(file_path)

            # Return serialized product data
            return Response({
                "products": ProductSerializer(product_objects, many=True).data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

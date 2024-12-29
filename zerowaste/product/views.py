import os
from rest_framework import generics, status  # type: ignore
from rest_framework.views import APIView # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework.permissions import IsAuthenticated # type: ignore
from django.shortcuts import get_object_or_404

from zerowaste import settings
from .services.tasks import process_and_save_products_task
from .models import Product
from .serializers import DeleteProductSerializer, CreateProductSerializer, UserProductListSerializer, ProductSerializer, ReceiptImageUploadSerializer

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


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
            message = {
                    'type': 'productmessage',  
                    'message': {
                        'type': 'add_product',
                        'data': ProductSerializer(serializer.save()).data
                    }
            }
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'notifications{user_product_lists.share_code}',
                 message
                )
            
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
            
            message = {
                    'type': 'productmessage',  
                    'message': {
                        'type': 'update_product',
                        'data': ProductSerializer(product_to_update).data
                    }
            }
            
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'notifications{user_product_lists.share_code}',
                 message
                )
            
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
            
            message = {
                    'type': 'productmessage',  
                    'message': {
                        'type': 'delete_product',
                        'data': serializer.validated_data['id']
                    }
            }
            
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'notifications{user_product_lists.share_code}',
                 message
                )
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UploadReceiptImageView(APIView):
    
    def post(self, request):
        serializer = ReceiptImageUploadSerializer(data=request.data)
        if serializer.is_valid():
            image_file = serializer.validated_data['image']
            
            # Define directory path
            directory_path = os.path.join(settings.BASE_DIR, 'food-item-tickets')

            # Create directory if not exists
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)
            # Salvează imaginea pe disc pentru a o transmite lui Celery
            image_file_path = os.path.join(directory_path, image_file.name)
            with open(image_file_path, 'wb+') as destination:
                for chunk in image_file.chunks():
                    destination.write(chunk)

            # Lansează task-ul Celery
            process_and_save_products_task.delay(image_file_path, request.user.id)

            return Response({"message": "Processing started"}, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# tasks.py

from celery import shared_task
from .receipt_processing import ReceiptProcessingAI
from django.contrib.auth import get_user_model
from PIL import Image
import numpy as np
from ..models import Product
import os
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


User = get_user_model()

@shared_task
def process_and_save_products_task(image_file_path, user_id):
    try:

        # Încarcă imaginea de la path
        image = Image.open(image_file_path)
        image = np.array(image)

        ocr_service = ReceiptProcessingAI()
        products = ocr_service.process_receipt(image)

        # Obține lista de produse a utilizatorului
        user = User.objects.get(id=user_id)
        user_product_list = user.product_list

        # Adaugă produsele în lista utilizatorului
        for product_name in products:
            product = Product.objects.create(name=product_name)
            user_product_list.products.add(product)

        user_product_list.save()
        
        message = {
            "type": "productmessage",
            "message": {
                "type": "add_products",
                "data": "ok"}
        }
        
        channel_layer = get_channel_layer()
        
        async_to_sync(channel_layer.group_send)(
            f'notifications{user_product_list.share_code}',  
             message
            )

        if os.path.exists(image_file_path):
            os.remove(image_file_path)

    except Exception as e:
        print(f"Error processing receipt image: {e}")




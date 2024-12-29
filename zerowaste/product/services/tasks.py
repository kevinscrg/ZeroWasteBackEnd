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
from django.core.mail import send_mail
from django.utils.timezone import localtime, now, make_aware
from datetime import datetime, timedelta

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


@shared_task
def send_email_to_user(user_id):
    try:
        user = User.objects.get(id=user_id)
        expiration_date = now() + timedelta(days=user.notification_day)

        products_to_expire = user.product_list.products.filter(best_before=expiration_date)

        if user.is_verified and products_to_expire.exists():
            product_names = ", ".join([product.name for product in products_to_expire])

            send_mail(
                subject="Your products are expiring soon",
                message=f"The following products are expiring soon: {product_names}",
                from_email="zerowastenoreply@gmail.com",
                recipient_list=[user.email],
            )
            return f"Email sent to {user.email}"
        else:
            return f"No email sent to {user.email}: User not verified or no products to notify."
    except User.DoesNotExist:
        return f"User with id {user_id} does not exist."
    except Exception as e:
        return f"Error while sending email to user {user_id}: {str(e)}"



@shared_task
def schedule_daily_emails():
    """
    Programează emailurile pentru utilizatori în funcție de ora preferată și produsele care expiră.
    """
    today = localtime(now()).date()
    users = User.objects.all()
    tasks_scheduled = 0
    for user in users:
        if user.preferred_notification_hour is not None:
            notification_time = datetime.combine(today, user.preferred_notification_hour)
            notification_time = make_aware(notification_time)
            expiration_date = now() + timedelta(days=user.notification_day)

            products_to_expire = user.product_list.products.filter(best_before=expiration_date)
            if products_to_expire.exists() and notification_time > now():
                send_email_to_user.apply_async(
                    args=[user.id],
                    eta=notification_time
                )
                tasks_scheduled += 1

    return f"Scheduled {tasks_scheduled} tasks for {today}."


from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 
                  'name', 
                  'best_before', 
                  'consumption_days', 
                  'opened']

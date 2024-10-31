from rest_framework import serializers # type: ignore
from .models import Product, UserProductList

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 
                    'best_before', 
                    'consumption_days', 
                    'opened']
        
class UpdateProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id',
                    'name', 
                    'best_before', 
                    'consumption_days', 
                    'opened']

class DeleteProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id']
        
    def validate(self, data):
        if not Product.objects.filter(id=data['id']).exists():
            raise serializers.ValidationError('Product with this id does not exist!')
        return data

class UserProductListSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True)

    class Meta:
        model = UserProductList
        fields = ['share_code','products']

    def create(self, validated_data):
        # Extract product data from the validated data
        products_data = validated_data.pop('products')
        
        # Create the UserProductList instance
        user_product_list = UserProductList.objects.create(**validated_data)

        # Loop through each product in the products_data and create it
        for product_data in products_data:
            # Here we create the product instance
            product = Product.objects.create(**product_data)  # Creates a new product instance
            user_product_list.products.add(product)  # Adds the product to the user's product list

        return user_product_list
    
    def update(self, instance, validated_data):
        # Update the products list
        products_data = validated_data.pop('products', [])
        
        # Clear existing products
        instance.products.clear()
        
        # Create and add new products to the instance
        for product_data in products_data:
            product, created = Product.objects.update_or_create(
                id=product_data.get('id'),
                defaults={
                    'name': product_data.get('name'),
                    'best_before': product_data.get('best_before'),
                    'consumption_days': product_data.get('consumption_days'),
                    'opened': product_data.get('opened'),
                }
            )
            instance.products.add(product)
        
        instance.save()
        return instance
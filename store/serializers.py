from rest_framework import serializers

from .models import Category, Product, ProductImage


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image", "alt_text"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["name", "slug"]


class ProductSerializer(serializers.ModelSerializer):
    product_image = ImageSerializer(many=True, read_only=True)
    category = CategorySerializer()

    class Meta:
        model = Product
        fields = ["id", "category", "title", "description",
                  "slug", "regular_price", "brand", "rating_number", "rating", "product_image"]

class ProductBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["brand"]
    
    

class ProductsSerializer(serializers.ModelSerializer):
    product_image = ImageSerializer(many=True, read_only=True)
    # category = CategorySerializer() if you want to add the category details in product data

    class Meta:
        model = Product
        fields = ["id", "title", "description",
                  "slug", "regular_price", "brand", "rating", "product_image"]

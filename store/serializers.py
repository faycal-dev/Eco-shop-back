from rest_framework import serializers

from .models import Category, Product, ProductImage, ProductSpecificationValue, ProductType


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image", "alt_text"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["name", "slug"]


class ProductSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSpecificationValue
        fields = ["id","specification", "value"]
        depth=1


class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = ["id","name", "is_active"]


class ProductSerializer(serializers.ModelSerializer):
    product_image = ImageSerializer(many=True, read_only=True)
    category = CategorySerializer()
    product_type = ProductTypeSerializer()
    productSpecificationValue = ProductSpecificationSerializer(many=True)

    class Meta:
        model = Product
        fields = ["id", "category", "title", "description",
                  "slug", "regular_price", "brand", "rating_number", "rating", "product_image", "product_type", "productSpecificationValue"]


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
                  "slug", "regular_price", "brand", "rating", "product_image", "is_active"]

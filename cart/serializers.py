from rest_framework import serializers

from store.serializers import ProductsSerializer

from .models import Order, Items


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductsSerializer()

    class Meta:
        model = Items
        fields = ["id", "product", "price", "quantity"]
        depth = 1


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "total_price", "items", "updated"]

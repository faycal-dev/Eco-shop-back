from functools import total_ordering
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from . import models
from store.models import Product
from .serializers import OrderSerializer


# ---------------------------------------custom permission----------------------------------------------------------------


class CartUserWritePermission(permissions.BasePermission):
    message = "Editing cart is restricted the author only!"

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

# -------------------------------------------------------------------------------------------------------------------------


class GetCartView(generics.ListAPIView, CartUserWritePermission):
    permission_classes = (CartUserWritePermission, )
    serializer_class = OrderSerializer

    def get_queryset(self):
        current_user = self.request.user

        return models.Order.objects.filter(user=current_user, billing_status=False)


class AddItemToCart(APIView, CartUserWritePermission):
    permission_classes = (CartUserWritePermission, )

    def post(self, request):
        product_id = request.data["product_id"]
        product_object = get_object_or_404(Product, id=product_id)

        try:
            if (models.Order.objects.filter(user=request.user, billing_status=False).exists()):
                cart_object = models.Order.objects.get(
                    user=request.user, billing_status=False)
                total_price = cart_object.total_price + product_object.regular_price
                cart_object.total_price = round(total_price, 2)
                cart_object.save()

                if (models.Items.objects.filter(order=cart_object, product=product_object).exists()):
                    item = models.Items.objects.get(
                        order=cart_object, product=product_object)
                    item.quantity += 1
                    item.save()
                else:
                    models.Items.objects.create(
                        order=cart_object, product=product_object, price=product_object.regular_price)

                return Response({"success": "Product added to cart"}, status=status.HTTP_201_CREATED)
            else:
                cart_object = models.Order.objects.create(
                    user=request.user, total_price=product_object.regular_price)
                models.Items.objects.create(
                    order=cart_object, product=product_object, price=product_object.regular_price)

                return Response({"success": "Product added to a new cart"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': 'Something went wrong when trying to add product to cart'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ModifyCartItem(APIView, CartUserWritePermission):
    permission_classes = (CartUserWritePermission, )

    def put(self, request):
        try:
            product_quantity = request.data["quantity"]
            product_id = request.data["id"]
            if (product_quantity < 1):
                return Response({"error": "Quantity must be grater than 1"}, status=status.HTTP_400_BAD_REQUEST)

            if (models.Order.objects.filter(user=request.user, billing_status=False).exists()):
                cart_object = models.Order.objects.get(
                    user=request.user, billing_status=False)
                item = get_object_or_404(
                    models.Items, order=cart_object.id, product=product_id)
                old_quantity = item.quantity
                total_price = cart_object.total_price + \
                    ((product_quantity - old_quantity) * item.price)
                cart_object.total_price = round(total_price, 2)
                item.quantity = product_quantity
                item.save()
                cart_object.save()
                return Response({"success": "Cart item updated successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': 'Something went wrong when trying to modify the cart product'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request):
        try:
            product_id = request.data["id"]
            if (models.Order.objects.filter(user=request.user, billing_status=False).exists()):
                cart_object = models.Order.objects.get(
                    user=request.user, billing_status=False)
                item = get_object_or_404(
                    models.Items, order=cart_object.id, product=product_id)
                total_price = cart_object.total_price - \
                    (item.price * item.quantity)
                cart_object.total_price = round(total_price, 2)
                item.delete()
                cart_object.save()
                return Response({"success": "Cart item deleted successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': 'Something went wrong when trying to delete the cart product'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            

class Chekout(APIView, CartUserWritePermission):
    permission_classes = (CartUserWritePermission, )
    
    def post(self, request):
        try:
            models.Order.objects.filter(user=request.user, billing_status=False).update(billing_status=True)
            return Response({"success": "Chekout validated successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': 'Something went wrong when trying to Validate the chekout'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            


class GetOrdersView(generics.ListAPIView):
    permission_classes = (CartUserWritePermission, )
    serializer_class = OrderSerializer

    def get_queryset(self):
        current_user = self.request.user

        return models.Order.objects.filter(user=current_user, billing_status=True)

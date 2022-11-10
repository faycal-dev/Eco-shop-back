from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response


from . import models
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer, ProductsSerializer, ProductBrandSerializer

# ---------------------------------------custom permission----------------------------------------------------------------


class WishlistUserWritePermission(permissions.BasePermission):
    message = "Editing wishlist is restricted the author only!"

    def has_object_permission(self, request, view, obj):
        return obj.users_wishlist == request.user

# -------------------------------------------------------------------------------------------------------------------------


class ProductListView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    queryset = Product.objects.all()
    serializer_class = ProductsSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description', 'rating']


class ProductBrandListView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    queryset = Product.objects.all().distinct("brand").order_by("brand")
    serializer_class = ProductBrandSerializer


class Product(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    lookup_field = "slug"
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class CategoryItemView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    serializer_class = ProductSerializer

    # this function is used to retrive all products with the desired category or its decendents
    def get_queryset(self):
        return models.Product.objects.filter(
            category__in=Category.objects.get(
                slug=self.kwargs["slug"]).get_descendants(include_self=True)
        )


class CategoryListView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    queryset = Category.objects.filter(
        level=0).get_descendants(include_self=True)
    serializer_class = CategorySerializer


class WishlistView(APIView, WishlistUserWritePermission):
    permission_classes = (WishlistUserWritePermission, )
    serializer_class = ProductsSerializer

    def get(self, request):
        try:
            products = models.Product.objects.filter(
                users_wishlist=request.user)
            serializer = self.serializer_class(products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': 'Something went wrong when trying to get whishlist'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ToggleProductToWishlistView(APIView, WishlistUserWritePermission):
    permission_classes = (WishlistUserWritePermission, )

    def post(self, request, id):
        try:
            product = models.Product.objects.get(id=id)
            if product.users_wishlist.filter(id=request.user.id).exists():
                product.users_wishlist.remove(request.user)
                return Response({'success': 'Product removed from wishlist'}, status=status.HTTP_200_OK)
            else:
                product.users_wishlist.add(request.user)
                return Response({'success': 'Product added to wishlist'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': 'Something went wrong when trying to modify whishlist'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

from django.shortcuts import render
from rest_framework import generics, permissions

from . import models
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer, ProductsSerializer, ProductBrandSerializer


class ProductListView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    queryset = Product.objects.all()
    serializer_class = ProductsSerializer
    
class ProductBrandListView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    queryset = Product.objects.all().distinct().order_by("brand")
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
            category__in=Category.objects.get(slug=self.kwargs["slug"]).get_descendants(include_self=True)
        )


class CategoryListView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    queryset = Category.objects.filter(level=0).get_descendants(include_self=True)
    serializer_class = CategorySerializer
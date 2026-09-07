from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .models import Brand, Category, Product
from .serializers import CategorySerializer, BrandSerializer, ProductSerializer
from rest_framework.views import APIView
from rest_framework import generics, viewsets
from rest_framework.pagination import LimitOffsetPagination, CursorPagination
from .pagination import CustomPagination, CustomCursorPagination


# Create your views here.
@api_view(["GET", "POST"])
def index_view(request):
    return Response(
        {"message": "Welcome to the Product App!"}, status=status.HTTP_200_OK
    )


@api_view(["GET", "POST"])
def category_list_view(request):
    if request.method == "POST":
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(
            {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )
    else:
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
def category_detail_view(request, id):
    try:
        category = Category.objects.get(id=id)
    except Category.DoesNotExist:
        return Response(
            {"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "PUT":
        serializer = CategorySerializer(data=request.data, instance=category)

        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        return Response(
            {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    elif request.method == "PATCH":
        serializer = CategorySerializer(
            data=request.data, instance=category, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        return Response(
            {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    elif request.method == "DELETE":
        category.delete()
        return Response(
            {"message": "Category deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )

    else:
        serializer = CategorySerializer(category)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)


class BrandView(APIView):

    def get(self, request, id=None):
        brand_obj = Brand.objects.all()
        if id:
            try:
                brand = self.brand_obj.get(id=id)
                serializer = BrandSerializer(brand)

                return Response(serializer.data, status=status.HTTP_200_OK)
            except Brand.DoesNotExist:
                return Response(
                    {"error": "Brand Not Found"}, status=status.HTTP_404_NOT_FOUND
                )
        else:
            serializer = BrandSerializer(brand_obj, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        brand_obj = Brand.objects.all()
        serializer = BrandSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(
            {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    def put(self, request, id):
        brand_obj = Brand.objects.all()
        if id:
            try:
                brand = self.brand_obj.get(id=id)
                serializer = BrandSerializer(data=request.data, instance=brand)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Brand.DoesNotExist:
                return Response(
                    {"error": "Brand Not Found"}, status=status.HTTP_404_NOT_FOUND
                )
        else:
            serializer = BrandSerializer(brand_obj, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, id):
        brand_obj = Brand.objects.all()
        if id:
            try:
                brand = self.brand_obj.get(id=id)
                serializer = BrandSerializer(
                    data=request.data, instance=brand, partial=True
                )
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Brand.DoesNotExist:
                return Response(
                    {"error": "Brand Not Found"}, status=status.HTTP_404_NOT_FOUND
                )
        else:
            serializer = BrandSerializer(self.brand_obj, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, id):
        brand_obj = Brand.objects.all()
        if id:
            try:
                brand = self.brand_obj.get(id=id)
                brand.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Brand.DoesNotExist:
                return Response(
                    {"error": "Brand not found"}, status=status.HTTP_404_NOT_FOUND
                )


class GenericBrandView(generics.ListCreateAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


class GenericBrandDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    lookup_field = "id"

    def get_queryset(self):
        query_params = self.request.query_params
        category_id = query_params.get("category_id")
        category_name = query_params.get("category_name")
        brand_name = query_params.get("name")
        if category_id:
            return self.queryset.filter(category__id=category_id)
        if category_name:
            return self.queryset.filter(category__name=category_name)
        if brand_name:
            return self.queryset.filter(name__exact=brand_name)
        return self.queryset


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = "id"
    pagination_class = CustomCursorPagination
    # pagination_class = CustomPagination

    def get_queryset(self):
        queryset = Product.objects.all()
        query_params = self.request.query_params

        brand_id = query_params.get("brand_id")

        category_id = query_params.get("category_id")

        if brand_id:
            queryset = self.queryset.filter(brand__id=brand_id)

        if category_id:
            queryset = self.queryset.filter(category__id=category_id)

        return queryset

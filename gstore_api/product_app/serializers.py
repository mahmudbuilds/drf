from rest_framework import serializers
from .models import Category, Brand, Product


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = "__all__"

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class BrandSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["category"] = CategorySerializer(instance.category).data
        return representation

    class Meta:
        model = Brand
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # representation['brand'] = BrandSerializer(instance.brand).data

        representation["brand"] = {
            "id": instance.brand.id,
            "name": instance.brand.name,
            "category_name": instance.brand.category.name,
        }

        image = None

        if representation["image"]:
            image = representation["image"]

        elif representation["image_link"]:
            image = representation["image"]

        representation.pop("image")
        representation.pop("image_link")

        representation["image"] = image

        return representation

    def validate(self, attrs):
        if attrs.get("image") and attrs.get("image"):
            raise serializers.ValidationError(
                "You can either use image link or upload the image itself."
            )

        return super().validate(attrs)

    class Meta:
        model = Product
        fields = "__all__"

from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=True)
router.register(r"brand-viewset", views.BrandViewSet)
router.register(r"product-viewset", views.ProductViewSet)

urlpatterns = [
    path("", views.index_view, name="index"),
    path("category", views.category_list_view, name="category-list"),
    path("category/<int:id>", views.category_detail_view, name="category-detail"),
    path("brand", views.BrandView.as_view()),
    path("brand/<int:id>", views.BrandView.as_view()),
    path("generic-brand/", views.GenericBrandView.as_view(), name="generic-brand"),
    path("generic-brand/<int:pk>", views.GenericBrandDetailView.as_view(), name="generic-brand-detail"),
    path("", include(router.urls))
]
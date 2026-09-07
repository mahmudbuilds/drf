from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r"", views.UserViewset, basename="users")

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("get-otp/", views.GetOTPView.as_view(), name="get-otp"),
    path("verify-otp/", views.VerifyOtpView.as_view(), name="verify-otp"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("", include(router.urls))
]


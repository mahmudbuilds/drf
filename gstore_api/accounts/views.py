from django.shortcuts import render
from rest_framework.views import APIView
from .models import CustomUser
from .serializers import RegisterSerializer, LoginSerializer, send_otp_email, GetOTPSerializer, VerifyOTPSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination

# Create your views here.
class RegisterView(APIView):
    def post(self, request):
        data = request.data
        serializer = RegisterSerializer(data=data)
        if serializer.is_valid(): 
            serializer.save()
            return Response({"message": "Registration successful"}, status=status.HTTP_201_CREATED)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    
class VerifyOtpView(APIView):
    def post(self, request):
        data = request.data
        serializer = VerifyOTPSerializer(data=data)
        if not serializer.is_valid():
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data.get("email")
        otp = serializer.validated_data.get("otp")
        try: 
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({"errors": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if user.verify_otp(otp):
            user.is_verified = True
            user.save()
            return Response({"message": "OTP verification successful"}, status=status.HTTP_200_OK)
        return Response({"errors": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
    
class GetOTPView(APIView):
    
    def post(self, request):
        data = request.data
        serializer = GetOTPSerializer(data=data)
        if not serializer.is_valid():
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data.get("email")
        try: 
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({"errors": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        otp = user.generate_otp()
        user.email_user("OTP Verification", f"Your OTP Code is {otp}", using='smtp')
        return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)
    
    
class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        data = request.data
        
        serializer = LoginSerializer(data=data)
        
        if not serializer.is_valid():
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            
            if not user.is_verified:
                send_otp_email(user)
                return Response({"errors": "User not verified"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Create a singned token for the user
            token = RefreshToken.for_user(user)
            access_token = str(token.access_token)
            refresh_token = str(token)
            return Response({"access": access_token, "refresh": refresh_token}, status=status.HTTP_200_OK)
        else:
            return Response({"errors": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        
        
class UserViewset(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        user = request.user
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def all_users(self, request):
        users = CustomUser.objects.all()
        paginator = self.paginator
        paginated_users = paginator.paginate_queryset(users, request)
        serializer = UserSerializer(paginated_users, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def make_admin(self, request, pk=None):
        try:
            user = CustomUser.objects.get(pk=pk)
            user.is_staff = True
            user.save()
            return Response({"message": "User made admin successfully"}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"errors": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"errors": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    


    
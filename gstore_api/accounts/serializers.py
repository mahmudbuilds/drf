from rest_framework import serializers
from .models import CustomUser

def send_otp_email(user):
    otp = user.generate_otp()
    user.email_user("OTP Verification", f"Your OTP Code is {otp}", using="smtp")

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)
    otp_secret = serializers.CharField(read_only=True)
    def validate(self, data):
        
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        
        if CustomUser.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Email already exists")
        return data

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'password', 'first_name', 'last_name', 'confirm_password', 'otp_secret']
        
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = CustomUser.objects.create_user(**validated_data)
        
        # email otp
        send_otp_email(user)
        
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
class GetOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'is_verified', 'is_active', 'phone_number', 'created_at']
        read_only_fields = ['id', 'email', 'is_active', 'is_verified', 'created_at']
        
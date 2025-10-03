from rest_framework import serializers
from userApp.models import UserProfile
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model - excludes sensitive fields"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'date_joined', 'is_active']
        read_only_fields = ['id', 'date_joined', 'is_active']

class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""
    user = UserSerializer(read_only=True)
    favorite_cuisines_list = serializers.SerializerMethodField()
    profile_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'bio', 'favorite_cuisines', 'favorite_cuisines_list',
            'profile_image', 'profile_image_url', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_favorite_cuisines_list(self, obj):
        """Return favorite cuisines as a list"""
        return obj.get_favorite_cuisines_list()
    
    def get_profile_image_url(self, obj):
        """Return the full URL for the profile image"""
        if obj.profile_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_image.url)
        return None

class UserProfileCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating UserProfile"""
    favorite_cuisines_list = serializers.ListField(
        child=serializers.ChoiceField(choices=UserProfile.CUISINE_CHOICES),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = UserProfile
        fields = [
            'bio', 'favorite_cuisines', 'favorite_cuisines_list', 'profile_image'
        ]
    
    def create(self, validated_data):
        favorite_cuisines_list = validated_data.pop('favorite_cuisines_list', [])
        profile = UserProfile.objects.create(**validated_data)
        if favorite_cuisines_list:
            profile.favorite_cuisines = ','.join(favorite_cuisines_list)
            profile.save()
        return profile
    
    def update(self, instance, validated_data):
        favorite_cuisines_list = validated_data.pop('favorite_cuisines_list', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if favorite_cuisines_list is not None:
            instance.favorite_cuisines = ','.join(favorite_cuisines_list)
        
        instance.save()
        return instance
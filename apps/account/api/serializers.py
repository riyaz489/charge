from rest_framework import serializers
from apps.account.models import Account, AccountSubscriber
from utils.manage_pass import generate_pass
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework_jwt.settings import api_settings

from apps.blog.api.serializers import BlogsThumbSerializer

JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER


from rest_framework_jwt.utils import jwt_decode_handler
from rest_framework_jwt.views import verify_jwt_token

class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)
    username = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        email = data.get("email", None)
        password = data.get("password", None)
        user = authenticate(email=email, password=password)
        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password is not found.'
            )
        try:
            payload = JWT_PAYLOAD_HANDLER(user)
            jwt_token = JWT_ENCODE_HANDLER(payload)
            update_last_login(None, user)
        except Account.DoesNotExist:
            raise serializers.ValidationError(
                'User with given email and password does not exists'
            )
        print(user.username)
        return {
            'email': user.email,
            'username': user.username,
            'token': jwt_token
        }


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['email', 'username', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        account = Account(
            email=validated_data['email'],
            username=validated_data['username']
        )
        password = validated_data['password']
        account.set_password(password)
        account.save()
        payload = JWT_PAYLOAD_HANDLER(account)
        jwt_token = JWT_ENCODE_HANDLER(payload)
        return account, jwt_token


class UserProfleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['email', 'username', 'date_joined', 'image', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        instance.image = validated_data.get('image', instance.image)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        instance.save()
        return instance


class BlogsListSerilizer(serializers.ModelSerializer):
    blogs_data = BlogsThumbSerializer(many=True, source='blog_set')
    user_id = serializers.CharField(min_length=3, max_length=50, source='id')
    following = serializers.IntegerField(source='subscribers.count')
    followers = serializers.SerializerMethodField()
    number_of_posts = serializers.IntegerField(source='blog_set.count')

    class Meta:
        model = Account
        fields = ["user_id", "username", "email", "blogs_data", "image", "following", "followers", "number_of_posts"]

    def get_followers(self, obj):
        return AccountSubscriber.objects.filter(following_account=obj.id).count()

    # or using methodField
    # def get_blogs_data(self, obj):
    #     followers_queryset =  # get queryset of followers
    #     return BlogsThumbSerializer(followers_queryset, many=True).data


class ResetPasswordSerilizer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    id = serializers.IntegerField(read_only=True)
    password = serializers.CharField(max_length=200, read_only=True)
    username = serializers.CharField(max_length=255, read_only=True)


    def validate(self, data):
        email = data.get("email", None)

        if not Account.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'A user with this email not found.'
            )
        try:
            user = Account.objects.get(email=email)
            new_pass = generate_pass()
            # setting new random password
            user.set_password(new_pass)
            user.save()

        except Account.DoesNotExist:
            raise serializers.ValidationError(
                'User with given email does not exists'
            )
        print(user.username)
        return {
            'email': user.email,
            'password': new_pass,
            'id': user.id,
            'username': user.username
        }
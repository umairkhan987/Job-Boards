import jwt
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from accounts.forms import country_names
from accounts.models import User, Profile
from jobBoard import settings


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['is_Freelancer'] = user.is_Freelancer
        token['is_Employer'] = user.is_Employer
        return token


class UserSerializer(serializers.ModelSerializer):
    account_type = serializers.CharField(write_only=True)
    password = serializers.CharField(min_length=8, write_only=True)

    # token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "email", "password", "account_type")
        # extra_kwargs = {"password": {'write_only': True}}

    def validate_account_type(self, data):
        if data is None:
            raise serializers.ValidationError("account type must be required.")
        return data

    def create(self, validated_data):
        password = validated_data.pop("password")
        account_type = validated_data.pop('account_type')
        user = User(**validated_data)
        user.set_password(password)
        if account_type == "Freelancer":
            user.is_Freelancer = True
        elif account_type == "Employer":
            user.is_Employer = True
        user.save()
        return user

    def get_token(self, user):
        if user.is_authenticated:
            payload = {
                "id": user.id,
                "email": user.email,
                "is_Freelancer": user.is_Freelancer,
                "is_Employer": user.is_Employer,
            }
            jwt_token = jwt.encode(payload, settings.SECRET_KEY)
            return jwt_token
            # return simple user token without jwt
            # tokens = RefreshToken.for_user(user)
            # token = text_type(tokens.access_token)
            # return token


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True, required=True, min_length=8)
    new_password1 = serializers.CharField(write_only=True, required=True, min_length=8)
    new_password2 = serializers.CharField(write_only=True, required=True, min_length=8)

    class Meta:
        model = User
        fields = ("old_password", "new_password1", "new_password2")

    def validate(self, attrs):
        if attrs['new_password1'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password1": "Password fields didn't match."})
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError({"old_password": "Old password is not correct"})
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password1'])
        instance.save()
        return instance

    @property
    def data(self):
        return {
            "detail": "Password updated successfully"
        }


class UpdateAccountSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'profileImg')

    def update(self, instance, validated_data):
        instance.first_name = validated_data['first_name']
        instance.last_name = validated_data['last_name']
        profile_image = validated_data.get("profileImg", None)
        if profile_image:
            if instance.profileImg:
                instance.profileImg.delete()
            instance.profileImg = profile_image
        instance.save()
        return instance


class UpdateProfileSerializer(serializers.ModelSerializer):
    rate = serializers.IntegerField(required=True, min_value=5, max_value=200)
    country = serializers.ChoiceField(choices=country_names, required=True)
    tags = serializers.CharField(required=True, max_length=255)
    introduction = serializers.CharField(required=True, max_length=2000, min_length=10)
    skills = serializers.ListField()

    class Meta:
        model = Profile
        fields = ("rate", "skills", "tags", "country", "introduction", "userCV")

    def update(self, instance, validated_data):
        instance.rate = validated_data['rate']
        instance.skills = validated_data['skills']
        instance.country = validated_data['country']
        instance.tags = validated_data['tags']
        instance.introduction = validated_data['introduction']
        user_cv = validated_data.get("userCV", None)
        if user_cv:
            if instance.userCV or user_cv == "null":
                instance.userCV.delete()
            instance.userCV = user_cv
        instance.save()
        return instance
from rest_framework import serializers

from .models import CustomUser, Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ["id", "email", "phone_number", "avatar", "country", "payments"]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser(
            email=validated_data["email"],
            phone_number=validated_data.get("phone_number", ""),
            country=validated_data.get("country", ""),
        )
        user.set_password(validated_data["password"])
        user.save()
        return user

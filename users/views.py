from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.generics import ListAPIView

from .models import CustomUser, Payment
from .serializers import UserSerializer, PaymentSerializer


class CustomUserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()


class PaymentListAPIView(ListAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ("course_purchased", "lesson_purchased", "payment_method")
    ordering_fields = ["purchased_at"]
    ordering = ["-purchased_at"]

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, filters, status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from materials.models import Course
from users.permissions import IsOwner, IsModerator
from users.services import create_stripe_checkout_session, create_stripe_price, create_stripe_product
from .models import CustomUser, Payment
from .serializers import UserSerializer, PaymentSerializer


class CustomUserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()

    def get_permissions(self):
        if self.action in ["create"]:
            self.permission_classes = [AllowAny]
        elif self.action in ["update", "partial_update"]:
            self.permission_classes = [IsAuthenticated, IsOwner]
        elif self.action in ["list", "retrieve"]:
            self.permission_classes = [IsAuthenticated, IsModerator]
        else:
            self.permission_classes = [IsAuthenticated, IsOwner | IsModerator]

        return [permission() for permission in self.permission_classes]


class PaymentListAPIView(ListAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ("course_purchased", "lesson_purchased", "payment_method")
    ordering_fields = ["purchased_at"]
    ordering = ["-purchased_at"]


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["course", "lesson", "payment_method"]
    ordering_fields = ["payment_date"]
    ordering = ["-payment_date"]

    @swagger_auto_schema(
        operation_description="Получить список платежей",
        manual_parameters=[
            openapi.Parameter("course", openapi.IN_QUERY, description="ID курса", type=openapi.TYPE_INTEGER, ),
            openapi.Parameter("lesson", openapi.IN_QUERY, description="ID урока", type=openapi.TYPE_INTEGER, ),
            openapi.Parameter("payment_method", openapi.IN_QUERY, description="Метод оплаты ('cash', 'card')",
                              type=openapi.TYPE_STRING, ),
            openapi.Parameter("ordering", openapi.IN_QUERY,
                              description="Сортировка по дате ('payment_date' или '-payment_date')",
                              type=openapi.TYPE_STRING, ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Создать запись о платеже")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Получить платеж по ID")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Обновить запись о платеже")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Частично обновить запись о платеже")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Удалить запись о платеже")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class CreateStripePaymentAPIView(APIView):

    def post(self, request, *args, **kwargs):
        course_id = request.data.get("course_id")
        course = get_object_or_404(Course, id=course_id)

        product_id = create_stripe_product(course.title)
        price_id = create_stripe_price(product_id, course.price)
        success_url = "http://127.0.0.1:8000/success/"
        cancel_url = "http://127.0.0.1:8000/cancel/"
        payment_url = create_stripe_checkout_session(price_id, success_url, cancel_url)

        payment = Payment.objects.create(user=request.user, course=course, amount=course.price, payment_method="card",
                                         payment_url=payment_url, )

        return Response({"payment_url": payment_url, "payment_id": payment.id}, status=status.HTTP_201_CREATED)

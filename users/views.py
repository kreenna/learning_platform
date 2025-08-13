from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from users.permissions import IsOwner, IsModerator, IsCreator
from rest_framework.permissions import IsAuthenticated


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

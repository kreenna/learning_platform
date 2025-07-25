from django.urls import path
from rest_framework.routers import SimpleRouter

from users.apps import UsersConfig
from users.views import CustomUserViewSet, PaymentListAPIView

app_name = UsersConfig.name

router = SimpleRouter()
router.register("", CustomUserViewSet)

urlpatterns = [
    path("payments/", PaymentListAPIView.as_view(), name="payments")
]

urlpatterns += router.urls

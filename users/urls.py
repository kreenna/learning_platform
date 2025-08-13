from django.urls import path
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.apps import UsersConfig
from users.views import CustomUserViewSet, PaymentListAPIView

app_name = UsersConfig.name

router = SimpleRouter()
router.register("", CustomUserViewSet)

urlpatterns = [
    path("payments/", PaymentListAPIView.as_view(), name="payments"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

urlpatterns += router.urls

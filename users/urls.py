from rest_framework.routers import SimpleRouter

from users.views import CustomUserViewSet
from users.apps import UsersConfig

app_name = UsersConfig.name

router = SimpleRouter()
router.register("", CustomUserViewSet)

urlpatterns = []

urlpatterns += router.urls
from django.urls import path
from rest_framework.routers import SimpleRouter

from materials.apps import MaterialsConfig
from materials.views import CourseViewSet, LessonsCreateAPIView, LessonListAPIView, LessonRetrieveAPIView, \
    LessonsUpdateAPIView, LessonDestroyAPIView

app_name = MaterialsConfig.name

router = SimpleRouter()
router.register("", CourseViewSet)

urlpatterns = [
    path("lessons/", LessonListAPIView.as_view(), name="lessons"),
    path("lessons/<int:pk>/", LessonRetrieveAPIView.as_view(), name="lesson"),
    path("lessons/create/", LessonsCreateAPIView.as_view(), name="lesson_create"),
    path("lessons/<int:pk>/update/", LessonsUpdateAPIView.as_view(), name="lesson_update"),
    path("lessons/<int:pk>/delete/", LessonDestroyAPIView.as_view(), name="lesson_delete"),
]

urlpatterns += router.urls

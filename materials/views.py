from django.shortcuts import get_object_or_404
from django.utils.timezone import now, timedelta
from rest_framework import viewsets
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView, \
    GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from materials.services import send_course_update_email
from users.permissions import IsCreator, IsModerator
from .models import Course, Lesson, Subscription
from .paginators import MaterialsPagination
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    pagination_class = MaterialsPagination
    queryset = Course.objects.all()

    def get_queryset(self):
        user = self.request.user
        # если пользователь - модератор, видит все курсы
        if user.groups.filter(name="managers").exists():
            return Course.objects.all()
        # если не модератор - видит только свои курсы (созданные самим пользователем)
        return Course.objects.filter(creator=user)

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def perform_update(self, serializer):
        instance = serializer.save()

        # получаем текущую дату и время
        time_threshold = now() - timedelta(hours=4)

        # проверяем, обновлялся ли курс более 4 часов назад
        if instance.updated_at < time_threshold:
            # получаем всех подписчиков курса
            subscribers = instance.subscriptions.all().select_related("owner")
            for subs in subscribers:
                send_course_update_email.delay(subs.owner.email, instance.title)

    def get_permissions(self):
        if self.action in ["list", "retrieve", "update", "partial_update"]:
            self.permission_classes = [IsAuthenticated, IsModerator | IsCreator]
        elif self.action in ["create"]:
            # запрещаем модераторам создавать
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action in ["destroy"]:
            self.permission_classes = [IsAuthenticated, IsCreator]
        else:
            self.permission_classes = [IsAuthenticated]

        return [permission() for permission in self.permission_classes]


class LessonsCreateAPIView(CreateAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()

    def get_permissions(self):
        permission_classes = [IsAuthenticated, ~IsModerator]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class LessonListAPIView(ListAPIView):
    serializer_class = LessonSerializer
    pagination_class = MaterialsPagination

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="managers").exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(creator=user)


class LessonRetrieveAPIView(RetrieveAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()

    def get_permissions(self):
        permission_classes = [IsAuthenticated, IsModerator | IsCreator]
        return [permission() for permission in permission_classes]


class LessonsUpdateAPIView(UpdateAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()


class LessonDestroyAPIView(DestroyAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()

    def get_permissions(self):
        permission_classes = [IsAuthenticated, IsCreator]
        return [permission() for permission in permission_classes]


class SubscriptionAPIView(GenericAPIView):
    def post(self, *args, **kwargs):
        user = self.request.user
        course_id = kwargs.get("course_id")
        course_item = get_object_or_404(Course, id=course_id)
        subs_item = Subscription.objects.filter(owner=user, course=course_item)

        # если подписка у пользователя на этот курс есть - удаляем ее
        if subs_item.exists():
            subs_item.delete()
            message = "подписка удалена"
        # если подписки у пользователя на этот курс нет - создаем ее
        else:
            subs_item.create(owner=user, course=course_item)
            message = "подписка добавлена"
        # возвращаем ответ в API
        return Response({"message": message})

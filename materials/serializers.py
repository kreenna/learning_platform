from rest_framework import serializers

from .models import Course, Lesson, Subscription
from .validators import validate_youtube_link


class LessonSerializer(serializers.ModelSerializer):
    video = serializers.URLField(validators=[validate_youtube_link])

    class Meta:
        model = Lesson
        fields = ["id", "title", "description", "preview", "video", "course"]


class CourseSerializer(serializers.ModelSerializer):
    lessons_amount = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    @staticmethod
    def get_lessons_amount(obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        user = self.context["request"].user
        if user.is_anonymous:
            return False

        return Subscription.objects.filter(owner=user, course=obj).exists()

    class Meta:
        model = Course
        fields = ["id", "title", "description", "preview", "lessons_amount", "lessons", "is_subscribed"]

    class SubscriptionSerializer(serializers.ModelSerializer):
        class Meta:
            model = Subscription
            fields = ["id", "owner", "course"]

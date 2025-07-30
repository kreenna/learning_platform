from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from materials.models import Course, Lesson
from users.models import Payment

User = get_user_model()


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            user = User.objects.first()
            if not user:
                self.stdout.write(self.style.ERROR("No users found in DB. Please create a user first."))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error fetching user: {e}"))
            return

        course = Course.objects.first()
        if not course:
            self.stdout.write(self.style.ERROR("No courses found in DB. Please create a course first."))
            return

        lesson = Lesson.objects.first()
        if not lesson:
            self.stdout.write(self.style.WARNING("No lessons found. Payments can be created only for courses."))

        payment1 = Payment.objects.create(
            user=user,
            course_purchased=course,
            lesson_purchased=None,
            payment_sum=Decimal("1500.00"),
            payment_method="Наличные"
        )
        self.stdout.write(self.style.SUCCESS(f"Created payment #{payment1.pk} for course '{course}'"))

        if lesson:
            payment2 = Payment.objects.create(
                user=user,
                course_purchased=None,
                lesson_purchased=lesson,
                payment_sum=Decimal("500.00"),
                payment_method="Перевод на карту"
            )
            self.stdout.write(self.style.SUCCESS(f"Created payment #{payment2.pk} for lesson '{lesson}'"))

        self.stdout.write(self.style.SUCCESS("Sample payments created successfully."))

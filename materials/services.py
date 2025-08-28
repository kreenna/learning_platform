from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_course_update_email(user_email, course_title):
    send_mail(
        subject=f"Обновления в курсе {course_title}",
        message=f"В курсе {course_title} произошли обновления. Посетите сайт, чтобы узнать подробности.",
        from_email="qwarekree@yandex.ru",
        recipient_list=[user_email],
        fail_silently=False,
    )

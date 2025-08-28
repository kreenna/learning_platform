from celery import shared_task
from django.utils.timezone import now, timedelta

from users.models import CustomUser


@shared_task
def deactivate_inactive_users():
    threshold_date = now() - timedelta(days=30)
    inactive_users = CustomUser.objects.filter(is_active=True, last_login__lt=threshold_date)
    count = inactive_users.update(is_active=False)
    return f"{count} users deactivated"

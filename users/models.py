from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from materials.models import Course, Lesson


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(verbose_name="Телефон")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True, verbose_name="Аватар")
    country = models.CharField(max_length=200, verbose_name="Страна")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Payment(models.Model):
    PAYMENT_CHOICES = [("Наличные", "Наличные"), ("Перевод на счет", "Перевод на счет")]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="payments",
                             verbose_name="Пользователь")
    purchased_at = models.DateTimeField(auto_now_add=True)

    course_purchased = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="purchases",
                                         verbose_name="Приобретенный курс", null=True, blank=True)
    lesson_purchased = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="purchases",
                                         verbose_name="Приобретенный урок", null=True, blank=True)
    payment_sum = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма оплаты")
    payment_method = models.CharField(choices=PAYMENT_CHOICES, verbose_name="Способ оплаты")
    link = models.URLField(max_length=500, null=True, blank=True, verbose_name="Ссылка на оплату")

    def __str__(self):
        return f"Платеж #{self.id} от {self.user} - {self.payment_sum} руб."

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"

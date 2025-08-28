from django.db import models

from users.models import CustomUser


class Course(models.Model):
    title = models.CharField(max_length=250, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    preview = models.ImageField(upload_to="previews/courses/", blank=True, null=True, verbose_name="Картинка")
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="courses", verbose_name="Создатель")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Цена курса")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Lesson(models.Model):
    title = models.CharField(max_length=250, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    preview = models.ImageField(upload_to="previews/lessons/", blank=True, null=True, verbose_name="Картинка")
    video = models.URLField(verbose_name="Ссылка на видео-урок")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons", verbose_name="Курс")
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="lessons", verbose_name="Создатель")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"


class Subscription(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="subscriptions",
                              verbose_name="Владелец")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="subscriptions", verbose_name="Курс")

    class Meta:
        unique_together = ("owner", "course")
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return f"{self.owner.email} подписан на {self.course.title}"

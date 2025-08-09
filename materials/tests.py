from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from users.models import CustomUser
from .models import Course, Lesson, Subscription


class BaseTestMixin:
    def setUp(self):
        # создаем группы
        self.moderators_group, _ = Group.objects.get_or_create(name="moderators")
        self.managers_group, _ = Group.objects.get_or_create(name="managers")

        # создаем пользователей
        self.manager = CustomUser.objects.create(email="manager@example.com", password="managerpass")
        self.manager.groups.add(self.managers_group)

        self.regular_user = CustomUser.objects.create(email="user@example.com", password="userpass")
        self.non_owner_user = CustomUser.objects.create(email="non_owner@example.com", password="userpass")

        # аутентификация клиентов
        self.client_mod = APIClient()
        self.client_mod.force_authenticate(user=self.manager)

        self.client_user = APIClient()
        self.client_user.force_authenticate(user=self.regular_user)

        self.non_owner = APIClient()
        self.non_owner.force_authenticate(user=self.non_owner_user)

        # создаем курсы и уроки
        self.course_user = Course.objects.create(title="User's Course", description="Desc", creator=self.regular_user)
        self.course_mod = Course.objects.create(title="Mod's Course", description="Desc", creator=self.manager)

        self.lesson_user = Lesson.objects.create(
            title="User's Lesson", description="Desc", video="https://www.youtube.com/watch?v=I968MFnHZyA",
            course=self.course_user, creator=self.regular_user
        )


class CourseViewSetTests(BaseTestMixin, APITestCase):

    def test_course_list_access_moderator(self):
        url = reverse("materials:course-list")
        response = self.client_mod.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # модератор видит все курсы
        course_ids = [c["id"] for c in response.data["results"]]
        self.assertIn(self.course_user.id, course_ids)
        self.assertIn(self.course_mod.id, course_ids)

    def test_course_list_access_regular_user(self):
        url = reverse("materials:course-list")
        response = self.client_user.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        course_ids = [c["id"] for c in response.data["results"]]
        self.assertIn(self.course_user.id, course_ids)
        self.assertNotIn(self.course_mod.id, course_ids)

    def test_course_create_regular_user(self):
        url = reverse("materials:course-list")
        data = {"title": "New Course", "description": "Desc"}
        response = self.client_user.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "New Course")
        self.assertEqual(Course.objects.get(id=response.data["id"]).creator, self.regular_user)

    def test_course_create_forbidden_moderator(self):
        url = reverse("materials:course-list")
        data = {"title": "Mod Course", "description": "Desc"}
        response = self.client_mod.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_course_update_by_owner(self):
        url = reverse("materials:course-detail", kwargs={"pk": self.course_user.id})
        data = {"title": "Updated Course", "description": "Updated Desc"}
        response = self.client_user.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Course")

    def test_course_update_forbidden_for_non_owner(self):
        url = reverse("materials:course-detail", kwargs={"pk": self.course_user.id})
        data = {"title": "Bad Update", "description": "Bad"}
        response = self.non_owner.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_course_delete_by_owner(self):
        url = reverse("materials:course-detail", kwargs={"pk": self.course_user.id})
        response = self.client_user.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_course_delete_forbidden_for_moderator(self):
        url = reverse("materials:course-detail", kwargs={"pk": self.course_user.id})
        response = self.client_mod.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class LessonAPITests(BaseTestMixin, APITestCase):

    def test_lesson_list_managers(self):
        url = reverse("materials:lessons")
        response = self.client_mod.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        lesson_ids = [l["id"] for l in response.data["results"]]
        self.assertIn(self.lesson_user.id, lesson_ids)

    def test_lesson_list_regular_user(self):
        url = reverse("materials:lessons")
        response = self.client_user.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        lesson_ids = [l["id"] for l in response.data["results"]]
        self.assertIn(self.lesson_user.id, lesson_ids)

    def test_lesson_create_regular_user(self):
        url = reverse("materials:lesson_create")
        data = {
            "title": "New Lesson",
            "description": "Desc",
            "video": "https://www.youtube.com/watch?v=I968MFnHZyA",
            "course": self.course_user.id,
        }
        response = self.client_user.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "New Lesson")
        self.assertEqual(Lesson.objects.get(id=response.data["id"]).creator, self.regular_user)

    def test_lesson_create_forbidden_manager(self):
        url = reverse("materials:lesson_create")
        data = {
            "title": "Manager's Lesson",
            "description": "Desc",
            "video": "https://www.youtube.com/watch?v=I968MFnHZyA",
            "course": self.course_mod.id
        }
        response = self.client_mod.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_update_owner(self):
        url = reverse("materials:lesson_update", kwargs={"pk": self.lesson_user.id})
        data = {
            "title": "Lesson Updated",
            "description": "Updated Desc",
            "video": self.lesson_user.video,
            "course": self.course_user.id
        }
        response = self.client_user.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Lesson Updated")

    def test_lesson_update_bad_link(self):
        url = reverse("materials:lesson_update", kwargs={"pk": self.lesson_user.id})
        data = {"title": "Hacked", "description": "Bad", "video": "https://bad",
                "course": self.course_user.id}
        response = self.client_mod.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_lesson_delete_owner(self):
        url = reverse("materials:lesson_delete", kwargs={"pk": self.lesson_user.id})
        response = self.client_user.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_lesson_delete_forbidden_moderator(self):
        url = reverse("materials:lesson_delete", kwargs={"pk": self.lesson_user.id})
        response = self.client_mod.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SubscriptionAPIViewTests(BaseTestMixin, APITestCase):

    def test_subscribe_and_unsubscribe(self):
        url = reverse("materials:subscribe", kwargs={"course_id": self.course_user.id})

        # подписка
        response = self.client_user.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "подписка добавлена")
        self.assertTrue(
            Subscription.objects.filter(owner=self.regular_user, course=self.course_user).exists()
        )

        # отписка
        response = self.client_user.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "подписка удалена")
        self.assertFalse(
            Subscription.objects.filter(owner=self.regular_user, course=self.course_user).exists()
        )

    def test_subscribe_requires_authentication(self):
        client = APIClient()  # анонимный
        url = reverse("materials:subscribe", kwargs={"course_id": self.course_user.id})
        response = client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

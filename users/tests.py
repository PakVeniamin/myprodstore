from django.test import TestCase
from django.urls import reverse, reverse_lazy
from http import HTTPStatus
from datetime import timedelta
from django.utils.timezone import now

from users.models import User, EmailVerification
from users.forms import UserRegistrationForm


# Create your tests here.
class UserRegistrationViewTestCase(TestCase):

    def setUp(self):
        self.path = reverse('users:registration')
        self.data = {
            'first_name': 'Veniamin', 'last_name': 'Pak',
            'username': 'pakman', 'email': 'veniaminpak.nsu@mail.ru',
            'password1': 'QWErty123456', 'password2': 'QWErty123456'
        }

    def test_user_registration_get(self):
        response = self.client.get(self.path)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context_data['title'], 'Store - Регистрация')
        self.assertTemplateUsed(response, 'users/register.html')

    def test_user_registration_post_success(self):
        username = self.data['username']
        self.assertFalse(User.objects.filter(username=username).exists())
        response = self.client.post(self.path, self.data)

        # чекним создание юзера
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse('users:login'))
        self.assertTrue(User.objects.filter(username=username).exists())

        # чекним верификацию емаила
        email_verification = EmailVerification.objects.filter(user__username=username)
        self.assertTrue(email_verification.exists())
        self.assertEqual(
            email_verification.first().expiration.date(),
            (now() + timedelta(hours=24)).date()
        )

    def test_user_registration_post_error(self):
        username = self.data['username']
        user = User.objects.create(username=username)
        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'Пользователь с таким именем уже существует.', html=True)

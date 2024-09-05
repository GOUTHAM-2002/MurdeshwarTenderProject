from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .models import Tender, Project
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.core import mail
from .models import Tender, Project
from .forms import TenderForm, ProjectForm, CustomUserCreationForm
from PIL import Image
from io import BytesIO
import tempfile

from .tokens import account_activation_token

#test for views
class UserViewsTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )
        self.superuser = get_user_model().objects.create_superuser(
            username='adminuser',
            email='admin@example.com',
            password='adminpassword'
        )
        self.client.login(username='testuser', password='testpassword')

    def test_login_view(self):
        response = self.client.post(reverse('login'), {
            'username_or_email': 'testuser',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertRedirects(response, reverse('home'))

    def test_register_view(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpassword',
            'password2': 'newpassword'
        })
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertEqual(get_user_model().objects.count(), 3)  # 2 users + 1 new

    def test_create_tender_view(self):
        # Prepare image files
        image = Image.new('RGB', (100, 100))
        image_io = BytesIO()
        image.save(image_io, format='PNG')
        image_io.seek(0)
        image_file = SimpleUploadedFile('image.png', image_io.read(), content_type='image/png')

        # Post request with tender form data
        response = self.client.post(reverse('create_tender'), {
            'title': 'Test Tender',
            'description': 'Test Description',
            'amount_quoted': '123.45',
            'png1': image_file,
            'png2': image_file,
            'png3': image_file
        })

        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertTrue(Tender.objects.filter(title='Test Tender').exists())

    def test_update_tender_view(self):
        # Create a Tender instance
        tender = Tender.objects.create(
            user=self.user,
            title='Old Title',
            description='Old Description',
            amount_quoted='100.00',
            png1=SimpleUploadedFile('old_image.png', b''),
            png2=SimpleUploadedFile('old_image.png', b''),
            png3=SimpleUploadedFile('old_image.png', b'')
        )

        # Prepare image files
        image = Image.new('RGB', (100, 100))
        image_io = BytesIO()
        image.save(image_io, format='PNG')
        image_io.seek(0)
        image_file = SimpleUploadedFile('new_image.png', image_io.read(), content_type='image/png')

        # Post request with updated tender form data
        response = self.client.post(reverse('update_tender', args=[tender.id]), {
            'title': 'Updated Title',
            'description': 'Updated Description',
            'amount_quoted': '150.00',
            'png1': image_file,
            'png2': image_file,
            'png3': image_file
        })

        self.assertEqual(response.status_code, 302)  # Should redirect
        tender.refresh_from_db()
        self.assertEqual(tender.title, 'Updated Title')

    def test_delete_tender_view(self):
        # Create a Tender instance
        tender = Tender.objects.create(
            user=self.user,
            title='Tender to Delete',
            description='This tender will be deleted.',
            amount_quoted='200.00',
            png1=SimpleUploadedFile('image.png', b''),
            png2=SimpleUploadedFile('image.png', b''),
            png3=SimpleUploadedFile('image.png', b'')
        )

        # Post request to delete the tender
        response = self.client.post(reverse('delete_tender', args=[tender.id]))
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertFalse(Tender.objects.filter(id=tender.id).exists())

    def test_project_create_view(self):
        response = self.client.post(reverse('project_create'), {
            'project_title': 'New Project',
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'min_quote': '1000.00',
            'rules_and_regulations': 'Some rules and regulations.',
            'documents': SimpleUploadedFile('document.pdf', b'')
        })
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertTrue(Project.objects.filter(project_title='New Project').exists())

    def test_project_update_view(self):
        project = Project.objects.create(
            project_title='Old Project',
            start_date='2024-01-01',
            end_date='2024-12-31',
            min_quote='500.00',
            rules_and_regulations='Old rules and regulations.',
            documents=SimpleUploadedFile('old_document.pdf', b'')
        )

        response = self.client.post(reverse('project_update'), {
            'project_title': 'Updated Project',
            'start_date': '2024-02-01',
            'end_date': '2024-12-31',
            'min_quote': '600.00',
            'rules_and_regulations': 'Updated rules and regulations.',
            'documents': SimpleUploadedFile('new_document.pdf', b'')
        })
        self.assertEqual(response.status_code, 302)  # Should redirect
        project.refresh_from_db()
        self.assertEqual(project.project_title, 'Updated Project')

    def test_project_delete_view(self):
        project = Project.objects.create(
            project_title='Project to Delete',
            start_date='2024-01-01',
            end_date='2024-12-31',
            min_quote='700.00',
            rules_and_regulations='This project will be deleted.',
            documents=SimpleUploadedFile('document.pdf', b'')
        )

        response = self.client.post(reverse('project_delete'))
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertFalse(Project.objects.filter(id=project.id).exists())

    def test_activate_view(self):
        # Simulate the activation process
        user = get_user_model().objects.create_user(
            username='inactiveuser',
            email='inactive@example.com',
            password='password',
            is_active=False
        )

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)

        response = self.client.get(reverse('activate', args=[uid, token]))
        self.assertEqual(response.status_code, 302)  # Should redirect
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_send_activation_email(self):
        user = get_user_model().objects.create_user(
            username='testuser2',
            email='testuser2@example.com',
            password='testpassword'
        )

        self.client.get(reverse('register'))
        self.assertEqual(len(mail.outbox), 1)  # Check if one email was sent
        email = mail.outbox[0]
        self.assertIn('Activate your user account', email.subject)
        self.assertIn(user.email, email.to[0])

# model based tests
class CustomUserModelTests(TestCase):

    def setUp(self):
        # Set up any test data here
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )

        self.superuser = get_user_model().objects.create_superuser(
            username='superuser',
            email='superuser@example.com',
            password='superpassword'
        )

    def test_create_user(self):
        user = get_user_model().objects.get(username='testuser')
        self.assertEqual(user.email, 'testuser@example.com')
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)

    def test_create_superuser(self):
        superuser = get_user_model().objects.get(username='superuser')
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)

    def test_user_str(self):
        self.assertEqual(str(self.user), 'testuser')


class TenderModelTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )
        self.tender = Tender.objects.create(
            user=self.user,
            title='Sample Tender',
            description='This is a sample tender description.',
            amount_quoted=1000.00,
            png1='path/to/image1.png',
            png2='path/to/image2.png',
            png3='path/to/image3.png',
            pdf='path/to/file.pdf'
        )

    def test_tender_str(self):
        self.assertEqual(str(self.tender), 'Sample Tender')

    def test_tender_fields(self):
        self.assertEqual(self.tender.title, 'Sample Tender')
        self.assertEqual(self.tender.amount_quoted, 1000.00)
        self.assertEqual(self.tender.description, 'This is a sample tender description.')


class ProjectModelTests(TestCase):

    def setUp(self):
        self.project = Project.objects.create(
            project_title='Sample Project',
            start_date='2024-01-01',
            end_date='2024-12-31',
            min_quote=5000.00,
            rules_and_regulations='Sample rules and regulations.',
            documents='path/to/document.pdf'  # Same as above for file paths
        )

    def test_project_str(self):
        self.assertEqual(str(self.project), 'Sample Project')

    def test_project_save(self):
        # Check if the save method properly replaces existing projects
        another_project = Project.objects.create(
            project_title='Another Project',
            start_date='2024-02-01',
            end_date='2024-11-30',
            min_quote=6000.00,
            rules_and_regulations='Different rules and regulations.',
            documents='path/to/another_document.pdf'
        )
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(Project.objects.first(), another_project)

    def test_project_fields(self):
        self.assertEqual(self.project.project_title, 'Sample Project')
        self.assertEqual(self.project.min_quote, 5000.00)
        self.assertEqual(self.project.rules_and_regulations, 'Sample rules and regulations.')

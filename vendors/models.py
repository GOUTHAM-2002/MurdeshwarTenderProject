from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class Tender(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tender')
    title = models.CharField(max_length=255)
    description = models.TextField()
    amount_quoted = models.DecimalField(max_digits=10, decimal_places=2)
    png1 = models.ImageField(upload_to='tenders/')
    png2 = models.ImageField(upload_to='tenders/')
    png3 = models.ImageField(upload_to='tenders/')
    pdf = models.FileField(upload_to='tenders/', blank=True, null=True)  # New field for PDF

    def __str__(self):
        return self.title
class Project(models.Model):
    project_title = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    min_quote = models.DecimalField(max_digits=10, decimal_places=2)
    rules_and_regulations = models.TextField()
    documents = models.FileField(upload_to='documents/')

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def save(self, *args, **kwargs):
        # If a project already exists, replace it
        if self.pk is None and Project.objects.exists():
            Project.objects.all().delete()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.project_title


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)




class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    agency = models.CharField(max_length=250)
    phone_no = models.CharField(max_length=15, blank=True, null=True)  # Updated to include phone number
    address = models.TextField()
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = CustomUserManager()

    def __str__(self):
        return self.username

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True
    )



from django import forms
from django.contrib.auth import authenticate

from .models import Project
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm as DefaultAuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class CustomUserCreationForm(UserCreationForm):
    usable_password = None
    # Include any additional fields here
    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'phone_no', 'password1', 'password2', 'agency', 'address', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize widget attributes here if needed
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class ProjectForm(forms.ModelForm):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Start Date'
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='End Date'
    )

    class Meta:
        model = Project
        fields = ['project_title', 'start_date', 'end_date','min_quote', 'rules_and_regulations', 'documents']

from django import forms
from .models import Tender


class TenderForm(forms.ModelForm):
    class Meta:
        model = Tender
        fields = ['title', 'description', 'amount_quoted', 'png1', 'png2', 'png3']

        class CustomAuthenticationForm(DefaultAuthenticationForm):
            def clean(self):
                username_or_email = self.cleaned_data.get('username_or_email')
                password = self.cleaned_data.get('password')

                if not username_or_email or not password:
                    raise ValidationError("Both username/email and password are required.")

                # Check if username_or_email is an email or username
                try:
                    if '@' in username_or_email:
                        user = User.objects.get(email=username_or_email)
                    else:
                        user = User.objects.get(username=username_or_email)
                except User.DoesNotExist:
                    raise ValidationError("Invalid username/email or password.")

                # Authenticate user
                user = authenticate(username=user.username, password=password)
                if user is None:
                    raise ValidationError("Invalid username/email or password.")

                return self.cleaned_data
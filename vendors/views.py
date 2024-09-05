from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .models import CustomUser, Tender
from .tokens import account_activation_token
from django.shortcuts import render, get_object_or_404, redirect
from .models import Project
from .forms import ProjectForm, TenderForm, CustomUserCreationForm
from .decorators import user_required
from .utils import  send_tender_email  # Import the utility function

from django.conf import settings
import os
import tempfile

from io import BytesIO
from PIL import Image
from fpdf import FPDF


def images_to_pdf(image_objects):
    """
    Converts a list of PIL Image objects into a single PDF.

    :param image_objects: List of PIL Image objects.
    :return: A file-like object containing the PDF data.
    """
    if len(image_objects) != 3:
        raise ValueError("Exactly 3 images are required.")

    pdf = FPDF()

    for img in image_objects:
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Save the image to a BytesIO object
        with BytesIO() as img_stream:
            img.save(img_stream, format='JPEG')
            img_stream.seek(0)

            # Add a page to the PDF and insert the image
            pdf.add_page()
            pdf.image(img_stream, x=0, y=0, w=210, h=297)  # Adjust size as needed

    # Create a BytesIO object to hold the PDF data
    pdf_output = BytesIO()
    pdf.output(pdf_output)

    # Return the BytesIO object containing the PDF data
    pdf_output.seek(0)
    return pdf_output

@login_required
def create_tender(request):
    if request.method == 'POST':
        form = TenderForm(request.POST, request.FILES)
        if form.is_valid():
            tender = form.save(commit=False)
            tender.user = request.user

            # Load images from the FileField
            images = [Image.open(tender.png1), Image.open(tender.png2), Image.open(tender.png3)]

            # Generate the PDF
            pdf_file = images_to_pdf(images)

            # Save the PDF to the model's PDF field
            tender.pdf.save('tender_images.pdf', pdf_file, save=False)

            # Save the tender instance
            tender.save()
            send_tender_email(request.user, tender, pdf_file)
            return redirect('home')
    else:
        form = TenderForm()

    return render(request, 'create_tender.html', {'form': form})
@login_required
def update_tender(request, tender_id):
    tender = get_object_or_404(Tender, id=tender_id, user=request.user)

    if request.method == 'POST':
        form = TenderForm(request.POST, request.FILES, instance=tender)
        if form.is_valid():
            updated_tender = form.save(commit=False)
            updated_tender.user = request.user

            # Handle the PDF creation if images are uploaded
            if updated_tender.png1 and updated_tender.png2 and updated_tender.png3:
                # Convert image fields to PIL Image objects
                image_objects = [
                    Image.open(updated_tender.png1) if updated_tender.png1 else None,
                    Image.open(updated_tender.png2) if updated_tender.png2 else None,
                    Image.open(updated_tender.png3) if updated_tender.png3 else None
                ]

                # Create PDF from the image objects
                pdf_file = images_to_pdf(image_objects)

                # Save the PDF to the Tender model
                updated_tender.pdf.save('tender_images.pdf', pdf_file)


            updated_tender.save()
            send_tender_email(request.user, updated_tender, pdf_file)
            return redirect('home')
    else:
        form = TenderForm(instance=tender)

    return render(request, 'update_tender.html', {'form': form})

def activate(request,uidb64,token):
    print("running activate")
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user,token):
        user.is_active=True
        user.save()
        messages.success(request,"Successfully registered")
        print("mewow")

        return redirect('login')
    else:
        print("bow")
        messages.error(request,"Activation link is invalid!")
        return redirect('login')
def activateEmail(request, user):
    mail_subject = "Activate you user account."
    message = render_to_string('template_account_activation.html',{
        'user' : user.username,
        'domain' : get_current_site(request).domain,
        'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
        'token' : account_activation_token.make_token(user),
        'protocol' : 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject,message,to=[user.email])
    if email.send():
        messages.success(request, f'Dear {user}, please check your email  to activate you account')
    else:
        messages.error(request,f'Problem sending email to you account. Make sure the entered details are correct!')



@login_required
def delete_tender(request, tender_id):
    tender = get_object_or_404(Tender, id=tender_id, user=request.user)
    if request.method == 'POST':
        tender.delete()
        return redirect('home')
    return render(request, 'delete_tender.html', {'tender': tender})


def home(request):
    if request.user.is_authenticated and request.user.username == 'gouthamn2024' and request.user.check_password(
            'murdeshwartender'):
        # If the user matches, redirect to the project_list view
        return redirect('project_list')
    project = Project.objects.first()
    if project:
        return render(request, 'home.html', {'project': project, 'user': request.user})
    return render(request, 'no_project.html', )


def index(request):
    return render(request, 'index.html')

@user_required
def project_list(request):
    project = Project.objects.first()  # Get the single instance of the project
    if not project:
        return redirect('project_create')

    if timezone.now().date() >= project.end_date:
        # Get all tenders if the condition is met
        tenders = Tender.objects.all()
    else:
        tenders = None
    return render(request, 'project_list.html', {'project': project,'tenders': tenders})


@user_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save()
            return redirect('project_list')
    else:
        form = ProjectForm()
    return render(request, 'project_form.html', {'form': form})


@user_required
def project_update(request):
    project = Project.objects.first()
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            return redirect('project_list')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'project_form.html', {'form': form})


@user_required
def project_delete(request, ):
    project = Project.objects.first()
    if request.method == 'POST':
        project.delete()
        return redirect('project_list')
    return render(request, 'project_confirm_delete.html', {'project': project})


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            activateEmail(request,user)
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


def login(request):
    print("Running login")
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email')
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(request, username=username_or_email, password=password)
        print("Attempted authentication")

        if user is None:
            # Check if username_or_email is an email
            if '@' in username_or_email:
                print("Detected email")
                user = authenticate(request, email=username_or_email, password=password)
                print("Attempted email-based authentication")

        if user is not None:
            print("User authenticated successfully")
            auth_login(request, user)
            if username_or_email == "gouthamn2024" and password == 'murdeshwartender':
                return redirect('project_list')
            return redirect('home')
        else:
            print("Authentication failed")
            form = AuthenticationForm(data=request.POST)
            form.add_error(None, "Invalid username/email or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})
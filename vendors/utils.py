from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

def send_tender_email(user, tender, pdf_file):
    """
    Sends an email with the tender details and the generated PDF to the user.

    :param user: The user to whom the email will be sent.
    :param tender: The tender instance with details.
    :param pdf_file: A file-like object containing the PDF data.
    """
    subject = 'Your Tender Details'
    message = render_to_string('emails/tender_details.html', {'tender': tender})

    email = EmailMessage(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email]
    )
    email.content_subtype = 'html'  # Specify that the content is HTML


    email.attach('tender_images.pdf', pdf_file.read(), 'application/pdf')
    email.send()
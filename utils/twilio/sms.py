
from django.conf import settings
from twilio.rest import Client
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Tracer.settings')
django.setup()



def send_sms_twilio(phone_number, code):
    client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)
    message = client.messages.create(
      from_=settings.TWILIO_NUMBER,
      body=code,
      to=phone_number
    )
    return message.sid






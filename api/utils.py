from django.core.mail import EmailMessage
import threading
# from google_auth_oauthlib.flow import Flow
from oauth2client import client
# import os
# import dotenv
import requests
import urllib
import jwt
from .models import CustomUser
from django.conf import settings

from django.db import transaction
import logging
# dotenv.load_dotenv()

class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()

class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(data['email_subject'], data['email_body'], to=[data['to_email']])
        EmailThread(email).start()

def get_id_token2(code):
    flow = client.OAuth2WebServerFlow(
        client_id=settings.GOOGLE_OAUTH2_CLIENT_ID,
        client_secret=settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        scope='https://www.googleapis.com/auth/userinfo.email',
        redirect_uri='http://localhost:8000/api/user/login/google/'
    )
    return flow.step1_get_authorize_url()

def get_id_token(code):
    try:
        credentials = client.credentials_from_clientsecrets_and_code(
            'client_secret.json',
            ['email', 'profile'],
            code,
            # redirect_uri='http://localhost:8000'
        )
        return credentials.id_token
    except client.Error as e:
        print(f"An error occurred: {e}")
        return None
    
def get_id_token_alt(code):
    token_url = 'https://oauth2.googleapis.com/token'
    client_id = settings.GOOGLE_OAUTH2_CLIENT_ID
    client_secret = settings.GOOGLE_OAUTH2_CLIENT_SECRET
    data = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'authorization_code',
        'redirect_uri': 'postmessage'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(token_url, data=data, headers=headers)
  
    if response.ok:
        id_token = response.json().get('id_token')
        return jwt.decode(id_token, options={'verify_signature': False})
    else:
        print(f"An error occurred: {response.status_code}")
        return None
    
# With the unnecessary urlencode
def get_id_token_alt2(code): 
    token_url = 'https://oauth2.googleapis.com/token'
    client_id = settings.GOOGLE_OAUTH2_CLIENT_ID
    client_secret = settings.GOOGLE_OAUTH2_CLIENT_SECRET
    data = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'authorization_code',
        'redirect_uri': 'postmessage'
    }
    body = urllib.parse.urlencode(data)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(token_url, data=body, headers=headers)
  
    if response.status_code == 200:
        id_token = response.json()['id_token']
        return jwt.decode(id_token, options={'verify_signature': False})
    else:
        print(f"An error occurred: {response.status_code}")
        return None



def authentication_or_create_user(user_email, first_name, last_name):
    try:
        user = CustomUser.objects.get(email=user_email)
    except CustomUser.DoesNotExist:
        user = CustomUser.objects.create_user(email=user_email, first_name=first_name, last_name=last_name, username=user_email)
        user.registration_method = 'google'
        user.save()
    return user



# Set up logging
logger = logging.getLogger(__name__)

def authentication_or_create_user2(user_email, first_name, last_name):
    try:
        # Try to retrieve the user by email
        user = CustomUser.objects.get(email=user_email)
        # Check if the registration method needs to be updated
        if user.registration_method != 'google':
            user.registration_method = 'google'
            user.save()
    except CustomUser.DoesNotExist:
        # If the user does not exist, create a new user with the provided details
        with transaction.atomic():
            user = CustomUser.objects.create_user(
                email=user_email,  # User's email
                first_name=first_name,  # User's first name
                last_name=last_name,  # User's last name
                username=user_email  # Use email as the username
            )
            user.registration_method = 'google'
            user.save()
            logger.info(f"Created new user: {user_email}")

    # Return the user object
    return user
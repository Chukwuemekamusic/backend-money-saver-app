from django.conf import settings
from django.shortcuts import redirect
from django.core.exceptions import ValidationError
from urllib.parse import urlencode
from typing import Dict, Any
import requests
from api.models import CustomUser

GOOGLE_ACCESS_TOKEN_OBTAIN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USER_INFO_URL = 'https://www.googleapis.com/oauth2/v1/userinfo'
GOOGLE_REVOKE_TOKEN_URL = 'https://oauth2.googleapis.com/revoke'
GOOGLE_REDIRECT_URI = f'{settings.BASE_API_URL}/api/user/login/google/callback'
LOGIN_URL = f'{settings.BASE_APP_URL}/internal/login'

# Exchange authorization code for access token
def google_get_access_token(code: str) -> Dict[str, Any]:
    data = {
        'code': code,
        'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
        'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        'redirect_uri': GOOGLE_REDIRECT_URI,
        'grant_type': 'authorization_code'
    }

    response = requests.post(GOOGLE_ACCESS_TOKEN_OBTAIN_URL, data=data)
    if not response.ok:
        raise ValidationError('Failed to obtain access token from Google.')
    access_token = response.json().get('access_token')
    return access_token


# Get user info from Google
def google_get_user_info(access_token: str) -> Dict[str, Any]:
    response = requests.get(GOOGLE_USER_INFO_URL, params={'access_token': access_token})
    if not response.ok:
        raise ValidationError('Failed to get user info from Google.')
    return response.json()

def get_user_data(validated_data):
    domain = settings.BASE_API_URL
    redirect_uri = f'{domain}/auth/api/login/google/'

    code = validated_data.get('code')
    error = validated_data.get('error')

    if error or not code:
        params = urlencode({'error': error})
        return redirect(f'{LOGIN_URL}?{params}')
    
    access_token = google_get_access_token(code=code, redirect_uri=redirect_uri)
    user_data = google_get_user_info(access_token=access_token)

    # Creates user in DB if first time login
    CustomUser.objects.get_or_create(
        username = user_data['email'],
        email = user_data['email'],
        first_name = user_data.get('given_name'), 
        last_name = user_data.get('family_name')
    )
    
    profile_data = {
        'email': user_data['email'],
        'first_name': user_data.get('given_name'),
        'last_name': user_data.get('family_name'),
    }
    return profile_data
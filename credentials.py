from auth.auth import Auth  # Import the Auth class
from utils import load_api_credentials  # Import the function from utils.py
import urllib.parse

def authenticate_and_get_token():
    # Load API credentials from JSON file
    credentials = load_api_credentials()
    api_key = credentials['api_key']
    api_secret = credentials['api_secret']
    redirect_uri = credentials['redirect_uri']

    auth_instance = Auth(api_key, api_secret, redirect_uri)  # Instantiate the Auth class

    # Generate authorization URL and get authorization code
    auth_code = auth_instance.get_authorization_code()

    # Get access token using authorization code
    access_token = auth_instance.get_access_token(auth_code)

    if not access_token:
        raise Exception("Authentication failed.")

    return api_key, api_secret, redirect_uri, access_token


def update_redirect_uri(api_credentials):
    """
    Update the api_credentials dictionary with an encoded redirect_uri.

    Parameters:
    - api_credentials: dict, the dictionary containing API credentials
    """
    redirect_uri = api_credentials.get('redirect_uri', '')
    encoded_redirect_uri = urllib.parse.quote(redirect_uri, safe='')
    api_credentials['redirect_uri'] = encoded_redirect_uri
    return api_credentials

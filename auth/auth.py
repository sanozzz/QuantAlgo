import requests
import json
import os
import urllib.parse
from flask import Flask, request, redirect, jsonify
import webbrowser
from utils import load_api_credentials  # Import the function

app = Flask(__name__)

class Auth:
    def __init__(self, api_key, api_secret, redirect_uri, token_file='token.json'):
        self.api_key = api_key
        self.api_secret = api_secret
        self.redirect_uri = redirect_uri
        self.token_file = token_file
        self.base_url = "https://api.upstox.com/v2"
        self.token_url = "https://api.upstox.com/v2/login/authorization/token"  # Correct endpoint for Upstox API v2
        self.access_token = self.load_token()

    def load_token(self):
        if os.path.exists(self.token_file):
            with open(self.token_file, 'r') as file:
                token_data = json.load(file)
                return token_data.get('access_token')
        return None

    def save_token(self, access_token):
        with open(self.token_file, 'w') as file:
            json.dump({'access_token': access_token}, file)

    def get_access_token(self, auth_code):
        payload = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.api_key,
            "client_secret": self.api_secret
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(self.token_url, data=payload, headers=headers)
        print(f"Access Token Request URL: {self.token_url}")
        print(f"Payload: {payload}")
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")
        if response.status_code == 200:
            access_token = response.json().get("access_token")
            self.save_token(access_token)
            return access_token
        else:
            print(f"Failed to get access token: {response.text}")
            return None

    def generate_login_url(self):
        encoded_redirect_uri = urllib.parse.quote(self.redirect_uri, safe='')
        print(f"Encoded redirect URI: {encoded_redirect_uri}")
        print(f"Client ID (API Key): {self.api_key}")
        return f'https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id={self.api_key}&redirect_uri={encoded_redirect_uri}'

    def get_authorization_code(self):
        authorization_url = self.generate_login_url()
        print("Visit this URL to authorize the application:", authorization_url)
        webbrowser.open(authorization_url)
        auth_code = input("Enter the authorization code from the URL: ")
        return auth_code

@app.route('/login')
def login():
    credentials = load_api_credentials()
    auth = Auth(credentials['api_key'], credentials['api_secret'], credentials['redirect_uri'])
    login_url = auth.generate_login_url()
    return redirect(login_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')
    if code:
        credentials = load_api_credentials()
        auth = Auth(credentials['api_key'], credentials['api_secret'], credentials['redirect_uri'])
        access_token = auth.get_access_token(code)
        return jsonify(access_token=access_token)
    else:
        return "Error: No code provided", 400

if __name__ == "__main__":
    app.run(debug=True)

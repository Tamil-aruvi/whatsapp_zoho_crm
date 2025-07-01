# zoho_auth.py

import os
import requests
import webbrowser
from dotenv import load_dotenv

load_dotenv()

# ZOHO_CLIENT_ID = 
# ZOHO_CLIENT_SECRET = 
# ZOHO_REFRESH_TOKEN = os.getenv("ZOHO_REFRESH_TOKEN")
# ZOHO_TOKEN_URL = "https://accounts.zoho.in/oauth/v2/token"



# ==== Replace with your actual values ====
CLIENT_ID = os.getenv("ZOHO_CLIENT_ID")
CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:5000/oauth/callback"  # This must match Zoho API Console
SCOPE = "ZohoCRM.modules.ALL"
REGION = "in"  # use 'in' for India, 'com' for US, etc.

# Step 1: Generate authorization URL
auth_url = (
    f"https://accounts.zoho.{REGION}/oauth/v2/auth?"
    f"scope={SCOPE}&"
    f"client_id={CLIENT_ID}&"
    f"response_type=code&"
    f"access_type=offline&"
    f"redirect_uri={REDIRECT_URI}"
)

print(f"\n🔗 Visit this URL in your browser to authorize:\n{auth_url}\n")
webbrowser.open(auth_url)

# Step 2: Paste the code from the URL you were redirected to
auth_code = input("📥 Paste the 'code' from the redirected URL: ").strip()

# Step 3: Exchange code for tokens
token_url = f"https://accounts.zoho.{REGION}/oauth/v2/token"
data = {
    "code": auth_code,
    "redirect_uri": REDIRECT_URI,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "grant_type": "authorization_code",
}

response = requests.post(token_url, data=data)

print("\n🔐 Token Response:", response.status_code)
print(response.json())
# zoho_leads.py
import requests
import os


# ✅ Replace with your real values or load from .env in production
ACCESS_TOKEN = os.getenv("ZOHO_ACCESS_TOKEN")
REFRESH_TOKEN = os.getenv("ZOHO_REFRESH_TOKEN")
CLIENT_ID = os.getenv("ZOHO_CLIENT_ID")
CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET")
API_DOMAIN = "https://www.zohoapis.in"  # For India users

def refresh_access_token():
    url = f"https://accounts.zoho.in/oauth/v2/token"
    params = {
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token"
    }

    r = requests.post(url, params=params)
    print("🔁 Refresh response:", r.status_code, r.text)  # Debug print

    try:
        data = r.json()
    except Exception as e:
        print("❌ Failed to parse JSON:", e)
        return None

    if r.status_code == 200 and "access_token" in data:
        new_token = data["access_token"]
        print("✅ Refreshed Access Token:", new_token)
        return new_token
    else:
        print("❌ Failed to refresh access token:", data.get("error", "Unknown Error"))
        return None

    url = f"https://accounts.zoho.in/oauth/v2/token"
    params = {
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token"
    }

    r = requests.post(url, params=params)
    print("🔁 Refresh response:", r.status_code, r.text)  # 🔍 Debugging aid

    if r.status_code == 200 and "access_token" in r.json():
        new_token = r.json()["access_token"]
        print("✅ Refreshed Access Token:", new_token)
        return new_token
    else:
        print("❌ Failed to refresh access token")
        return None

def get_headers():
    global ACCESS_TOKEN

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    # ⛔ Check if token is valid
    test = requests.get(f"{API_DOMAIN}/crm/v2/settings/modules", headers=headers)
    if test.status_code == 401:
        print("🔒 Access token expired, trying to refresh...")
        new_token = refresh_access_token()
        if new_token:
            ACCESS_TOKEN = new_token
            headers["Authorization"] = f"Bearer {ACCESS_TOKEN}"
        else:
            raise Exception("❌ Could not refresh access token")

    return headers

def search_lead_by_phone(phone_number):
    url = f"{API_DOMAIN}/crm/v2/Leads/search?phone={phone_number}"
    print(f"🔍 Searching lead with phone {phone_number}...")
    r = requests.get(url, headers=get_headers())

    if r.status_code == 200:
        data = r.json().get("data")
        return data[0] if data else None
    else:
        print("❌ Lead search error:", r.text)
        return None

def create_lead(name, email, phone):
    url = f"{API_DOMAIN}/crm/v2/Leads"
    payload = {
        "data": [
            {
                "Last_Name": name,
                "Email": email,
                "Phone": phone,
                "Lead_Source": "Chatbot"
            }
        ]
    }
    print(f"📤 Creating new lead for {name} ({email}, {phone})")
    r = requests.post(url, headers=get_headers(), json=payload)

    if r.status_code == 201:
        print("✅ Lead created!")
        return r.json()["data"][0]
    else:
        print("❌ Lead creation failed:", r.text)
        return None
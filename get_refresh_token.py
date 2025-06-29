import requests

data = {
    "grant_type": "authorization_code",
    "client_id": "1000.QEIYCMBCL0O4UPQW38BX6599A7VJRT",
    "client_secret": "4ccda46545150cb00ebb1b592e271870851883f6df",
    "redirect_uri": "http://localhost:8000/oauth/callback",
    "code": "1000.6d6d4f3b60589338355d00f8f9b5735d.4707b975adf0e4c6c82095108d17320c"
}

response = requests.post("https://accounts.zoho.in/oauth/v2/token", data=data)
print(response.json())

# test_zoho_leads.py

from zoho_leads import search_lead_by_phone, create_lead

test_phone = "number"  # Replace with your actual number
test_name = "name Test"
test_email = "name.test@example.com"

print(f"🔍 Searching lead with phone {test_phone}...")
lead = search_lead_by_phone(test_phone)

if lead:
    print("✅ Lead found:", lead["Full_Name"], "| ID:", lead["id"])
else:
    print("❌ Lead not found. Creating new one...")
    new_lead = create_lead(test_name, test_email, test_phone)
    if new_lead:
        print("✅ Lead created successfully:", new_lead)
    else:
        print("❌ Lead creation failed.")
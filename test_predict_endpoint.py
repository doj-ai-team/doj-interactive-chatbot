import requests
import uuid

session = requests.Session()
username = "tester_" + str(uuid.uuid4())[:8]

# Register user
print("Registering...")
res = session.post("http://127.0.0.1:5000/auth/register", data={
    "username": username,
    "email": f"{username}@test.com",
    "password": "password",
    "role": "Citizen"
})
print("Register Status:", res.status_code)

# Create a dummy txt file because creating a valid PDF manually is error-prone, but PyPDF2 needs a valid PDF.
# Let's just create a valid empty PDF string
pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Count 0\n/Kids []\n>>\nendobj\ntrailer\n<<\n/Root 1 0 R\n/Size 3\n>>\n%%EOF"
with open("test.pdf", "wb") as f:
    f.write(pdf_content)

print("Uploading...")
with open("test.pdf", "rb") as f:
    files = {"file": f}
    data = {"file_type": "pdf"}
    res = session.post("http://127.0.0.1:5000/predict", files=files, data=data)
    print("Upload Status:", res.status_code)
    try:
        print("Response JSON:", res.json())
    except Exception as e:
        print("Response Text:", res.text[:500])

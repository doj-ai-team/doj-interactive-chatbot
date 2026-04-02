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

# Create a dummy docx
from docx import Document
doc = Document()
doc.add_paragraph('Test case details for docx file.')
doc.save('test.docx')

print("Uploading DOCX...")
with open("test.docx", "rb") as f:
    files = {"file": f}
    data = {"file_type": "docx"}
    res = session.post("http://127.0.0.1:5000/predict", files=files, data=data)
    print("Upload Status:", res.status_code)
    try:
        print("Response JSON:", res.json())
    except Exception as e:
        print("Response Text:", res.text[:500])

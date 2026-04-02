import requests

session = requests.Session()

# Login
login_data = {'username': 'testadmin', 'password': 'password'}
res = session.post('http://localhost:5000/auth/login', data=login_data)
print("Login status:", res.status_code)

# Upload file
with open('dummy_case.txt', 'wb') as f:
    f.write(b'This is a test document.')

files = {'file': ('dummy_case.txt', open('dummy_case.txt', 'rb'))}
data = {'file_type': 'pdf'}  # Simulate pdf upload despite text file (extract_text_from_file handles pdf if valid, wait it will crash on a txt file pretending to be pdf)

res = session.post('http://localhost:5000/predict', files=files, data=data)
print("Predict status:", res.status_code)
try:
    print(res.json())
except Exception as e:
    print("Response text:", res.text)

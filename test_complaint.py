import requests

try:
    url = "http://127.0.0.1:5000/complaint"
    with open("test.txt", "rb") as f:
        files = {"file": f}
        data = {"file_type": "txt"}
        print(f"Sending Complaint POST to {url}...")
        response = requests.post(url, files=files, data=data, timeout=120)

    with open("test_output_complaint.txt", "w", encoding="utf-8") as out:
        out.write(f"Status Code: {response.status_code}\n")
        out.write(f"Response: {response.text}\n")
    print("Done writing to test_output_complaint.txt")
except Exception as e:
    print(f"Error: {e}")

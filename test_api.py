import requests

try:
    with open("test_img.jpg", "wb") as f:
        f.write(b"\x00" * 1024) # dummy 1kb image
        
    files = {"image": ("test_img.jpg", open("test_img.jpg", "rb"), "image/jpeg")}
    print("Sending request...")
    res = requests.post("http://localhost:8000/api/attendance/test-face", files=files)
    print("Status:", res.status_code)
    print("Response:", res.text)
except Exception as e:
    print("Error:", e)

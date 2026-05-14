import requests

BASE_URL = "http://localhost:8000"

def test_fake_jpg_attack():
    with open("fake.jpg", "w") as f:
        f.write("This is not a real JPEG image")
    
    with open("fake.jpg", "rb") as f:
        files = {"file": ("fake.jpg", f, "image/jpeg")}
        headers = {"X-User-Id": "alice"}
        response = requests.post(f"{BASE_URL}/files/upload", files=files, headers=headers)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    import os
    os.remove("fake.jpg")

if __name__ == "__main__":
    test_fake_jpg_attack()
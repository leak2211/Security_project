import pytest
import requests
from typing import Dict

BASE_URL = "http://localhost:8000"


USERS = {
    "alice": "alice",
    "bob": "bob",
    "admin": "admin"
}


FILES = {
    "file1": "file1", 
    "file2": "file2",  
    "file3": "file3", 
    "file4": "file4",  
    "file5": "file5"   
}

def make_request(method: str, endpoint: str, user_id: str, **kwargs):
   
    headers = {"X-User-Id": user_id}
    if "headers" in kwargs:
        headers.update(kwargs["headers"])
        del kwargs["headers"]
    
    url = f"{BASE_URL}{endpoint}"
    
    if method.upper() == "GET":
        return requests.get(url, headers=headers, **kwargs)
    elif method.upper() == "DELETE":
        return requests.delete(url, headers=headers, **kwargs)
    elif method.upper() == "POST":
        return requests.post(url, headers=headers, **kwargs)
    else:
        raise ValueError(f"Unsupported method: {method}")

class TestSecurity:
    
    def setup_method(self):
        try:
            response = requests.get(f"{BASE_URL}/")
            assert response.status_code == 200
        except requests.exceptions.ConnectionError:
            pytest.fail("Server is not running. Start with: uvicorn src.main:app --reload")
    
    def test_idor_read_alice_tries_bob_file(self):
        response = make_request("GET", "/files/file3", "alice") 
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ TEST 1 PASSED: Alice cannot read Bob's file (IDOR protection)")
    
    def test_alice_reads_own_file(self):
        response = make_request("GET", "/files/file1", "alice") 
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["owner_name"] == "alice"
        print("✓ TEST 2 PASSED: Alice can read her own file")
    
    def test_admin_reads_bob_file(self):
        response = make_request("GET", "/files/file3", "admin")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["owner_name"] == "bob"
        print("✓ TEST: Admin can read any file")
    
    def test_admin_deletes_bob_file(self):
        response = make_request("GET", "/files/file3", "admin")
        assert response.status_code == 200, "File should exist before deletion"
        
        response = make_request("DELETE", "/files/file3", "admin")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "deleted successfully" in data["msg"]
        
        response = make_request("GET", "/files/file3", "admin")
        assert response.status_code == 404, "File should be deleted"
        
        print("✓ TEST 3 PASSED: Admin can delete Bob's file")
    
    def test_alice_cannot_delete_bob_file(self):
        response = make_request("DELETE", "/files/file3", "alice")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ TEST: Alice cannot delete Bob's file")
    
    def test_alice_deletes_own_file(self):
        response = make_request("DELETE", "/files/file2", "alice")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ TEST: Alice can delete her own file")
    

    def test_alice_gets_my_files(self):
        response = make_request("GET", "/files/my", "alice")
        assert response.status_code == 200
        data = response.json()
        assert data["user"] == "alice"
        assert all(file["owner_name"] == "alice" for file in data["files"])
        print(f"✓ TEST: Alice has {data['count']} files")
    
    def test_bob_gets_my_files(self):
        response = make_request("GET", "/files/my", "bob")
        assert response.status_code == 200
        data = response.json()
        assert data["user"] == "bob"
        assert all(file["owner_name"] == "bob" for file in data["files"])
        print(f"✓ TEST: Bob has {data['count']} files")
    
    def test_admin_gets_all_files(self):
        response = make_request("GET", "/files/all", "admin")
        assert response.status_code == 200
        data = response.json()
        assert "files" in data
        print(f"✓ TEST: Admin sees all {data['count']} files")
    
    def test_alice_cannot_get_all_files(self):
        response = make_request("GET", "/files/all", "alice")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ TEST: Alice cannot access /files/all (admin only)")
    
    def test_file_not_found(self):
        response = make_request("GET", "/files/nonexistent", "alice")
        assert response.status_code == 404
        print("✓ TEST: Non-existent file returns 404")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔒 SECURITY TESTS FOR CORPORATE FILE MANAGER")
    print("="*60 + "\n")
    
    pytest.main([__file__, "-v", "-s", "--tb=short"])
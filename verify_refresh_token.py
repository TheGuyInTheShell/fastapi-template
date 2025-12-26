import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_refresh_flow():
    session = requests.Session()
    
    # 1. Sign In
    print(f"1. Logging in to {BASE_URL}/auth/sign-in...")
    login_data = {
        "username": "admin",
        "password": "admin"  # Default credentials
    }
    
    try:
        response = session.post(f"{BASE_URL}/auth/sign-in", json=login_data)
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Is it running on port 8000?")
        sys.exit(1)
        
    if response.status_code == 404 or response.status_code == 401:
        print("Login failed, attempting to sign up...")
        signup_data = {
            "username": "admin",
            "password": "admin",
            "email": "admin@admin.com",
            "full_name": "Admin User"
        }
        resp_signup = session.post(f"{BASE_URL}/auth/sign-up", json=signup_data)
        if resp_signup.status_code == 200:
             print("Sign up successful! Retrying login...")
             response = session.post(f"{BASE_URL}/auth/sign-in", json=login_data)
        else:
             print(f"Sign up failed: {resp_signup.status_code} - {resp_signup.text}")
             # Try a different user if admin exists but password wrong?
             # Just fail for now or try test/test
             
    if response.status_code != 200:
        print(f"Login failed: {response.status_code} - {response.text}")
        sys.exit(1)
        
    data = response.json()
    access_token = data.get("access_token")
    refresh_token = data.get("refresh_token")
    
    print("Login successful!")
    print(f"Access Token present: {bool(access_token)}")
    print(f"Refresh Token present (body): {bool(refresh_token)}")
    
    cookies = session.cookies.get_dict()
    print(f"Cookies: {cookies.keys()}")
    
    if "access_token" not in cookies:
        print("Error: access_token cookie not set")
    if "refresh_token" not in cookies:
        print("Error: refresh_token cookie not set")
        
    # 2. Test Access Token
    print("\n2. Testing Access Token at /auth/...")
    # The /auth/ endpoint expects 'token' query param due to Depends(oauth2_schema) or header?
    # modules/auth/controller.py:
    # oauth2_schema = OAuth2PasswordBearer("auth/sign-in")
    # def token(token: str = Depends(oauth2_schema)):
    # OAuth2PasswordBearer looks for Authorization header: Bearer <token>
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{BASE_URL}/auth/", headers=headers)
    
    if response.status_code == 200:
        print("Access Token valid!")
    else:
        print(f"Access Token invalid: {response.status_code} - {response.text}")
        # Note: If it fails, check if the endpoint uses the cookie or header. 
        # oauth2_schema usually looks for header unless overridden.
        
    # 3. Test Refresh
    print("\n3. Testing Refresh at /auth/refresh...")
    # Verify cookie is sent. 'session' should handle it automatically if domain matches.
    # The cookie path was set to /auth/refresh.
    
    response = session.post(f"{BASE_URL}/auth/refresh")
    
    if response.status_code == 200:
        print("Refresh successful!")
        new_data = response.json()
        new_access_token = new_data.get("access_token")
        print(f"New Access Token received: {bool(new_access_token)}")
        
        if new_access_token == access_token:
             print("Warning: New access token is same as old one (might be okay if not enough time passed or implementation details)")
        else:
             print("New access token is different (good).")
             
        # 4. Test New Access Token
        print("\n4. Testing New Access Token...")
        headers = {"Authorization": f"Bearer {new_access_token}"}
        response = requests.get(f"{BASE_URL}/auth/", headers=headers)
        if response.status_code == 200:
            print("New Access Token valid!")
        else:
            print(f"New Access Token invalid: {response.status_code} - {response.text}")

    else:
        print(f"Refresh failed: {response.status_code} - {response.text}")
        sys.exit(1)

if __name__ == "__main__":
    test_refresh_flow()

import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_api_middleware_refresh():
    session = requests.Session()
    
    # 1. Sign In
    print(f"1. Logging in to {BASE_URL}/auth/sign-in...")
    login_data = {"username": "admin", "password": "admin"}
    
    try:
        response = session.post(f"{BASE_URL}/auth/sign-in", json=login_data)
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server.")
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
             if resp_signup.status_code == 401: # user already exists
                 print("User seems to exist but login failed (maybe wrong password or role?). Retrying login anyway (maybe transient?).")
             else:
                 sys.exit(1)
        
    if response.status_code != 200:
        print(f"Login failed: {response.status_code} - {response.text}")
        sys.exit(1)
        
    data = response.json()
    access_token = data.get("access_token")
    refresh_token = data.get("refresh_token")
    
    if not access_token or not refresh_token:
        print("Error: Missing tokens in login response.")
        sys.exit(1)

    print("Login successful.")

    # 2. Test Protected API Route with EXPIRED/INVALID Access Token but VALID Refresh Token
    print("\n2. Testing protected route /users/ with invalid access token + valid refresh token header...")
    
    # Using a fake invalid token
    invalid_token = access_token + "invalid"
    
    headers = {
        "Authorization": f"Bearer {invalid_token}",
        "refresh-token": refresh_token
    }
    
    # /users/ usually requires admin permission. Assuming 'admin' user has it.
    response = requests.get(f"{BASE_URL}/users/", headers=headers)
    
    if response.status_code == 200:
        print("Access granted via refresh token!")
        new_access_token = response.headers.get("new-access-token")
        if new_access_token:
            print(f"New Access Token received in header: {new_access_token[:20]}...")
        else:
            print("Warning: Access granted but no 'new-access-token' header found.")
    else:
        print(f"Access failed: {response.status_code} - {response.text}")
        sys.exit(1)

if __name__ == "__main__":
    test_api_middleware_refresh()

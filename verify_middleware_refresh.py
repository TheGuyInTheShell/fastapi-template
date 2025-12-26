import requests
import sys
import time

BASE_URL = "http://127.0.0.1:8000"

def test_middleware_refresh():
    session = requests.Session()
    
    # 1. Sign In (Admin)
    print(f"1. Logging in to {BASE_URL}/admin/partial/sign-in...")
    # Form data for admin login
    login_data = {
        "username": "admin",
        "password": "admin"
    }
    
    try:
        # Note: Sign-in endpoint might catch exceptions and return HTML
        response = session.post(f"{BASE_URL}/admin/partial/sign-in", data=login_data)
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server.")
        sys.exit(1)
        
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        sys.exit(1)
        
    print("Login successful (Response OK). Checking cookies...")
    cookies = session.cookies.get_dict()
    print(f"Cookies: {cookies.keys()}")
    
    if "access_token" not in cookies or "refresh_token" not in cookies:
        print("Error: Missing tokens in cookies.")
        sys.exit(1)
        
    access_token = cookies["access_token"]
    
    # 2. Verify Access (Dashboard)
    print("\n2. verifying access to /admin...")
    response = session.get(f"{BASE_URL}/admin")
    if response.status_code == 200:
        print("Initial access successful.")
    else:
        print(f"Initial access failed: {response.status_code}")
        # Note: 302/307 redirects to sign-in mean fail
        print(response.headers)
        sys.exit(1)

    # 3. Trigger Refresh Logic
    # We will simulate an expired/missing access_token by deleting it from the session cookies
    print("\n3. Deleting 'access_token' cookie to trigger refresh...")
    session.cookies.set("access_token", None, domain="127.0.0.1", path="/")
    del session.cookies["access_token"] 
    
    # Be sure it's gone
    if "access_token" in session.cookies.get_dict():
        print("Warning: access_token still presents in cookies!")
    
    # Request protected route
    print("Requesting /admin again (should trigger middleware refresh)...")
    response = session.get(f"{BASE_URL}/admin")
    
    if response.status_code == 200:
        print("Refresh successful! Access granted.")
        
        # Check if new access token is set in response cookies
        # session.cookies automatically updates with response cookies
        new_cookies = session.cookies.get_dict()
        if "access_token" in new_cookies:
            print("New access_token cookie received.")
            if new_cookies["access_token"] != access_token:
                print("Token is new/different.")
            else:
                 print("Token is same (maybe logic just restored it).")
        else:
            print("Error: access_token cookie NOT received in response (Middleware issue?).")
            # If middleware sets cookie, it should be here. 
            # If middleware just allows request but doesn't set cookie, this will fail next request if we don't save it.
            
    else:
        print(f"Refresh failed: {response.status_code}")
        if response.history:
              print(f"History: {[r.status_code for r in response.history]}")
        sys.exit(1)

if __name__ == "__main__":
    test_middleware_refresh()

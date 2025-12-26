import requests
import pyotp
import sys

BASE_URL = "http://127.0.0.1:8000"
USERNAME = "admin"
PASSWORD = "password"

# Use the same session and helpers as verify_api_middleware_refresh.py if possible
# But this is standalone.

def test_2fa_flow():
    print("--- Starting 2FA Flow Verification ---")
    
    # 1. Login (Initial - 2FA Disabled)
    print("1. Logging in (Expect 200 OK w/ Tokens)...")
    payload = {"username": USERNAME, "password": PASSWORD}
    response = requests.post(f"{BASE_URL}/auth/sign-in", json=payload)
    
    if response.status_code != 200:
        print(f"FAILED: Login failed. Status: {response.status_code}, Body: {response.text}")
        # Try sign up if user missing?
        return
        
    data = response.json()
    access_token = data.get("access_token")
    if not access_token:
        print("FAILED: No access token returned")
        return
    
    headers = {"Authorization": f"Bearer {access_token}"}
    print("SUCCESS: Logged in.")

    # 2. Setup 2FA
    print("2. Setting up 2FA...")
    response = requests.get(f"{BASE_URL}/auth/2fa/setup", headers=headers)
    if response.status_code != 200:
        print(f"FAILED: Setup failed. Status: {response.status_code}, Body: {response.text}")
        return
    
    setup_data = response.json()
    secret = setup_data.get("secret")
    print(f"SUCCESS: Received secret: {secret}")

    # 3. Enable 2FA
    print("3. Enabling 2FA...")
    totp = pyotp.TOTP(secret)
    code = totp.now()
    
    enable_payload = {"otp_code": code, "secret": secret}
    response = requests.post(f"{BASE_URL}/auth/2fa/enable", json=enable_payload, headers=headers)
    
    if response.status_code != 200:
        print(f"FAILED: Enable failed. Status: {response.status_code}, Body: {response.text}")
        return
    print("SUCCESS: 2FA Enabled.")

    # 4. Login Again (Expect 202 Accepted w/ Temp Token)
    print("4. Logging in again (Expect 202 OTP Required)...")
    response = requests.post(f"{BASE_URL}/auth/sign-in", json=payload)
    
    if response.status_code != 202:
        print(f"FAILED: Expected 202. Status: {response.status_code}, Body: {response.text}")
        return
    
    login_data = response.json()
    temp_token = login_data.get("temp_token")
    if not temp_token:
        print("FAILED: No temp_token returned")
        return
    print("SUCCESS: Received temp_token.")

    # 5. Verify OTP
    print("5. Verifying OTP...")
    code = totp.now()
    verify_payload = {"otp_code": code, "temp_token": temp_token}
    response = requests.post(f"{BASE_URL}/auth/verify-otp", json=verify_payload)
    
    if response.status_code != 200:
        print(f"FAILED: Verify failed. Status: {response.status_code}, Body: {response.text}")
        return
    
    verify_data = response.json()
    new_access_token = verify_data.get("access_token")
    if not new_access_token:
        print("FAILED: No access token returned after verification")
        return
    
    print("SUCCESS: Verified OTP and received tokens.")
    
    headers = {"Authorization": f"Bearer {new_access_token}"}

    # 6. Disable 2FA
    print("6. Disabling 2FA...")
    response = requests.post(f"{BASE_URL}/auth/2fa/disable", headers=headers)
    if response.status_code != 200:
         print(f"FAILED: Disable failed. Status: {response.status_code}, Body: {response.text}")
         return
    print("SUCCESS: 2FA Disabled.")
    
    print("--- 2FA Flow Verification Complete ---")

if __name__ == "__main__":
    test_2fa_flow()

#!/usr/bin/env python3
"""
Test script to verify login phase implementation
"""

from ctf_solver import CTFSolver

def test_login():
    """Test the login phase specifically"""
    print("=" * 60)
    print("TESTING LOGIN PHASE")
    print("=" * 60)
    
    base_url = "http://u2lsx1lvvxnfzg-0.playat.flagyard.com"
    solver = CTFSolver(base_url)
    
    # First register to ensure account exists
    print("[+] Step 1: Register account (prerequisite)")
    reg_result = solver.register(username='testuser', password='testpass')
    print(f"[+] Registration result: {'SUCCESS' if reg_result else 'FAILED'}")
    
    print("\n" + "=" * 60)
    print("TESTING LOGIN WITH SAME CREDENTIALS")
    print("=" * 60)
    
    # Test login with same credentials
    print("[+] Step 2: Login with same credentials (username=testuser&password=testpass)")
    login_result = solver.login(username='testuser', password='testpass')
    
    print(f"[+] Login result: {'SUCCESS' if login_result else 'FAILED'}")
    
    # Show cookie state after login
    print(f"[+] Session cookies captured: {len(solver.cookie_jar)}")
    for cookie in solver.cookie_jar:
        print(f"    Cookie: {cookie.name}={cookie.value[:50]}...")
        print(f"    Domain: {cookie.domain}")
        print(f"    Path: {cookie.path}")
    
    # Test that cookies enable authenticated requests
    print("\n[+] Step 3: Test authenticated request capability")
    shop_url = f"{base_url}/shop"
    response = solver.make_request(shop_url)
    
    print(f"[+] Shop access status: {response['status']}")
    print(f"[+] Shop access URL: {response['url']}")
    
    if response['status'] == 200 and '/shop' in response['url']:
        print("[+] SUCCESS: Session cookies enable authenticated requests")
        return True
    else:
        print("[-] FAILED: Session cookies may not be working properly")
        return False

if __name__ == "__main__":
    test_login()

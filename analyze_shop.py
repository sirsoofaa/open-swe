#!/usr/bin/env python3
"""
Detailed shop analysis script to complete task 3
"""

from ctf_solver import CTFSolver
import re

def analyze_shop_detailed():
    """Perform detailed analysis of shop content"""
    print("=" * 60)
    print("DETAILED SHOP ANALYSIS - TASK 3")
    print("=" * 60)
    
    base_url = "http://u2lsx1lvvxnfzg-0.playat.flagyard.com"
    solver = CTFSolver(base_url)
    
    # Complete authentication flow
    print("[+] Step 1: Register and login")
    solver.register(username='testuser', password='testpass')
    solver.login(username='testuser', password='testpass')
    
    print("\n[+] Step 2: Access shop with authenticated session")
    shop_response, flag = solver.access_shop()
    
    if flag:
        print(f"[!] FLAG FOUND DURING SHOP ACCESS: {flag}")
        return flag
    
    if not shop_response or shop_response['status'] != 200:
        print("[-] Failed to access shop")
        return None
    
    print("\n[+] Step 3: Complete HTML content analysis")
    content = shop_response['content']
    
    # Save full HTML for inspection
    with open('shop_content.html', 'w') as f:
        f.write(content)
    print("[+] Full shop HTML saved to 'shop_content.html'")
    
    # Look for all button elements
    button_pattern = r'<button[^>]*>(.*?)</button>'
    buttons = re.findall(button_pattern, content, re.IGNORECASE | re.DOTALL)
    print(f"\n[+] Found {len(buttons)} button elements:")
    for i, button in enumerate(buttons):
        clean_button = re.sub(r'<[^>]+>', '', button).strip()
        print(f"    Button {i+1}: {clean_button}")
    
    # Look for onclick handlers
    onclick_pattern = r'onclick="([^"]*)"'
    onclick_handlers = re.findall(onclick_pattern, content, re.IGNORECASE)
    print(f"\n[+] Found {len(onclick_handlers)} onclick handlers:")
    for i, handler in enumerate(onclick_handlers):
        print(f"    Handler {i+1}: {handler}")
    
    # Look for JavaScript functions
    function_pattern = r'function\s+(\w+)\s*\([^)]*\)\s*\{'
    functions = re.findall(function_pattern, content, re.IGNORECASE)
    print(f"\n[+] Found {len(functions)} JavaScript functions:")
    for func in functions:
        print(f"    Function: {func}")
    
    # Look for AJAX endpoints
    ajax_patterns = [
        r'\.post\s*\(\s*["\']([^"\']+)["\']',
        r'\.get\s*\(\s*["\']([^"\']+)["\']',
        r'fetch\s*\(\s*["\']([^"\']+)["\']',
        r'XMLHttpRequest.*open\s*\(\s*["\'][^"\']*["\'],\s*["\']([^"\']+)["\']'
    ]
    
    ajax_endpoints = []
    for pattern in ajax_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        ajax_endpoints.extend(matches)
    
    if ajax_endpoints:
        print(f"\n[+] Found {len(ajax_endpoints)} AJAX endpoints:")
        for endpoint in ajax_endpoints:
            print(f"    Endpoint: {endpoint}")
    
    # Look for product data structures
    product_data_pattern = r'const\s+productData\s*=\s*\{(.*?)\};'
    product_data_match = re.search(product_data_pattern, content, re.DOTALL)
    if product_data_match:
        print(f"\n[+] Found productData JavaScript object")
        product_data = product_data_match.group(1)
        print(f"    Data preview: {product_data[:200]}...")
    
    # Look for cart functionality
    cart_patterns = [
        r'addToCart\s*\([^)]*\)',
        r'cart\s*\.\s*add',
        r'updateCart',
        r'cartItems',
        r'checkout'
    ]
    
    cart_functions = []
    for pattern in cart_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        cart_functions.extend(matches)
    
    if cart_functions:
        print(f"\n[+] Found {len(cart_functions)} cart-related functions:")
        for func in cart_functions:
            print(f"    Cart function: {func}")
    
    # Look for form elements (even if not in <form> tags)
    input_pattern = r'<input[^>]*>'
    inputs = re.findall(input_pattern, content, re.IGNORECASE)
    print(f"\n[+] Found {len(inputs)} input elements:")
    for i, inp in enumerate(inputs[:10]):  # Show first 10
        print(f"    Input {i+1}: {inp}")
    
    print("\n" + "=" * 60)
    print("SHOP ANALYSIS COMPLETE")
    print("=" * 60)
    
    return {
        'buttons': buttons,
        'onclick_handlers': onclick_handlers,
        'functions': functions,
        'ajax_endpoints': ajax_endpoints,
        'cart_functions': cart_functions,
        'inputs': inputs,
        'content_length': len(content)
    }

if __name__ == "__main__":
    result = analyze_shop_detailed()
    if result:
        print(f"\n[+] Analysis complete. Found {len(result.get('buttons', []))} buttons, {len(result.get('ajax_endpoints', []))} AJAX endpoints")

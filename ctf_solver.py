#!/usr/bin/env python3
"""
CTF Solver for TechShop Challenge
Hint: "You are alone in the shop just buy"
"""

import urllib.request
import urllib.parse
import urllib.error
import http.cookiejar
import re
import sys
from html.parser import HTMLParser


class FormParser(HTMLParser):
    """HTML parser to extract form data and action URLs"""
    
    def __init__(self):
        super().__init__()
        self.forms = []
        self.current_form = None
        self.in_form = False
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        if tag == 'form':
            self.in_form = True
            self.current_form = {
                'action': attrs_dict.get('action', ''),
                'method': attrs_dict.get('method', 'GET').upper(),
                'inputs': []
            }
        elif tag == 'input' and self.in_form:
            input_data = {
                'type': attrs_dict.get('type', 'text'),
                'name': attrs_dict.get('name', ''),
                'value': attrs_dict.get('value', ''),
                'placeholder': attrs_dict.get('placeholder', '')
            }
            self.current_form['inputs'].append(input_data)
        elif tag == 'button' and self.in_form:
            if attrs_dict.get('type') == 'submit':
                button_data = {
                    'type': 'submit',
                    'name': attrs_dict.get('name', ''),
                    'value': attrs_dict.get('value', 'Submit')
                }
                self.current_form['inputs'].append(button_data)
    
    def handle_endtag(self, tag):
        if tag == 'form' and self.in_form:
            self.forms.append(self.current_form)
            self.current_form = None
            self.in_form = False


class CTFSolver:
    """Main CTF solver class"""
    
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.cookie_jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookie_jar),
            urllib.request.HTTPRedirectHandler()
        )
        urllib.request.install_opener(self.opener)
        
    def make_request(self, url, data=None, method='GET'):
        """Make HTTP request with proper error handling"""
        try:
            if data is not None:
                if isinstance(data, dict):
                    data = urllib.parse.urlencode(data).encode('utf-8')
                elif isinstance(data, str):
                    data = data.encode('utf-8')
                    
            req = urllib.request.Request(url, data=data)
            req.add_header('User-Agent', 'Mozilla/5.0 (CTF Solver)')
            req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            
            response = urllib.request.urlopen(req)
            content = response.read().decode('utf-8', errors='ignore')
            
            return {
                'status': response.getcode(),
                'headers': dict(response.headers),
                'content': content,
                'url': response.geturl()
            }
            
        except urllib.error.HTTPError as e:
            error_content = e.read().decode('utf-8', errors='ignore')
            return {
                'status': e.code,
                'headers': dict(e.headers),
                'content': error_content,
                'url': e.url,
                'error': str(e)
            }
        except Exception as e:
            return {
                'status': 0,
                'headers': {},
                'content': '',
                'url': url,
                'error': str(e)
            }
    
    def parse_forms(self, html_content):
        """Parse HTML to extract form information"""
        parser = FormParser()
        parser.feed(html_content)
        return parser.forms
    
    def find_flag(self, text):
        """Search for flag patterns in text"""
        flag_patterns = [
            r'flag\{[^}]+\}',
            r'FLAG\{[^}]+\}',
            r'ctf\{[^}]+\}',
            r'CTF\{[^}]+\}',
            r'\{[a-f0-9]{32,}\}',
            r'[a-f0-9]{32,64}'
        ]
        
        for pattern in flag_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches
        return None
    
    def register(self, username='testuser', password='testpass'):
        """Register a new account"""
        print(f"[+] Registering account: {username}")
        
        register_url = f"{self.base_url}/register"
        data = {
            'username': username,
            'password': password
        }
        
        response = self.make_request(register_url, data, 'POST')
        
        print(f"[+] Registration response status: {response['status']}")
        print(f"[+] Registration response URL: {response['url']}")
        
        # Check for success indicators
        if 'success' in response['content'].lower() or response['status'] == 200:
            print("[+] Registration appears successful")
            return True
        elif 'already exists' in response['content'].lower():
            print("[+] User already exists, proceeding with login")
            return True
        else:
            print(f"[-] Registration may have failed: {response.get('error', 'Unknown error')}")
            print(f"[+] Response content preview: {response['content'][:200]}...")
            return False
    
    def login(self, username='testuser', password='testpass'):
        """Login with credentials"""
        print(f"[+] Logging in with: {username}")
        
        login_url = f"{self.base_url}/login"
        data = {
            'username': username,
            'password': password
        }
        
        response = self.make_request(login_url, data, 'POST')
        
        print(f"[+] Login response status: {response['status']}")
        print(f"[+] Login response URL: {response['url']}")
        print(f"[+] Cookies after login: {len(self.cookie_jar)}")
        
        # Check if redirected to shop or dashboard
        if '/shop' in response['url'] or 'shop' in response['content'].lower():
            print("[+] Login successful - redirected to shop")
            return True
        elif response['status'] == 200:
            print("[+] Login response received")
            return True
        else:
            print(f"[-] Login may have failed: {response.get('error', 'Unknown error')}")
            return False
    
    def access_shop(self):
        """Access the shop page"""
        print("[+] Accessing shop...")
        
        shop_url = f"{self.base_url}/shop"
        response = self.make_request(shop_url)
        
        print(f"[+] Shop response status: {response['status']}")
        print(f"[+] Shop response URL: {response['url']}")
        
        if response['status'] == 200:
            print("[+] Successfully accessed shop")
            
            # Print shop content for analysis
            print(f"[+] Shop content length: {len(response['content'])}")
            
            # Look for flag in shop page
            flag = self.find_flag(response['content'])
            if flag:
                print(f"[!] FLAG FOUND IN SHOP PAGE: {flag}")
                return response, flag
            
            # Analyze shop content for products and purchase mechanisms
            self.analyze_shop_content(response['content'])
            
            # Parse forms for purchase options
            forms = self.parse_forms(response['content'])
            print(f"[+] Found {len(forms)} forms in shop")
            
            for i, form in enumerate(forms):
                print(f"[+] Form {i+1}: {form['method']} {form['action']}")
                for inp in form['inputs']:
                    print(f"    Input: {inp}")
            
            return response, None
        else:
            print(f"[-] Failed to access shop: {response.get('error', 'Unknown error')}")
            return response, None
    
    def analyze_shop_content(self, content):
        """Analyze shop content for products and purchase mechanisms"""
        print("[+] Analyzing shop content...")
        
        # Look for product information
        products = []
        
        # Search for product patterns in JavaScript
        js_product_pattern = r'// ID: (\d+), Name: ([^\\n]+)'
        js_matches = re.findall(js_product_pattern, content)
        if js_matches:
            print(f"[+] Found {len(js_matches)} products in JavaScript:")
            for product_id, product_name in js_matches:
                products.append({'id': product_id, 'name': product_name})
                print(f"    Product {product_id}: {product_name}")
        
        # Look for HTML product elements
        html_patterns = [
            r'<div[^>]*class="[^"]*product[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*data-product-id="(\d+)"[^>]*>(.*?)</div>',
            r'<h[1-6][^>]*>([^<]*(?:laptop|phone|headphone|watch|product)[^<]*)</h[1-6]>',
        ]
        
        for pattern in html_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            if matches:
                print(f"[+] Found HTML product elements: {len(matches)}")
                for match in matches[:5]:  # Show first 5 matches
                    if isinstance(match, tuple):
                        print(f"    HTML: {match[0][:100]}...")
                    else:
                        print(f"    HTML: {match[:100]}...")
        
        # Look for purchase mechanisms
        purchase_patterns = [
            r'<button[^>]*(?:buy|purchase|order|cart)[^>]*>(.*?)</button>',
            r'<a[^>]*(?:buy|purchase|order|cart)[^>]*>(.*?)</a>',
            r'<input[^>]*type="submit"[^>]*value="[^"]*(?:buy|purchase|order|cart)[^"]*"',
            r'onclick="[^"]*(?:buy|purchase|order|cart)[^"]*"',
            r'function\s+(?:buy|purchase|order|cart)\s*\(',
        ]
        
        purchase_elements = []
        for pattern in purchase_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            if matches:
                purchase_elements.extend(matches)
        
        if purchase_elements:
            print(f"[+] Found {len(purchase_elements)} purchase-related elements:")
            for element in purchase_elements[:10]:  # Show first 10
                print(f"    Purchase element: {str(element)[:100]}...")
        else:
            print("[-] No obvious purchase elements found")
        
        # Look for JavaScript functions and AJAX calls
        js_function_patterns = [
            r'function\s+(\w*(?:buy|purchase|order|cart)\w*)\s*\([^)]*\)',
            r'(\w*(?:buy|purchase|order|cart)\w*)\s*:\s*function',
            r'\.post\s*\(\s*["\']([^"\']*(?:buy|purchase|order|cart)[^"\']*)["\']',
            r'\.get\s*\(\s*["\']([^"\']*(?:buy|purchase|order|cart)[^"\']*)["\']',
        ]
        
        js_functions = []
        for pattern in js_function_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                js_functions.extend(matches)
        
        if js_functions:
            print(f"[+] Found {len(js_functions)} JavaScript purchase functions/endpoints:")
            for func in js_functions:
                print(f"    JS function/endpoint: {func}")
        
        # Look for hidden elements or data attributes
        hidden_patterns = [
            r'data-product-id="([^"]+)"',
            r'data-price="([^"]+)"',
            r'<input[^>]*type="hidden"[^>]*name="([^"]+)"[^>]*value="([^"]+)"',
        ]
        
        hidden_data = []
        for pattern in hidden_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                hidden_data.extend(matches)
        
        if hidden_data:
            print(f"[+] Found {len(hidden_data)} hidden data elements:")
            for data in hidden_data[:10]:  # Show first 10
                print(f"    Hidden data: {data}")
        
        return {
            'products': products,
            'purchase_elements': purchase_elements,
            'js_functions': js_functions,
            'hidden_data': hidden_data
        }
    
    def make_purchase(self, shop_response):
        """Attempt to make a purchase"""
        print("[+] Looking for purchase functionality...")
        
        forms = self.parse_forms(shop_response['content'])
        
        # Look for buy/purchase forms
        purchase_forms = []
        for form in forms:
            form_html = str(form).lower()
            if any(keyword in form_html for keyword in ['buy', 'purchase', 'order', 'cart']):
                purchase_forms.append(form)
        
        if not purchase_forms:
            # Try any POST forms as potential purchase forms
            purchase_forms = [f for f in forms if f['method'] == 'POST']
        
        if not purchase_forms:
            print("[-] No purchase forms found")
            # Try common purchase endpoints
            common_endpoints = ['/buy', '/purchase', '/order', '/cart/add']
            for endpoint in common_endpoints:
                print(f"[+] Trying endpoint: {endpoint}")
                url = f"{self.base_url}{endpoint}"
                response = self.make_request(url, {}, 'POST')
                
                flag = self.find_flag(response['content'])
                if flag:
                    print(f"[!] FLAG FOUND: {flag}")
                    return flag
                    
                if response['status'] == 200:
                    print(f"[+] {endpoint} responded successfully")
                    print(f"[+] Response preview: {response['content'][:200]}...")
            
            return None
        
        # Try each purchase form
        for i, form in enumerate(purchase_forms):
            print(f"[+] Trying purchase form {i+1}")
            
            # Build form data
            form_data = {}
            for inp in form['inputs']:
                if inp['type'] in ['text', 'hidden', 'number']:
                    form_data[inp['name']] = inp['value'] or '1'
                elif inp['type'] == 'submit':
                    if inp['name']:
                        form_data[inp['name']] = inp['value']
            
            # Determine action URL
            action = form['action']
            if action.startswith('/'):
                purchase_url = f"{self.base_url}{action}"
            elif action.startswith('http'):
                purchase_url = action
            else:
                purchase_url = f"{self.base_url}/shop/{action}" if action else f"{self.base_url}/shop"
            
            print(f"[+] Submitting to: {purchase_url}")
            print(f"[+] Form data: {form_data}")
            
            response = self.make_request(purchase_url, form_data, 'POST')
            
            print(f"[+] Purchase response status: {response['status']}")
            print(f"[+] Purchase response URL: {response['url']}")
            
            # Look for flag in response
            flag = self.find_flag(response['content'])
            if flag:
                print(f"[!] FLAG FOUND: {flag}")
                return flag
            
            # Check headers for flag
            headers_text = str(response['headers'])
            flag = self.find_flag(headers_text)
            if flag:
                print(f"[!] FLAG FOUND IN HEADERS: {flag}")
                return flag
            
            print(f"[+] Response preview: {response['content'][:300]}...")
        
        return None
    
    def solve(self):
        """Main solving function"""
        print(f"[+] Starting CTF solver for: {self.base_url}")
        print(f"[+] Hint: 'You are alone in the shop just buy'")
        print()
        
        # Step 1: Register
        if not self.register():
            print("[-] Registration failed, but continuing...")
        
        print()
        
        # Step 2: Login
        if not self.login():
            print("[-] Login failed, exiting...")
            return None
        
        print()
        
        # Step 3: Access shop
        shop_response, flag = self.access_shop()
        if flag:
            return flag
        
        if not shop_response or shop_response['status'] != 200:
            print("[-] Could not access shop, exiting...")
            return None
        
        print()
        
        # Step 4: Make purchase
        flag = self.make_purchase(shop_response)
        
        return flag


def main():
    """Main function"""
    base_url = "http://u2lsx1lvvxnfzg-0.playat.flagyard.com"
    
    solver = CTFSolver(base_url)
    flag = solver.solve()
    
    if flag:
        print()
        print("=" * 50)
        print(f"[!] SUCCESS! FLAG FOUND: {flag}")
        print("=" * 50)
    else:
        print()
        print("[-] No flag found. Manual investigation may be required.")


if __name__ == "__main__":
    main()



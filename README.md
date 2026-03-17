# 403 Bypass Tool for Bug Bounty Hunters

A comprehensive tool for testing 403 forbidden bypass techniques with built-in rate limiting bypass capabilities.

## Features

- **Rate Limiting Bypass**: IP rotation, random delays, proxy support
- **Path Manipulation**: Test various path variations (..;, //, ./, etc.)
- **Header Bypasses**: X-Forwarded-For, X-Real-IP, and other headers
- **HTTP Method Testing**: TRACE, CONNECT, PROPFIND, and other methods
- **Protocol Variations**: HTTP/HTTPS switching, port variations
- **Case Sensitivity**: Uppercase, lowercase, mixed case tests
- **Unicode Bypasses**: Unicode normalization techniques
- **Parameter Pollution**: Add parameters that might bypass restrictions
- **Content-Type Manipulation**: Various MIME types
- **Advanced Headers**: Header combinations for deeper testing
🚀 Complete Guide: How to Use the 403 Bypass Tool
📦 Installation
Step 1: Clone or Create the Tool

Save the Python script as bypass403.py
Step 2: Install Dependencies
bash

pip install requests colorama
# or
pip install -r requirements.txt

Step 3: Make it Executable (Linux/Mac)
bash

chmod +x bypass403.py

🎯 Basic Usage Examples
1. Simple Scan

Test a single URL with default settings:
bash

python3 bypass403.py -u https://example.com/admin

2. Verbose Mode

See detailed output of each request:
bash

python3 bypass403.py -u https://example.com/admin -v

3. Save Results

Save successful bypasses to a JSON file:
bash

python3 bypass403.py -u https://example.com/admin -o results.json

🔥 Rate Limiting Bypass Examples
4. Add Delay Between Requests

Avoid rate limiting by adding delays:
bash

# Fixed 2 second delay
python3 bypass403.py -u https://example.com/admin --delay 2

# Random delays between 1-3 seconds
python3 bypass403.py -u https://example.com/admin --delay 1 --random-delay

5. IP Rotation Bypass

Rotate IP headers to bypass IP-based rate limiting:
bash

python3 bypass403.py -u https://example.com/admin --rotate-ip

6. Use Proxies

Rotate through different proxies:
bash

# Create proxies.txt file with one proxy per line
echo "127.0.0.1:8080" > proxies.txt
echo "192.168.1.1:3128" >> proxies.txt

# Run with proxies
python3 bypass403.py -u https://example.com/admin --proxy-file proxies.txt

🚀 Advanced Usage
7. Aggressive Scan

Use more threads with rate limiting protection:
bash

python3 bypass403.py -u https://example.com/admin \
  -t 20 \
  --delay 1 \
  --random-delay \
  --rotate-ip \
  -v \
  -o aggressive_scan.json

8. Stealth Mode

Slow and stealthy scan to avoid detection:
bash

python3 bypass403.py -u https://example.com/admin \
  -t 3 \
  --delay 5 \
  --random-delay \
  --rotate-ip \
  --proxy-file proxies.txt \
  -v

9. Quick Test

Fast test of common bypasses:
bash

python3 bypass403.py -u https://example.com/admin -t 30 -to 3

📋 Command Line Options Reference
Option	Description	Example
-u, --url	Target URL (required)	-u https://target.com/admin
-t, --threads	Number of threads (default: 10)	-t 20
-to, --timeout	Request timeout in seconds	-to 3
-v, --verbose	Verbose output	-v
-o, --output	Save results to JSON	-o results.json
--delay	Delay between requests (seconds)	--delay 2
--random-delay	Use random delays	--random-delay
--rotate-ip	Rotate IP headers	--rotate-ip
--proxy-file	File with proxies	--proxy-file proxies.txt
🎯 Real-World Scenarios
Scenario 1: Bug Bounty Program
bash

# Target: example.com's admin panel
python3 bypass403.py -u https://example.com/admin \
  --rotate-ip \
  --delay 1 \
  --random-delay \
  -v \
  -o bugbounty_results.json

Scenario 2: CTF Challenge
bash

# Fast scanning for CTF
python3 bypass403.py -u http://ctf-challenge.com/flag \
  -t 50 \
  -to 2 \
  -v

Scenario 3: Corporate Pentest
bash

# Stealthy corporate test
python3 bypass403.py -u https://internal.company.com/admin \
  -t 5 \
  --delay 3 \
  --random-delay \
  --rotate-ip \
  --proxy-file corporate_proxies.txt \
  -o pentest_results.json

📊 Understanding the Output
Color Coding:

    🟢 Green: Success! Status 200 OK

    🟡 Yellow: Partial success (other status codes)

    🔴 Red: Errors or failures

    🟣 Magenta: Interesting content detected

Sample Output:
text

╔══════════════════════════════════════════════════════════╗
║     403 Bypass Tool - Bug Bounty Edition                 ║
║     Testing: https://example.com/admin                   ║
║     Rate Limit Bypass: ON                                ║
║     Delay: 1s (random)                                   ║
╚══════════════════════════════════════════════════════════╝

[*] Testing original URL...
    Original status: 403

[*] Testing path variations...
[+] SUCCESS: Path: Trailing dot - Status: 200
[+] SUCCESS: Header: X-Forwarded-For localhost - Status: 200
[?] PARTIAL: Method: HEAD - Status: 405

💡 Pro Tips
1. Create Proxy List
bash

# Generate proxy list (example)
curl https://www.proxy-list.download/api/v1/get?type=http > proxies.txt

2. Combine with Other Tools
bash

# Use with ffuf for directory fuzzing
ffuf -u https://example.com/FUZZ -w wordlist.txt | while read line; do
  python3 bypass403.py -u "$line" --rotate-ip --delay 0.5
done

3. Monitor Rate Limiting

Watch for these indicators in verbose mode:

    429 status codes

    "Too Many Requests" messages

    Slow response times

    Connection resets

4. Optimize for Target

    API endpoints: Focus on header and method bypasses

    Admin panels: Focus on path variations and IP spoofing

    Cloud services: Focus on X-Forwarded headers

⚠️ Important Notes

    Always have permission to test the target

    Respect rate limits - use delays

    Don't DOS - keep threads reasonable

    Check results.json for detailed findings

    Some bypasses may be noisy - use stealth mode for sensitive targets

🐛 Troubleshooting
Common Issues:

"Connection refused"
bash

# Increase timeout
python3 bypass403.py -u https://example.com/admin -to 10

"Too many requests"
bash

# Add delays and rotate IP
python3 bypass403.py -u https://example.com/admin --delay 3 --rotate-ip

"SSL errors"
bash

# The tool handles SSL automatically, but if issues persist:
# Try HTTP version
python3 bypass403.py -u http://example.com/admin

📈 Performance Tips

    Start with -t 10 and adjust based on target response

    Use --delay to avoid getting blocked

    Enable --rotate-ip for aggressive targets

    Save results with -o for later analysis

    Use -v only when debugging (slows down scanning)

🎓 Practice Targets

Test on your own applications first:
bash

# Local test
python3 bypass403.py -u http://localhost/admin

# Test environment
python3 bypass403.py -u https://testphp.vulnweb.com/admin

Remember: With great power comes great responsibility - only test systems you own or have explicit permission to test!

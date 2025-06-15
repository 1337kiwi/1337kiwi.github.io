---
layout: post
title: Writeup - NahamCon CTF -- JS and JWT Token Exploits
date: 2025-05-28 01:24:59
tags: 
- rev
- web
- ctf
- writeup
---

<p class="meta">May 28 2024 - Web and Rev Challenges - NahamCon CTF Writeup Pt 1</p>

# NahamCon CTF

I fought in this war on team [Onlyfeet](https://ctftime.org/team/144644/), which I'm a part of. Yeah, I'm cool I promise. Here's some writeups, have fun. 

Long live the feet lovers. 

# SNAD

SNAD is a web challenge that presents us with an interactive sand dropping simulator. The goal is to analyze the client-side JavaScript and manipulate the sand physics to retrieve the flag.

## Initial Analysis

When we visit the challenge page, we're greeted with a sand dropping simulator interface. The page appears to be a physics simulation where sand particles fall and accumulate.

![SNAD Interface](/assets/ctf/nahamcon-2025/snad/interface.png)

## Code Review

Looking at the page source, we can examine the JavaScript code in `script.js`. The most interesting function we find is `retrieveFlag()`:

![retrieveFlag Function](/assets/ctf/nahamcon-2025/snad/retrieveflag-function.png)

This function appears to be the key to solving the challenge. Let's see what happens when we call it directly from the browser console.

## First Attempt

Running `retrieveFlag()` in the browser console gives us an interesting response:

![Retrieve Flag Output](/assets/ctf/nahamcon-2025/snad/retrieve-output.png)

The output shows: "Only 0/7 positions correct. Keep trying!" This tells us that we need to place sand in 7 specific positions to get the flag.

## Finding the Target Positions

The challenge provides a helpful debug feature - pressing the 't' key reveals the target positions where sand needs to be placed. This shows us exactly where we need to inject sand particles and what color they should be.

## Solution Strategy

After examining the code further, we discover two key functions:
1. `toggleGravity()` - Allows us to disable gravity so sand stays where we place it
2. `injectSand(x, y, colorHue)` - Allows us to programmatically place sand at specific coordinates with a specific color

The target positions are stored in `window.targetPositions`, which contains the exact coordinates and color hues we need.

## Solve Script

Here's the complete solution script:

```javascript
// Disable gravity so sand stays in place
toggleGravity();

// Get the target positions from the global variable
const targets = window.targetPositions;

// Inject sand at each target position with the correct color
targets.forEach(target => {
    injectSand(target.x, target.y, target.colorHue);
    console.log(`Injected sand at (${target.x}, ${target.y}) with hue ${target.colorHue}`);
});

// Now call retrieveFlag() to get our flag
retrieveFlag();
```

## Success!

After running our solve script, we successfully place sand in all 7 required positions and retrieve the flag:

![Success Output](/assets/ctf/nahamcon-2025/snad/success.png)

**Flag:** `flag{6ff0c72ad11bf174139e970559d9b5d2}`

## Key Takeaways
Written with AI support

This challenge demonstrates several important web security concepts:
- **Client-side validation weakness**: The flag verification happens entirely in the browser
- **JavaScript analysis**: Understanding client-side code to find hidden functionality
- **Browser developer tools**: Using the console to interact with and manipulate web applications
- **Physics simulation manipulation**: Bypassing intended game mechanics to solve the puzzle

The challenge was a fun combination of reverse engineering and creative problem-solving, requiring us to understand the sand physics simulation and find ways to manipulate it programmatically.

# Infinite Queue

Infinite Queue is a web challenge that presents us with a ticket queuing system. The goal is to bypass the queue system and purchase a ticket by exploiting JWT vulnerabilities and hidden functionality.

## Initial Analysis

When we visit the challenge page, we're greeted with a ticket queuing system interface. The description is adorable and sets up the scenario:

![Landing Page](/assets/ctf/nahamcon-2025/infinite-queue/landing.png)

![Adorable Description](/assets/ctf/nahamcon-2025/infinite-queue/adorable-desc.png)

The page appears very empty at first glance, but there are hidden elements we need to discover.

## Discovering Hidden Elements

Examining the page source reveals that there's more functionality than meets the eye. The buy-button seems to have something interesting:

![Buy Button](/assets/ctf/nahamcon-2025/infinite-queue/buy-button.png)

Further investigation reveals several hidden divs that contain additional functionality:

![Hidden Divs](/assets/ctf/nahamcon-2025/infinite-queue/hidden-divs.png)

![Hidden Div Details](/assets/ctf/nahamcon-2025/infinite-queue/hidden-div.png)

## The Queue System

When we sign up for the queue, we get placed in a very long queue - a totally serious reference to the challenge name:

![Ticket Queue](/assets/ctf/nahamcon-2025/infinite-queue/ticket-queue.png)

![Graduate School Queue](/assets/ctf/nahamcon-2025/infinite-queue/graduate%20school.png)

## JWT Analysis

Looking deeper into the app, we find a debug area and discover that when we sign up, we receive a basic JWT token:

![Basic JWT](/assets/ctf/nahamcon-2025/infinite-queue/basic-jwt.png)

Let's decode this JWT to understand its structure:

![Decoded JWT](/assets/ctf/nahamcon-2025/infinite-queue/decoded-jwt.png)

## Attempting to Complete Purchase

The hidden functionality reveals a complete purchase button, but when we try to use it, we get an error because our JWT is invalid:

![Complete Purchase Not Ready](/assets/ctf/nahamcon-2025/infinite-queue/complete-purchase-not-ready.png)

## Exploiting the Debug Functionality

To trigger the traceback in the debug area, I decided to manipulate the JWT. I created my own JWT with a modified timestamp set to the current time:

![Unix Timestamp](/assets/ctf/nahamcon-2025/infinite-queue/unix-timestamp.png)

![Resigned JWT](/assets/ctf/nahamcon-2025/infinite-queue/resigned-jwt.png)

When I submitted this manipulated JWT, it triggered a traceback that leaked the JWT signing key:

![JWT Secret](/assets/ctf/nahamcon-2025/infinite-queue/jwt-secret.png)

![Leaked JWT Key](/assets/ctf/nahamcon-2025/infinite-queue/leaked-jwt-key.png)

## Final Exploitation

Now that I have the JWT signing key, I can properly sign a valid JWT token. I took my previously invalid JWT, resigned it with the leaked key, and then attempted to complete the purchase:

![Success](/assets/ctf/nahamcon-2025/infinite-queue/success.png)

Success! The purchase completed and I was able to retrieve the flag.

## Key Takeaways
Written with AI Support

This challenge demonstrates several important web security concepts:

- **Hidden functionality discovery**: Using developer tools to find hidden DOM elements
- **JWT token manipulation**: Understanding JWT structure and attempting to forge tokens
- **Error-based information disclosure**: Exploiting debug functionality to leak sensitive information
- **Cryptographic key exposure**: How error messages can inadvertently expose signing keys
- **Token resignation**: Using leaked keys to create valid authentication tokens

The challenge was a great example of how seemingly innocent debug features can lead to serious security vulnerabilities, especially when they expose sensitive cryptographic material through error messages.
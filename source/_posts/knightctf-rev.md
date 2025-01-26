---
layout: post
title: Writeup - KnightCTF 2025 Rev Challenges | My Sword is Binja, My Shield is GEF 
date: 2025-01-24 04:04:06 -0400
tags: 
- rev
- knightctf
- ctf
- writeup
---

{{ page.title }}

<p class="meta">January 24 2024 - Writeups for all KnightCTF Rev Challenges</p>

# KnightCTF

I recently competed in KnightCTF 2025 for shits and giggles, and I wanted to do the rev challenges because I've been wanting to improve my reverse-engineering skills? 

This CTF was fun and the challenges, while not overly complex, were a great refresher on basic reverse engineer methodologies. I ended up being too busy to do one or two of the challenges in time, so I ended up doing those on my own afterwards.

Also, I try to put the challenge creator in these to give them credit, but after the challenges were over they took them down basically instantly, and their [URL](https://2025.knightctf.com/challenges) 403's me when I try to look at them. 

# Knight’s Droid 

Basic APK Reversing. 

Chall Description

    For ages, a cryptic mechanical guardian has slumbered beneath the Knight’s Citadel. 
    Some say it holds powerful secrets once wielded by ancient code-wielding Knights. 
    Many have tried to reactivate the droid and claim its hidden knowledge—yet none have returned victorious. 
    Will you be the one to solve its riddles and awaken this legendary machine?

The challenge consisted of [an apk file](/assets/ctf/knightctf-2025/knightsdroid/knights_droid.apk). Usually, when I see APKs, I use [jadx](https://github.com/skylot/jadx) or [JD-GUI](http://java-decompiler.github.io/) to decompile them. They're solid, easy to use, and can handle most APK reverse-engineering. In this case, I used jadx. 

APKs can be easily decompiled because they're packaged in a format that includes compiled bytecode (DEX files), and all other resources the app uses (images, config files, etc.), and they aren't obfuscated or protected by default. DEX bytecode is easily converted back to readable formats by the above applications, and APKs aren't inherently protected in any way. I have seen a rise in the number of obfuscated APKs, but overall the trend is still to not heavily protect the APK.

## 1. Browsing the source code

Looking around, the first thing I'll take a look at is the `com/knightctf.knights_droid` folder, as that's where the meat of the app is (usually) stored. I see several classes, and go through them. The first interesting one for me is `MainActivity`, where I see the flag checking being performed. 

<img src="/assets/ctf/knightctf-2025/knightsdroid/mainactivity.png" width="1000px">

Taking a closer look, we see a class called `SecretKeyVerifier` being used, which looks like this.

<img src="/assets/ctf/knightctf-2025/knightsdroid/secretkey.png" width="1000px">

## 2. Shifts and Ciphers

Okay, cool. We have a couple strings here, most notably the `GYPB{_ykjcnwp5_GJECDP_u0q_c0p_uKqN_Gj1cd7_zN01z_}` string. We perform the `computeShiftFromKey` function on this string, passing in a `firstTen` variable. Looking at the rest of the code, the app takes in the first 10 characters of `context.getPackageName();`, which should be `com.knight`. So it takes the first ten letters of the package name, and passes them into this function 

```java
    private static int computeShiftFromKey(String key) {
        int sum = 0;
        for (char c : key.toCharArray()) {
            sum += c;
        }
        return sum % 26;
    }
```

and then takes the number computed and passes it into this function

```java
    private static String droidMagic(String input, int droidTask) {
        int droidTask2 = ((droidTask % 26) + 26) % 26;
        StringBuilder sb = new StringBuilder();
        for (char c : input.toCharArray()) {
            if (Character.isUpperCase(c)) {
                int originalPos = c - 'A';
                int newPos = (originalPos + droidTask2) % 26;
                sb.append((char) (newPos + 65));
            } else if (Character.isLowerCase(c)) {
                int originalPos2 = c - 'a';
                int newPos2 = (originalPos2 + droidTask2) % 26;
                sb.append((char) (newPos2 + 97));
            } else {
                sb.append(c);
            }
        }
        return sb.toString();
    }
```

## 3. Shifting Sands

Just by looking at `droidMagic`, I can tell it performs a basic character shift, between 0 and 25 (26 characters in the alphabet). 

For each character in the input string:
    If the character is an uppercase letter, it shifts its position within the uppercase alphabet (A-Z) by droidTask2 positions.
    If the character is a lowercase letter, it shifts its position within the lowercase alphabet (a-z) by the same amount.
    Any non-alphabetic character (e.g., spaces, punctuation) is left unchanged.

While I can create a solve script to figure this out, I can also just bruteforce this. It's a rotation cipher, so I stick it in cyberchef, and go up and down the rotations until I see that it's ROT4. Cyberchef hands us the flag

![cyberchef output](/assets/ctf/knightctf-2025/knightsdroid/cyberchef.png)

`KCTF{_congrat5_KNIGHT_y0u_g0t_yOuR_Kn1gh7_dR01d_}`

# Binary Quest

Protection Bypassing, or basic string lookup

Chall Description

    In the far-off kingdom of Valoria, an ancient relic called the “Sacred Flag” lies hidden within a guarded fortress. 
    Legend says only a true knight of cunning and skill can lay claim to its power. 
    Dare you venture into the shadows and emerge victorious? 
    Your journey begins now—onward, brave soul, and seize your destiny in the Binary Quest.

We're given a [binary file](/assets/ctf/knightctf-2025/binaryquest/binary.quest).

## Step 1. USPS? UPS? Nah, UPX.

When looking at the strings, we can see that it's packed by [UPX](https://upx.github.io/).
![This file is packed with the UPX executable packer.](/assets/ctf/knightctf-2025/binaryquest/upx.png)

We also see what seems to be the flag.

![partial flag](/assets/ctf/knightctf-2025/binaryquest/partial_flag.png)

That's interesting, but that flag seems to be a partial one. Let's actually unpack this thing. 

`upx -d ./binary.quest` gives us the unpacked binary. 

## Step 2. The binary

First, knowing that the partial flag may exist, I take a look at where it's located. I see that the main() function calls strcpy() and strncpy() on it. Aaaaaand Binja automatically displays it. Nice.

![binja found the flag](/assets/ctf/knightctf-2025/binaryquest/flag.png)

Flag is `KCTF{_W4s_i7_e4sY?_}`

But let's try to remove the debugging check, for shits and giggles (thanks for the idea @abl_). 


## Bonus: PTRACE? More like NOPTRACE.

So in the main function, we call another function before anything else is done, except the basic output. This function, `sub_12e0()`, performs a debugging check. It calls ptrace to check for a debugger, and exits if it sees a debugger.

```c
int64_t sub_12e0()

    int64_t result = ptrace(request: PTRACE_TRACEME, 0, 1, 0)
    
    if (result != -1)
        return result
    
    puts(str: "\nThe King's Watchers sense pryi…")
    puts(str: "You have been discovered! The ch…")
    exit(status: 1)
    noreturn
```

The dissassembly looks like this:

```assembly
sub_12e0:
    sub     rsp, 0x8
    xor     ecx, ecx  {0x0}
    xor     esi, esi  {0x0}
    xor     edi, edi  {0x0}
    xor     eax, eax  {0x0}
    mov     edx, 0x1
    call    ptrace
    cmp     rax, 0xffffffffffffffff
    je      data_1300[1]

    add     rsp, 0x8
    retn     {__return_addr}

    lea     rdi, [rel data_2008]  {"\nThe King's Watchers sense pryi…"}
    call    puts
    lea     rdi, [rel data_2040]  {"You have been discovered! The ch…"}
    call    puts
    mov     edi, 0x1
    call    exit
```

We can do a lot here to bypass the check. 

1. We can patch the `cmp rax, 0xffffffffffffffff` instruction to be `cmp rax, 0`, which would effectively bypass the branch from ever being taken, because rax would no longer equal `0xffffffffffffffff`. 
2. We could also patch the `call ptrace` instruction to a nop, bypassing the syscall. 
3. We could also modify the `rax` register after the ptrace call by inserting an instruction like `mov rax, 0x0`, resulting in a successful ptrace call.
4. We could also replace the jump instruction with a nop instruction. 

Anyways, [I modified the file](/assets/ctf/knightctf-2025/binaryquest/modified_binary.quest). Now, we can use ltrace and the flag will be used in the strlen instruction. 

# Easy Path to the Grail

Reversing bit orders and hex encodings.

    Brave knight, your quest is simple yet essential—unlock the secrets hidden in this binary challenge and tread the path to the grail. The journey will test your wits as you reverse the provided binary, uncovering the treasure within.

Again, we're given a [binary file](/assets/ctf/knightctf-2025/easypathtothegrail/grail.knight).

This one isn't packed with UPX, but they also haven't stripped many of the symbols. This is nice! 

## Step 1. The Binary

Going through the main() function, I rename variables based on behaviour, and get a better understanding of what's going on. 

![main function](/assets/ctf/knightctf-2025/easypathtothegrail/main.png)

It seems that we're taking the user input, running teh `tranform_input()` function on it, and then comparing the output to `D2C22A62DEA62CCE9EFA0ECC86CE9AFA4ECC6EFAC6162C3636CC76E6A6BE`. 

Cool, so the `tranform_input()` function is what we actually need to reverse.

## Step 2. Transformers (not in the ai sense)

The `transform_input()` looks like this. I've commented what each important line does. 

```c
  char* transform_input(char* input, char* output)

  {
      char* input_ptr = input;
      char* output_ptr = output;
      
      while (*(uint8_t*)input_ptr) // Loops until null terminator is reached
      {
          sprintf(output_ptr, "%02X", (uint64_t)do_fight(*(uint8_t*)input_ptr), "%02X"); // The `sprintf` line takes in the current byte of input and runs the `do_fight()` function on it.
          output_ptr = &output_ptr[2]; // Since do_fight() output is hex format, we move the ptr forward 2 bytes to write the next 2 hex digits
          input_ptr = &input_ptr[1]; // We move the ptr forward 1 byte to the next char in input
      }
      
      *(uint8_t*)output_ptr = 0; // Add a null terminator to the end of output string
      return output_ptr;
  }
```

Okay, so all that `transform_input()` does is take the input string, run `do_fight()` on each character, format the `do_fight()` output to a hex code, and build an output string containing that. Cool. Let's take a look at `do_fight()`

## Step 3: Final round. Fight! 

The `do_fight()` function looks like this.

```c
  uint64_t do_fight(uint8_t arg1) __pure

  {
      uint8_t var_1c = arg1;
      char var_d = 0;
      
      for (int32_t i = 0; i <= 7; i += 1)
      {
          var_d = var_d << 1 | (var_1c & 1);
          var_1c u>>= 1;
      }
      
      return (uint64_t)var_d;
  }
```

I cleaned it up.

```c
  uint64_t do_fight(uint8_t inputChar) __pure

  {
      uint8_t inputCharTMP = inputChar;
      char reversedBits = 0;
      
      for (int32_t i = 0; i <= 7; i += 1)  // 8 bytes total
      {
        // Shift the current reversed bits in reversedBits to the left by 1 then add the LSB of inputCharTMP to reversedBits.
        reversedBits = reversedBits << 1 | (inputCharTMP & 1);

        // Right shift inputCharTMP to process the next bit 
        inputCharTMP u>>= 1;
      }
      
      return (uint64_t)reversedBits;
  }
```

What this does, essentially, is take the input character as an 8-bit input, and reverses the order of its bits. 
For each of the 8 bits in inputChar, we shift the current bit in reversedBits left by 1 to make space for the new bit.
Then, we use a bitwise AND `& 1` to extract the right-most bit of inputChar, add it to reversedBits, and then shift inputChar by 1 to loop around and perform the same task on the next bit. 

Let's reverse this process. I made a [python script](/assets/ctf/knightctf-2025/easypathtothegrail/solve.py) to do it.

```python
output = 'D2C22A62DEA62CCE9EFA0ECC86CE9AFA4ECC6EFAC6162C3636CC76E6A6BE'

byteArr = bytes.fromhex(output)

revBytes = []

for byte in byteArr:
    reversedByte = 0
    for i in range(8):
        # Shift reversed_byte left by 1 and append the LSB of byte
        reversedByte = (reversedByte << 1) | (byte & 1)
        # Shift byte right by 1
        byte >>= 1
    revBytes.append(reversedByte)

reversed_string = bytes(revBytes).decode('ascii')

print(f"Reversed string: {reversed_string}")
```

And our flag is `KCTF{e4sy_p3asY_r3v_ch4ll3nge}`

# Knight's Enigma

Reversing bit orders and hex encodings.

    In the shadowed corridors of an ancient fortress, a legendary knight once safeguarded a secret so potent that countless contenders have vanished trying to decipher it. 
    Now the seal has cracked, and echoes of its power seep into the present. 
    Test your courage as you follow cryptic traces left by the knight’s hand, unraveling an enigma steeped in the mysticism of ages past.
    Will your wits prove enough to break the bindings and uncover the realm’s hidden legacy—or will you, too, fade into the swirling mists of history? 
    The choice—and fate—are yours to determine.

Again, we're given a [binary file](/assets/ctf/knightctf-2025/knightsenigma/knight_s.enigma).

This one has a massive main() function, and it seems to be written in rust, considering the methodologies it uses. However, a lot of the code here isn't necessarily important. Looking at our code, our win condition seems to be getting a successful `memcmp()` on two variables. 

![main](/assets/ctf/knightctf-2025/knightsenigma/main.png)

## Step 1. Dast, Rust, Dust


After some going back and forth, I realised that we could ignore a lot of the SIMD operations and memory modifications, as this was the important part of our code. After attaching gdb and running through this code a couple times, I realized that, outside of memory operations, these bits of code were what actually modified anything.

```rust
    if (rdx_32:1.b == 0) // or if (rdx_14:1.b == 0)
        rax_11 = mods.dp.d(sx.q(rax_11 - 0x60), 0x1a) + 0x61
    else
        rax_11 = mods.dp.d(sx.q(rax_11 - 0x40), 0x1a) + 0x41
```

```rust
    char rdx_43 = (rax_11.b u>> 4 & 1) | (((rax_11.b u>> 3 & 1) | (((rax_11.b u>> 2 & 1) | ((((rax_11.b * 2) & 2) | (rax_11.b u>> 1 & 1)) * 2)) * 2)) * 2)
    char rcx_12 = (rax_11.b u>> 5 & 1) | (rdx_43 * 2)
    uint8_t rdx_45 = rax_11.b
    rax_11.b u>>= 7
    char var_87_1 = (rax_11.b | (((rdx_45 u>> 6 & 1) | (rcx_12 * 2)) * 2)) ^ 0xaa
```

It just performed these actions, rinse and repeat, on each value in each register. 
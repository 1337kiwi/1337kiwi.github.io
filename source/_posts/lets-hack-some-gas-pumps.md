---
layout: post
title: "Let's hack some gas pumps"
date: 2026-06-13 04:04:06 -0400
tags:
- hardware
- embedded
- payments
- blogpost
---

I spent about five hours talking to a Gilbarco Veeder-Root (GVR) field technician. Their whole job is opening these machines up, swapping boards, and reflashing them. I have never gotten this much detail on how a gas station works under the hood, and unless I end up cornering one of the engineers who designed them, I probably won't get better detail. 

> Some Disclaimers: I had full permission from the owner of the gas station to experiment and hack and fuck around to my heart's content. Turns out that when you help gas stations with detecting and shutting down illegal jammers (which criminals use to steal money from the shady gambling arcade games in gas stations -- maybe a blogpost for later!), they trust you to fuck around with their stuff :D. 
> This technician was also cool as hell (he had a laptop running Kali Linux). Anyways, don't do any of this without permission from everyone involved!

This blogpost is about the security posture of the fuel dispenser you use every week. 

To answer the lamest and least interesting question of the day, no, stealing gas isn't hard, you just have to pop open the cabinet with a CH751 key and pull out a specific cable right when it starts pumping, or sometimes before depending on the model. Have fun figuring out the cable. And honestly, if you want to steal bad enough that you'll take apart the front of a gas pump for it, then be my guest. Just keep in mind that the person who eats that theft is usually the franchisee who owns that one station, not some faceless megacorp.

# What's Actually in a Gas Pump

A modern dispenser is a little network of computers stuffed into a steel cabinet, sitting on top of the hydraulics that move the actual fuel.

![Inside an open Gilbarco Encore dispenser](/assets/gas/internals.png)

Open the top and there are boards everywhere. The ones worth knowing about:

- The secure payment module is a separate, tamper-protected board that handles card data. It shows up in the menus as "VFI" (Verifone lineage). The payment path is separated from the general config side, and hitting config mode or hacking most of the machines on the pump won't do you any favours. Most of the processing is done on the board, and data in transit is communicated securely. This split is a surprise tool that will help us later! ([Gilbarco Encore 700 S Start-up and Service Manual](/assets/gas/encore-700s-service-manual.pdf))
- The printer: It runs its own firmware, and you can update that firmware from the config menu. Yes, the receipt printer has a firmware update option sitting in the same menu as the network config.
- The comms board: A board just for wireless RX/TX. The dispenser talks back to a controller inside the store, sometimes over a wire and sometimes over radio. This also receives pricing updates and puts them on the gas pump itself. (Fun detail: the current in-dispenser router has a [dedicated alarm](/assets/gas/flexpay-iv-omnia-service-manual.pdf) just for "pump serial cable left disconnected".)

  NOTE: Messing with this is *hard*. I allegedly may have tried and I'm pretty sure the TXes have authenticated encryption. 
- The hydraulics: Under all the electronics are the pump, the meters, the valves, and the plumbing. This is the part that weights-and-measures inspectors actually regulate.
- The CRIND: "Card Reader In Dispenser." This runs the whole customer side: the screen, the keypad, the card reader, and the contactless pad. On the newer Encore units, the CRIND is Gilbarco's FlexPay hardware. 

You can hit diagnostic mode in these systems using the blue card! 

None of this is exotic. It's embedded boards, serial links, and a controller. The weird part is that it lives outdoors where anyone can realistically mess with it for years on end. The threat model is unique and interesting. 

# The Blue Card

The tech gifted me this:

![Gilbarco Veeder-Root Fueling Systems diagnostic card, held against the pump's DEVICE CONFIG screen](/assets/gas/device_config.jpg)

It's a Gilbarco "Fueling Systems" diagnostic card, part #Q12534-170. And **you can just buy it online.** 

It's a listed part at fuel-equipment supply stores, and nobody gatekeeps it. [Here's one listing.](https://store.senecaco.com/store/c47/miscellaneous-dispenser-parts/p116/gilbarco-q12534-170-diagnostic-card/)

Swipe it at the pump, where you would normally swipe a credit card, and you drop into a diagnostics and configuration mode. This whole menu tree is documented in Gilbarco's own public FlexPay IV (with Omnia) service manual, if you want to read along. ([MDE-5369V, p.4-3](/assets/gas/flexpay-iv-omnia-service-manual.pdf#page=27)) Here's the DEVICE CONFIG screen from that same photo, with the card held up against it:

```
DEVICE CONFIG
<1> - DEVICE SELECTION
<2> - VFI DEVICE CONFIGURATION
<3> - OTHER DEVICES IP ASSIGNMENT
<4> - TIMEZONE SELECTION
<5> - PRINTER FIRMWARE UPDATE
<6> - RESTORE DEFAULT RESOURCES
<7> - DAILY REBOOT PARAMETER
```

So from the curb, with a card anyone can order, you get device selection, config for the secure payment module, IP assignment for the other devices on the forecourt, and a "restore default resources" option. 

Let's hope the security cameras work. 

## The Card Is Just a Magstripe

I have a magstripe reader/writer, so of course I read the card. Here's the whole thing:

```
Track 1 (210 BPI, 7 BPC, odd parity):
GILBARCO DIAGNOSTICS NOT VALID FOR SALES0000000001

Track 2 (75 BPI, 5 BPC): separators only, no real payload
Track 3: no data
```

![Reading the card in a magstripe utility](/assets/gas/magread.png)

That's it. It's a static string on track 1. There's no challenge-response, no second factor auth, and the data is the same on every swipe. The "authentication" for the dispenser's configuration menu is a fixed value on a magstripe, and the magstripe is for sale.

Anyone with a $30 reader and a blank HiCo card can clone it. Keep an eye out for me at security conferences :P

# So Can You Actually Do Damage?

From the menu alone, less than I expected.

I could change a lot in diagnostic mode: availability, device parameters, and a pile of other config. So my first thought was the obvious one: Can I change the price of gas? 

nope

It doesn't work, at least not cleanly, because the dispenser doesn't control the price. It constantly pulls from the controller inside the store, also known as the basestation, and the basestation overrules any price you change locally on one pump. 

To make a bogus price stick, you'd have to attack the link between the pump and the basestation instead of the pump itself. That puts you in radio territory, and you need a whole hackrf and if you jam it you gain a couple felonies, and if you override the signal with your own I'm pretty sure the FCC just kills you.

Which is good! (The consistent updates, not the FCC killing me) 

That re-check is the pump doing something right. The config menu is wide open, but the pump doesn't trust its own copy of the price, and the payment path sits on its own walled-off module (told you that split would come back).

# The Lock Everyone Already Has the Key To

The way you actually get a pump to dispense fuel it shouldn't is physical, and it's not hard to figure out what cable needs to be pulled. It does depend on the model, but those schematics are everywhere online at this point. 


If you've been around physical security at all, you know of the CH751 key. It opens a ridiculous amount of commercial equipment and RV panels and elevators and displays and it costs like 2 bucks. So the physical security of an unattended box full of embedded computers that probably cost a pretty penny comes down to a lock that barely counts. 

Sometimes, gas station owners will slap a masterlock or some other lock somewhere on the panel for a secondary measure, and that adds about 30 seconds worth of time it takes to get into the cabinet. 

The pulsers, which actually count how much fuel went out, got an encrypted version around 2017 with a unique ID per unit and lift-off detection that kills the fueling position if someone pulls it off the meter. ([Encrypted pulser retrofit kit manual](/assets/gas/encrypted-pulser-retrofit-kit.pdf))

# This Lines Up With the Public Record

The fuel industry has a documented security history, and what I saw lines up with it pretty well.

- Tank gauges on the open internet: Back in 2015, HD Moore at Rapid7 scanned for automatic tank gauges exposed on TCP port 10001 and found ~5,800 of them that could be reached from the internet with no auth. You could mess with stuff. ([Rapid7](https://web.archive.org/web/20210413200023/https://www.rapid7.com/blog/post/2015/01/22/the-internet-of-gas-station-tank-gauges/))
- In October 2025, a CISA advisory came out for the GVR TLS4B tank gauge. It's a CVSS 9.9 that gives an authenticated remote attacker a shell on the linux machine. ([CISA](https://www.cisa.gov/news-events/ics-advisories/icsa-25-296-03)) The tank gauge is still the soft spot it seems.
- In May 2026, CNN reported "Iranian hackers" (lol) broke into tank gauges at stations across the US, hitting the same "sitting on the internet with no password" problem that Rapid7 called out, and sometimes messing with fuel readings. ([CNN](https://www.cnn.com/2026/05/15/politics/iran-hackers-tank-readers-gas-stations))

The money path (EMV, payment modules, price rechecks, and anti-skimmer tech) keeps getting more secure, but everything around it, like tank gauges and config menus and cabinet locks, is behind by decades.

And it's *hard* to figure it out. Changing keys is immensely expensive, it means that technicians have to have copies of keys for every gas pump. And what if the gas station owner loses those keys, and the technicians don't have backups? How do you make it as cheap and easy as possible to perform maintenance on the millions of gas pumps around the country? 

Well, you've gotta give up security. And it will probably stay completely unimportant to these corporations unless...

1. Being insecure becomes more expensive. Fines or constant breaches or people being annoying and putting every gas pump they see in DIAG mode. Something where a company loses more money by **not** securing the thing. 

or

2. The government starts dishing out fines and regulations. Which is 1 with extra steps. 

And GVR basically admitted it in 2015, when it sent out a security notice that said that the tank gauge passcode ships off by default, and told customers to coordinate with "any third party that might be polling the gauge" before turning security on. Flipping it on meant re-provisioning everyone who remotely checks the tank, and not breaking the maintenance workflow is more important than improving security posture. Which is a completely valid business decision and at least they're honest about it? ([Veeder-Root Technical Service Notification, Jan 2015](/assets/gas/veeder-root-atg-security-notice-2015.pdf))

> Also a good point as to why "secure-by-design" and "first principles" and all those fancy words that basically mean "prioritizing security from the beginning of product design" are important. Start with security from the ground up and you won't have to make half measures to secure it after. 

Gilbarco's own Passport newsletter from 2011 told merchants they could remotely manage the POS server over VNC, or a VPN tunnel, reasoning that "neither solution affects your PCI compliance because you are not accessing a device that stores critical card holder information." ([Gilbarco, 2011](/assets/gas/passport-vnc-notice-2011.pdf))

# Where I'd Look Next

The magstripe is basic low hanging fruit, but I think there's more there. That card is a flat, static string that unlocks a "diagnostics, not for sales" level. Is there a *higher* level? Maybe an engineer or factory code that unlocks more than the field-tech card does in the same format? I'd probably make a bunch of potential likely cards and test them all but that's a lot of work right now. Maybe reversing the scanner would work. 

I keep also thinking about the controller. It was running Win7 and definitely had vulnerabilities. But I did some research and documentation work and there is more there. Omnia is the little router that GVR puts inside US dispensers to do the 2 wire loop over TCP/IP ([Omnia service manual](/assets/gas/flexpay-iv-omnia-service-manual.pdf)), and the store itself has an EDH ([EDH PA-DSS implementation guide](/assets/gas/passport-edh-pa-dss-guide.pdf)).

Nobody outside Gilbarco has published anything about either one. Tank gauges got audited and attacked publicly in 2015 and last year, and a similar controller got an [admin backdoor and RCE in 2017](https://securelist.com/expensive-gas/83542/). ([CISA advisory](https://www.cisa.gov/news-events/ics-advisories/icsa-19-122-01))

But the Omnia and the EDH? No CVEs, no DEF CON / blackhat talks, nothing on github, and not even wireshark files on any forums. There's an SDK over at [gvrspotsdk.com](https://www.gvrspotsdk.com/), but you have to file an NDA with GVR and hand over a lab contact. ([FlexPay IV Simulator Reference Sheet](/assets/gas/flexpay-iv-simulator-reference.pdf)) So the real way probably isn't asking nicely although social engineering may work. I probably have to wait for an EDH or Omnia board to fall off the back of a truck right in front of me and see if I can pop a UART or JTAG connection and get a shell.

I'm willing to bet that at companies like Gilbarco, security isn't as much of an issue. Prodsec teams are constantly at war with engineers who want to ship products, and teams that don't want to put in effort for what they see as low risk situations. 

This is the same story played in tens of thousands of companies every day. The payment stack got better because it was expensive to *not* improve it, with chargebacks and fines and fraud making it costly to ignore. Everything else like the lock, the config menu, the tank gauge, and whatever OS happens to still be running in the back room, stays insecure as it's cheaper to be insecure. 

If you know more about these systems or feel like chatting, let me know :)  
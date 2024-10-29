# unbound-onlywhite

## Make an Exam Environment by whitelisting only allowed Domains aka. Websites

The idea to this was born at scool, where I have to exam students periodically. IMO it should be possible for them to access some parts
of the internet (where the docs live), but no ChatGPT and friends, webmail sites and other cheating opportunities. So I built this script (`exam.py`) here based on OPNSense and the unbound resolver. The main "trick" is to set the root zone (`.`) to "refuse" and from there down gently open up the sites they should be able to use. Have a look at the files in the `etc` dir. Have in mind, that, if you allow "ecosia.org" for example, this implicitly also allows "api.ecosia.org", which you probably want to block separately in the *.den.zone file. As alternative one could just allow "www.ecosia.org".

## Getting started

### Important OPNSense fiddlery

- git clone this repository as `root` into `/root` (or just extract the zipfile/tarball)
- prohibit port 53 destinations coming from the WIFI
- prohibit other cheating opportunities like port 22
- unbound should only listen on the WIFI routing interface
- unbound should use some other "on premise" DNS Server (as "forward"). Not using a forwarder, I ran into strange timeouts when unbound does the recursion on its own. I find this behaviour plausible, as I am doing weird things.
- raise unbounds log level for querylogs in order to track denied queries
- OPNSense should not use this kinda misconfigured unbound as a system resolver itself.

### optional OPNSense fiddlery

- install bash or other (unsing `pkg` from the root shell)
- have an equivalent of the "toor" user with uid=0 with your favorite shell as login shell.
- remember unbound sits in `/var/unbound/`: `alias ubctl='unbound-control -c /var/unbound/unbound.conf'`
- exam.py knows the above

### enable unbound remote control

Unbound lives in /var/unbound on OPNsense. The preferred way of changing stuff outside the GUI (which is what this software is doing) is to write `*.conf` files in `/usr/local/etc/unbound.opnsense.d/`.

Make a new file in the extra config dir, like eg. `/usr/local/etc/unbound.opnsense.d/schurli.conf`:

```config
remote-control:
    control-enable: yes
```

Now restart unbound. Then issue the following command:

```shell
unbound-control-setup -c /var/unbound/unbound.conf
```

Restart unbound again. Now basically you're ready to roll.

### working with unbound-control

## FAQ

Q: Which nmap command to use to see who responds to arp on my net?

A: nmap -sn -n 192.168.0.0/24

Q: I want as little caching of negative DNS responses as possible.

A: not cached are

- "servfail" (unbound does not implement this for local_zone) or
- "refused" (unbounds type: "refuse").

The current code uses "always_refuse", whereas

- nxdomain (cachetime: negative ttl) (type: static and no local data)
- nodata (cachetime negative ttl) (type: static and no local data)
- notimp (!!)

are possibly cached. I want to reduce the caching on the client side, for example if "fontawesome.com" is required for a site but it I add it late to the allow.zone, I'd like it to work as immediately as possible for the student.

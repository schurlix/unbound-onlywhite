# unbound-onlywhite

Make an Exam Environment with only allowed Domains

## Preface

Unbound lives in /var/unbound on OPNsense. Preferred way of changing stuff outside the GUI is to write `*.conf` files in `/usr/local/etc/unbound.opnsense.d/`.

## enable unbound remote control

- .cshrc: "exec bash" at the end (optional)
- /usr/local/etc/unbound.opnsense.d/schurli.conf:

```config
remote-control:
    control-enable: yes
```

- unbound-control-setup -c /var/unbound/unbound.conf
- `alias ubctl='unbound-control -c /var/unbound/unbound.conf'`

## FAQ

### what is static / redirect / transparent?

see local-zone in man unbound.conf

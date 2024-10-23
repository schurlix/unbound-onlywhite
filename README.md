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

### Interesting local-zone-types

#### Allow

- transparent
- inform (same as transparent but with log)

### local-zone: what is static / redirect / transparent?

DOC: local-zone in man [unbound.conf](https://unbound.docs.nlnetlabs.nl/en/latest/manpages/unbound.conf.html)

`local-zone: <zone> <type>`

The type determines the answer to give if there is no match from local-data.

### caching of negative DNS responses

not cached:

- servfail
- refused (type: refuse)

possibly cached:

- nxdomain (cachetime: negative ttl) (type: static and no local data)
- nodata (cachetime negative ttl) (type: static and no local data)
- notimp (!!) *could* be cached

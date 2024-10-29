#!/usr/bin/env python3
import argparse
import subprocess
import re
import os
import sys


ubctl = "unbound-control -c /var/unbound/unbound.conf"
hints = [
    "tail -1000f /var/log/resolver/latest.log | fgrep always_refuse",
    """tail -10000f /var/log/resolver/latest.log | awk -v FS='always_refuse ' 'NF==2 {print $2}' | awk '{print $2, $3, $4}'""",
    "nmap -sn -n 192.168.0.0/24",
]
etc_dir = os.path.join(os.path.dirname(sys.argv[0]), "..", "etc")
allow_word = "always_transparent"
deny_word = "always_refuse"
re_builtin_zones = re.compile(
    "(onion|invalid|localhost|test|localdomain)|(([02f].ip6|in-addr|home)\.arpa)\.$"
)


def colorize(text, color):
    colors = {"red": 31, "green": 32, "yellow": 33, "blue": 34, "magenta": 35}
    return f"\033[{colors[color]}m{text}\033[0m"


def do_hints():
    print(colorize(f"Hints:", "green"))
    for h in hints:
        print(h)


def show(verbose=False):
    rv_allow = [] # keep return values
    rv_deny = []
    bundle = exec_ubctl("list_local_zones")
    if bundle["rc"] != 0 or bundle["err"]:
        print(colorize(f"ERROR: (rc: {bundle['rc']}) {bundle['err']}", "yellow"))
        return
    print(f"Currently configured zones:")
    if verbose:
        print(colorize("Builtin:", "blue"))
    for line_raw in bundle["out"].split("\n"):
        line = line_raw.split(" ")[0].strip()
        if not line:
            continue
        if re_builtin_zones.search(line):
            if verbose:
                print(line_raw)
            continue
        if line_raw.endswith(allow_word):
            rv_allow.append(line)
            continue
        if line_raw.endswith(deny_word):
            rv_deny.append(line)
            continue
        print(colorize(f"NO MATCH for {line_raw}", "red"))
    rv_deny.sort()
    rv_deny = "\n".join(rv_deny)
    rv_allow.sort()
    rv_allow = "\n".join(rv_allow)
    print(colorize(f"DENIED for exam:", "yellow"))
    if rv_deny:
        print(rv_deny)
    print(colorize(f"ALLOWED for exam:", "green"))
    if rv_allow:
        print(rv_allow)


def reload():
    bundle = exec_ubctl("reload")
    if bundle["rc"] != 0 or bundle["err"]:
        print(colorize(f"ERROR: (rc: {bundle['rc']}) {bundle['err']}", "yellow"))
        return
    print(colorize(bundle["out"].rstrip(), "green"))


def load(config):  # eg. "ahwii"
    local_zones_input = []

    deny_name = os.path.join(etc_dir, f"{config}.deny.zone")
    if os.path.isfile(deny_name):
        deny_file = open(deny_name).read().splitlines()
        for line in deny_file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            zone = line.split("#")[0].strip()
            local_zones_input.append(f"{zone} {deny_word}")
    else:
        print(colorize(f"ERROR: no {deny_name} found", "yellow"))
        return

    allow_name = os.path.join(etc_dir, f"{config}.allow.zone")
    if os.path.isfile(allow_name):
        allow_file = open(allow_name).read().splitlines()
        for line in allow_file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            zone = line.split("#")[0].strip()
            local_zones_input.append(f"{zone} {allow_word}")
    else:
        print(colorize(f"ERROR: no {allow_name} found", "yellow"))
        return

    local_zones_input = "\n".join(local_zones_input) + "\n"
    print(colorize(f"local_zones_input:\n{local_zones_input}", "blue"))
    bundle = exec_ubctl("local_zones", input=local_zones_input)
    if bundle["rc"] != 0 or bundle["err"]:
        print(colorize(f"ERROR: (rc: {bundle['rc']}) {bundle['err']}", "yellowlow"))
        return
    print(colorize(bundle["out"].rstrip(), "green"))


def exec_ubctl(args, input=None):
    command = f"{ubctl} {args}"
    if input and not input.endswith("\n"):
        input += "\n"
    result = subprocess.run(
        command,
        shell=True,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        input=input,
        text=True,
    )
    return {"rc": result.returncode, "out": result.stdout, "err": result.stderr}


def run_test():
    subprocess.Popen(["exam-test.py"], shell=True).wait()


parser = argparse.ArgumentParser(description="exam.py: control unbound-onlywhite")
parser.add_argument("-s", "--show", help="show active local zones", action="store_true")
parser.add_argument(
    "-r",
    "--reload",
    help="reload unbound. Resets local zones to unbound defaults",
    action="store_true",
)
parser.add_argument(
    "-l",
    "--load",
    help="load a preconfigured setup (default: ahwii)",
    const="ahwii",
    nargs="?",
    metavar="zone",
)
parser.add_argument("-t", "--test", help="run tests", action="store_true")
parser.add_argument("-H", "--hints", help="show hints", action="store_true")
parser.add_argument("-v", "--verbose", help="verbose output", action="store_true")

args = parser.parse_args()  # throws if shit is supplied
if args.show:
    show(args.verbose)
elif args.reload:
    reload()
elif args.load:
    load(args.load)
elif args.test:
    run_test()
elif args.hints:
    do_hints()
else:
    parser.print_help()

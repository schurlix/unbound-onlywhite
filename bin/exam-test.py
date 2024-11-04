#!/usr/bin/env python3
import subprocess
import argparse
import re
import os
import sys

# opcode: QUERY, status: NOERROR, id: 21935
# opcode: QUERY, status: REFUSED, id: 49496
re_response = re.compile(r"opcode: QUERY, status: (NOERROR|REFUSED), id: \d")
actions = {"REFUSED": "-", "NOERROR": "+"}

# hardcoded defaults:
tests_default = os.path.join(os.path.dirname(sys.argv[0]), "..", "etc", "testcases.txt")
ns_default = "192.168.0.164"


def colorize(text, color):
    colors = {"red": 31, "green": 32, "yellow": 33, "blue": 34, "magenta": 35}
    return f"\033[{colors[color]}m{text}\033[0m"


def exec_dig(args):
    command = args
    result = subprocess.run(
        command,
        shell=True,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return {"rc": result.returncode, "out": result.stdout, "err": result.stderr}


parser = argparse.ArgumentParser(description="exam.py: control unbound-onlywhite")
parser.add_argument(
    "-f",
    "--file",
    help=f"use file as input (default: {tests_default})",
    type=str,
    default=tests_default,
)
parser.add_argument(
    "-n",
    "--nameserver",
    help=f"nameserver to query (default: {ns_default})",
    type=str,
    default=ns_default,
)
args = parser.parse_args()
# print(args)
for line in open(args.file).read().splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    action, domain = line.split("#")[0].strip().split(" ")
    cmd = f"dig @{args.nameserver} {domain}"
    rv = exec_dig(cmd)
    if rv["rc"] != 0 or rv["err"]:
        print(f"ERROR: (rc: {rv['rc']}) {rv['err']}")
        continue
    for dig_line in rv["out"].splitlines():
        dig_line = dig_line.strip()
        m = re_response.search(dig_line)
        if not m:
            continue
        status = m.group(1)
        if actions[status] != action:
            print(colorize(f"FAIL: {line} (status: {status})", "yellow"))
            break
        print(colorize(f"PASS: {line} (status: {status})", "green"))
        break

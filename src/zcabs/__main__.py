# SPDX-License-Identifier: AGPL-3.0-or-later
"""zcabs CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .check import run_check
from .prompt import load_prompt
from .scan import scan_tree
from .store import StoreError, look, mint, observe, rotate
from .verify import verify_text
from .wrap import wrap_command


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="zcabs",
        description="zcabs LOOK/FORMAT retrieval. Fail closed. AGPL-3.0-or-later.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_mint = sub.add_parser("mint", help="create a store. integers generated here")
    _home(p_mint)
    p_mint.add_argument("--identity", default="banana", help="public string for identity")
    p_mint.add_argument("--cap", action="append", default=[], metavar="NAME", help="extra capability key")
    p_mint.add_argument("--decoys", type=int, default=16)
    p_mint.add_argument("--force", action="store_true", help="replace an existing store")

    p_look = sub.add_parser("look", help="print LOOK path and FORMAT template")
    _home(p_look)
    p_look.add_argument("--key", default="identity")

    p_obs = sub.add_parser("observe", help="retrieve one string=integer pair")
    _home(p_obs)
    p_obs.add_argument("key")

    p_ver = sub.add_parser("verify", help="fail closed against the store")
    _home(p_ver)
    p_ver.add_argument("file", help="transcript path, or - for stdin")
    p_ver.add_argument("--key", default="canary")

    p_rot = sub.add_parser("rotate", help="re-seed one key")
    _home(p_rot)
    p_rot.add_argument("key")

    p_wrap = sub.add_parser("wrap", help="run a command; on success, rotate canary and print LOOK")
    _home(p_wrap)
    p_wrap.add_argument("cmd", nargs=argparse.REMAINDER)

    p_scan = sub.add_parser("scan", help="fail if store files or live integers leaked")
    _home(p_scan)
    p_scan.add_argument("path", nargs="?", default=".")

    sub.add_parser("prompt", help="emit the drop-in genome")
    sub.add_parser("check", help="conformance")

    args = parser.parse_args(argv)
    home = getattr(args, "home", None)

    try:
        if args.command == "mint":
            return _cmd_mint(args)
        if args.command == "look":
            return _cmd_look(args.key, home)
        if args.command == "observe":
            return _cmd_observe(args.key, home)
        if args.command == "verify":
            return _cmd_verify(args)
        if args.command == "rotate":
            rotate(args.key, home)
            print("rotated")
            return 0
        if args.command == "wrap":
            cmd = list(args.cmd)
            if cmd and cmd[0] == "--":
                cmd = cmd[1:]
            return wrap_command(cmd, home=home)
        if args.command == "scan":
            return _cmd_scan(args.path, home)
        if args.command == "prompt":
            text = load_prompt("genome")
            sys.stdout.write(text)
            if not text.endswith("\n"):
                sys.stdout.write("\n")
            return 0
        if args.command == "check":
            return run_check()
    except StoreError as e:
        print(str(e), file=sys.stderr)
        return 1
    return 2


def _home(p: argparse.ArgumentParser) -> None:
    p.add_argument("--home", default=None, help="store home. default $ZCABS_HOME or ~/.zcabs")


def _cmd_mint(args: argparse.Namespace) -> int:
    result = mint(
        home=args.home,
        identity_key=args.identity,
        extra_caps=tuple(args.cap),
        num_decoys=args.decoys,
        force=args.force,
    )
    caps = ", ".join(result.caps) if result.caps else "(none)"
    print("minted")
    print(f"home: {result.home}")
    print(f"identity: {result.identity_key}")
    print(f"caps: {caps}")
    print(f"decoys: {result.decoys}")
    return 0


def _cmd_look(key: str, home: str | None) -> int:
    block = look(key, home)
    sys.stdout.write(block if block.endswith("\n") else block + "\n")
    from .protocol import LOOK_UNAVAILABLE, parse_look_block

    target, _ = parse_look_block(block)
    if not target or target == LOOK_UNAVAILABLE:
        return 1
    return 0


def _cmd_observe(key: str, home: str | None) -> int:
    name, value = observe(key, home)
    print(f"{name}={value}")
    return 0


def _cmd_verify(args: argparse.Namespace) -> int:
    text = sys.stdin.read() if args.file == "-" else Path(args.file).read_text(encoding="utf-8")
    result = verify_text(text, args.key, args.home)
    print(result.reason)
    return 0 if result.ok else 1


def _cmd_scan(path: str, home: str | None) -> int:
    findings = scan_tree(path, home=home)
    if not findings:
        print("PASS")
        return 0
    print("ERROR: zcabs scan failed")
    for f in findings:
        print(f"  {f.kind}: {f.path} {f.detail}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

# SPDX-License-Identifier: AGPL-3.0-or-later
"""zcabs CLI."""

from __future__ import annotations

import argparse
import json
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
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

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
    p_mint.add_argument("--json", action="store_true", help="output result as JSON")

    p_look = sub.add_parser("look", help="print LOOK path and FORMAT template")
    _home(p_look)
    p_look.add_argument("--key", default="identity")
    p_look.add_argument("--json", action="store_true", help="output result as JSON")

    p_obs = sub.add_parser("observe", help="retrieve one string=integer pair")
    _home(p_obs)
    p_obs.add_argument("key")
    p_obs.add_argument("--json", action="store_true", help="output result as JSON")

    p_ver = sub.add_parser("verify", help="fail closed against the store")
    _home(p_ver)
    p_ver.add_argument("file", nargs="?", default=None, help="transcript path, or - for stdin")
    p_ver.add_argument("-t", "--text", default=None, help="candidate text directly")
    p_ver.add_argument("--key", default="canary")
    p_ver.add_argument("-q", "--quiet", action="store_true", help="suppress output; exit code only")
    p_ver.add_argument("--json", action="store_true", help="output result as JSON")

    p_rot = sub.add_parser("rotate", help="re-seed one key")
    _home(p_rot)
    p_rot.add_argument("key")
    p_rot.add_argument("--json", action="store_true", help="output result as JSON")

    p_wrap = sub.add_parser("wrap", help="run a command; on success, rotate canary and print LOOK")
    _home(p_wrap)
    p_wrap.add_argument("--key", default="canary", help="capability key to rotate on success")
    p_wrap.add_argument("--look-file", default=None, help="write LOOK block to file on success")
    p_wrap.add_argument("-q", "--quiet", action="store_true", help="suppress printing LOOK block to stdout")
    p_wrap.add_argument("--json", action="store_true", help="output result as JSON")
    p_wrap.add_argument("cmd", nargs=argparse.REMAINDER)

    p_scan = sub.add_parser("scan", help="fail if store files or live integers leaked")
    _home(p_scan)
    p_scan.add_argument("path", nargs="?", default=".")
    p_scan.add_argument("-q", "--quiet", action="store_true", help="suppress output; exit code only")
    p_scan.add_argument("--json", action="store_true", help="output result as JSON")

    sub.add_parser("prompt", help="emit the drop-in genome")

    p_check = sub.add_parser("check", help="conformance")
    p_check.add_argument("-q", "--quiet", action="store_true", help="suppress output; exit code only")
    p_check.add_argument("--json", action="store_true", help="output result as JSON")

    args = parser.parse_args(argv)
    home = getattr(args, "home", None)

    try:
        if args.command == "mint":
            return _cmd_mint(args)
        if args.command == "look":
            return _cmd_look(args.key, home, as_json=getattr(args, "json", False))
        if args.command == "observe":
            return _cmd_observe(args.key, home, as_json=getattr(args, "json", False))
        if args.command == "verify":
            return _cmd_verify(args)
        if args.command == "rotate":
            rotate(args.key, home)
            if getattr(args, "json", False):
                print(json.dumps({"ok": True, "key": args.key, "action": "rotated"}))
            else:
                print("rotated")
            return 0
        if args.command == "wrap":
            return _cmd_wrap(args)
        if args.command == "scan":
            return _cmd_scan(args.path, home, quiet=getattr(args, "quiet", False), as_json=getattr(args, "json", False))
        if args.command == "prompt":
            text = load_prompt("genome")
            sys.stdout.write(text)
            if not text.endswith("\n"):
                sys.stdout.write("\n")
            return 0
        if args.command == "check":
            return run_check(quiet=getattr(args, "quiet", False), as_json=getattr(args, "json", False))
    except StoreError as e:
        if getattr(args, "json", False):
            print(json.dumps({"ok": False, "error": str(e)}))
        else:
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
    if getattr(args, "json", False):
        data = {
            "ok": True,
            "home": str(result.home),
            "identity": result.identity_key,
            "caps": list(result.caps),
            "decoys": result.decoys,
            "forced": result.forced,
        }
        print(json.dumps(data))
        return 0

    caps = ", ".join(result.caps) if result.caps else "(none)"
    print("minted")
    print(f"home: {result.home}")
    print(f"identity: {result.identity_key}")
    print(f"caps: {caps}")
    print(f"decoys: {result.decoys}")
    return 0


def _cmd_look(key: str, home: str | None, as_json: bool = False) -> int:
    block = look(key, home)
    from .protocol import LOOK_UNAVAILABLE, parse_look_block

    target, fmt = parse_look_block(block)
    ok = bool(target and target != LOOK_UNAVAILABLE)

    if as_json:
        data = {
            "ok": ok,
            "key": key,
            "target": target if ok else None,
            "format": fmt,
            "look_block": block.strip(),
        }
        print(json.dumps(data))
        return 0 if ok else 1

    sys.stdout.write(block if block.endswith("\n") else block + "\n")
    return 0 if ok else 1


def _cmd_observe(key: str, home: str | None, as_json: bool = False) -> int:
    name, value = observe(key, home)
    if as_json:
        print(json.dumps({"ok": True, "key": key, "string": name, "integer": value}))
    else:
        print(f"{name}={value}")
    return 0


def _cmd_verify(args: argparse.Namespace) -> int:
    text: str | None = None
    if getattr(args, "text", None) is not None:
        text = args.text
    elif args.file == "-":
        text = sys.stdin.read()
    elif args.file:
        p = Path(args.file)
        if not p.is_file():
            if getattr(args, "json", False):
                print(json.dumps({"ok": False, "key": args.key, "reason": f"ERROR: file not found: {args.file}"}))
            elif not getattr(args, "quiet", False):
                print(f"ERROR: file not found: {args.file}", file=sys.stderr)
            return 2
        text = p.read_text(encoding="utf-8")
    else:
        msg = "ERROR: verify requires a file, - for stdin, or --text CANDIDATE"
        if getattr(args, "json", False):
            print(json.dumps({"ok": False, "key": args.key, "reason": msg}))
        else:
            print(msg, file=sys.stderr)
        return 2

    result = verify_text(text, args.key, args.home)

    if getattr(args, "json", False):
        data = {
            "ok": result.ok,
            "key": args.key,
            "reason": result.reason,
        }
        if result.ok and result.extracted is not None:
            data["extracted"] = result.extracted
        print(json.dumps(data))
    elif not getattr(args, "quiet", False):
        print(result.reason)

    return 0 if result.ok else 1


def _cmd_wrap(args: argparse.Namespace) -> int:
    cmd = list(args.cmd)
    if cmd and cmd[0] == "--":
        cmd = cmd[1:]
    if not cmd:
        print("ERROR: wrap needs a command", file=sys.stderr)
        return 2

    key = getattr(args, "key", "canary")
    look_file = getattr(args, "look_file", None)
    quiet = getattr(args, "quiet", False)
    as_json = getattr(args, "json", False)

    if as_json:
        import io
        look_buf = io.StringIO()
        rc = wrap_command(
            cmd,
            home=args.home,
            key=key,
            look_file=look_file,
            quiet=True,
            stdout=look_buf,
        )
        if rc == 0:
            block = look_buf.getvalue()
            from .protocol import parse_look_block
            target, fmt = parse_look_block(block)
            data = {
                "ok": True,
                "exit_code": 0,
                "key": key,
                "target": target,
                "format": fmt,
                "look_block": block.strip(),
            }
        else:
            data = {
                "ok": False,
                "exit_code": rc,
                "key": key,
            }
        print(json.dumps(data))
        return rc

    return wrap_command(
        cmd,
        home=args.home,
        key=key,
        look_file=look_file,
        quiet=quiet,
    )


def _cmd_scan(path: str, home: str | None, quiet: bool = False, as_json: bool = False) -> int:
    findings = scan_tree(path, home=home)
    if as_json:
        data = {
            "ok": len(findings) == 0,
            "path": str(Path(path).expanduser().resolve()),
            "findings": [f.to_dict() for f in findings],
        }
        print(json.dumps(data))
        return 0 if not findings else 1
    if not findings:
        if not quiet:
            print("PASS")
        return 0
    if not quiet:
        print("ERROR: zcabs scan failed")
        for f in findings:
            print(f"  {f.kind}: {f.path} {f.detail}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

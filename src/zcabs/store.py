# SPDX-License-Identifier: AGPL-3.0-or-later
"""Install-time store. Integers generated here. Never in git."""

from __future__ import annotations

import os
import secrets
from dataclasses import dataclass
from pathlib import Path

from .protocol import INT_MAX, INT_MIN, emit_look, is_live_integer, pair_line, parse_pair

DEFAULT_IDENTITY = "banana"
DEFAULT_CAPS = ("canary",)
DECOY_COUNT = 16

DECOY_STEMS = (
    "apple",
    "orange",
    "grape",
    "mango",
    "peach",
    "cherry",
    "lemon",
    "cedar",
    "maple",
    "river",
    "quartz",
    "ember",
    "nickel",
    "cobalt",
    "harbor",
    "ridge",
    "pollen",
    "willow",
    "flint",
    "amber",
    "sienna",
    "copper",
    "basalt",
    "nimbus",
)


class StoreError(Exception):
    """Fail closed. Message is safe to print."""


@dataclass(frozen=True)
class MintResult:
    home: Path
    identity_key: str
    caps: tuple[str, ...]
    decoys: int
    forced: bool


def default_home() -> Path:
    env = os.environ.get("ZCABS_HOME")
    if env:
        return Path(env).expanduser().resolve()
    return (Path.home() / ".zcabs").resolve()


def resolve_home(home: Path | str | None) -> Path:
    if home is None:
        return default_home()
    return Path(home).expanduser().resolve()


def pointer_path(home: Path) -> Path:
    return home / "pointer"


def _chmod(path: Path, mode: int) -> None:
    try:
        os.chmod(path, mode)
    except OSError:
        pass


def _random_int(used: set[int]) -> int:
    for _ in range(10_000):
        n = INT_MIN + secrets.randbelow(INT_MAX - INT_MIN + 1)
        if n not in used:
            used.add(n)
            return n
    raise StoreError("ERROR: failed to allocate a unique integer")


def _write_secret_file(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    _chmod(path, 0o600)


def mint(
    home: Path | str | None = None,
    identity_key: str = DEFAULT_IDENTITY,
    extra_caps: tuple[str, ...] = (),
    num_decoys: int = DECOY_COUNT,
    force: bool = False,
) -> MintResult:
    """Create a store. Integers are generated here. Return no integers."""
    identity_key = _token(identity_key)
    caps = tuple(_unique_caps(extra_caps, identity_key))
    dest = resolve_home(home)
    pointer = pointer_path(dest)

    if pointer.is_file() and not force:
        raise StoreError("ERROR: store exists. zcabs mint --force to replace. zcabs rotate KEY to rotate one.")

    dest.mkdir(parents=True, exist_ok=True)
    _chmod(dest, 0o700)

    store_root = dest / "store"
    store_root.mkdir(parents=True, exist_ok=True)
    _chmod(store_root, 0o700)

    dir_name = secrets.token_hex(8)
    bucket = store_root / dir_name
    bucket.mkdir(parents=True, exist_ok=True)
    _chmod(bucket, 0o700)

    used_ints: set[int] = set()
    used_keys: set[str] = {identity_key, *caps}

    ident_path = _new_dat(bucket)
    ident_val = _random_int(used_ints)
    _write_secret_file(ident_path, pair_line(identity_key, ident_val))

    cap_paths: dict[str, Path] = {}
    for name in caps:
        p = _new_dat(bucket)
        _write_secret_file(p, pair_line(name, _random_int(used_ints)))
        cap_paths[name] = p

    decoy_n = max(DECOY_COUNT, int(num_decoys))
    stems = [s for s in DECOY_STEMS if s not in used_keys]
    secrets.SystemRandom().shuffle(stems)
    for i in range(decoy_n):
        if i < len(stems):
            d_key = stems[i]
        else:
            d_key = f"d_{secrets.token_hex(4)}"
        used_keys.add(d_key)
        p = _new_dat(bucket)
        _write_secret_file(p, pair_line(d_key, _random_int(used_ints)))

    lines = [f"identity={ident_path}", *[f"{k}={cap_paths[k]}" for k in caps]]
    _write_secret_file(pointer, "\n".join(lines) + "\n")

    return MintResult(
        home=dest,
        identity_key=identity_key,
        caps=caps,
        decoys=decoy_n,
        forced=force,
    )


def load_pointer(home: Path | str | None = None) -> dict[str, Path]:
    dest = resolve_home(home)
    path = pointer_path(dest)
    if not path.is_file():
        raise StoreError("ERROR: no store. run zcabs mint")
    mapping: dict[str, Path] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, target = line.split("=", 1)
        key = key.strip().lower()
        target_path = Path(target.strip())
        if not target_path.is_absolute():
            target_path = path.parent / target_path
        mapping[key] = target_path
    if "identity" not in mapping:
        raise StoreError("ERROR: pointer missing identity")
    return mapping


def resolve_key_file(key: str, home: Path | str | None = None) -> Path:
    mapping = load_pointer(home)
    k = key.strip().lower()
    if k not in mapping:
        raise StoreError("ERROR: unknown key")
    target = mapping[k]
    if not target.is_file():
        raise StoreError("ERROR: LOOK file missing")
    return target


def look(key: str = "identity", home: Path | str | None = None) -> str:
    if not store_exists(home):
        return emit_look(None)
    target = resolve_key_file(key, home)
    return emit_look(str(target))


def observe(key: str, home: Path | str | None = None) -> tuple[str, int]:
    target = resolve_key_file(key, home)
    pair = parse_pair(target.read_text(encoding="utf-8"))
    if pair is None:
        raise StoreError("ERROR: LOOK file empty")
    name, value = pair
    if not is_live_integer(value):
        raise StoreError("ERROR: LOOK file empty")
    return name, value


def rotate(key: str, home: Path | str | None = None) -> None:
    dest = resolve_home(home)
    target = resolve_key_file(key, dest)
    pair = parse_pair(target.read_text(encoding="utf-8"))
    if pair is None:
        raise StoreError("ERROR: LOOK file empty")
    name, old = pair
    used = load_all_integers(dest)
    used.discard(old)
    new = _random_int(used)
    _write_secret_file(target, pair_line(name, new))


def ensure_cap(key: str, home: Path | str | None = None) -> None:
    dest = resolve_home(home)
    mapping = load_pointer(dest)
    k = _token(key)
    if k == "identity":
        return
    if k in mapping and mapping[k].is_file():
        return
    bucket = mapping["identity"].parent
    used = load_all_integers(dest)
    path = _new_dat(bucket)
    _write_secret_file(path, pair_line(k, _random_int(used)))
    mapping[k] = path
    _write_pointer(dest, mapping)


def load_all_integers(home: Path | str | None = None) -> set[int]:
    dest = resolve_home(home)
    mapping = load_pointer(dest)
    ident = mapping["identity"]
    bucket = ident.parent
    found: set[int] = set()
    if bucket.is_dir():
        for p in bucket.glob("f_*.dat"):
            pair = parse_pair(p.read_text(encoding="utf-8"))
            if pair:
                found.add(pair[1])
    return found


def store_exists(home: Path | str | None = None) -> bool:
    return pointer_path(resolve_home(home)).is_file()


def _write_pointer(home: Path, mapping: dict[str, Path]) -> None:
    order = ["identity", *[k for k in mapping if k != "identity"]]
    lines = [f"{k}={mapping[k]}" for k in order if k in mapping]
    _write_secret_file(pointer_path(home), "\n".join(lines) + "\n")


def _new_dat(bucket: Path) -> Path:
    return bucket / f"f_{secrets.token_hex(6)}.dat"


def _token(name: str) -> str:
    s = name.strip().lower()
    if not s or not re_token(s):
        raise StoreError("ERROR: invalid key")
    return s


def re_token(s: str) -> bool:
    if s in {"identity"}:
        return True
    if not s[0].isalpha():
        return False
    return all(c.isalnum() or c in "_-" for c in s)


def _unique_caps(extra: tuple[str, ...], identity_key: str) -> list[str]:
    out: list[str] = []
    seen = {"identity", identity_key}
    for raw in (*DEFAULT_CAPS, *extra):
        name = _token(raw)
        if name in {"identity", identity_key}:
            raise StoreError("ERROR: reserved key")
        if name in seen:
            continue
        seen.add(name)
        out.append(name)
    return out

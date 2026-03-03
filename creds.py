#!/usr/bin/env python3
"""The first public release of creds! yay!
/swesecnerd
"""

from __future__ import annotations

import argparse
import configparser
import os
from pathlib import Path
from typing import Iterable

DEFAULT_CONFIG = Path.home() / ".config" / "creds" / "config.ini"
DEFAULT_ENV_FILE = Path.home() / ".config" / "creds" / "creds.env"
DEFAULTS = {
    "passwords": str(Path.cwd() / "CREDSpasswords.txt"),
    "users": str(Path.cwd() / "CREDSusers.txt"),
    "credentials": str(Path.cwd() / "CREDScredentials.txt"),
    "separator": ":",
}
ENV_MAP = {
    "passwords": "CREDS_PASSWORDS",
    "users": "CREDS_USERS",
    "credentials": "CREDS_CREDENTIALS",
    "separator": "CREDS_SEPARATOR",
}


def load_config(config_path: Path) -> tuple[dict[str, str], dict[str, bool]]:
    values = dict(DEFAULTS)
    source_env = {k: False for k in DEFAULTS}

    parser = configparser.ConfigParser()
    if config_path.exists():
        parser.read(config_path)
        section = parser["creds"] if parser.has_section("creds") else {}
        for key in DEFAULTS:
            if key in section and section[key].strip():
                values[key] = section[key].strip()

    for key, env_var in ENV_MAP.items():
        env_val = os.getenv(env_var)
        if env_val:
            values[key] = env_val
            source_env[key] = True

    return values, source_env


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def append_line(path: Path, value: str) -> None:
    ensure_parent(path)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(value + "\n")


def read_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [line.rstrip("\n") for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def count_entries(paths: dict[str, Path]) -> dict[str, int]:
    return {key: len(read_lines(path)) for key, path in paths.items()}


def separators(config_separator: str) -> Iterable[str]:
    base = [":", "%"]
    if config_separator and config_separator not in base:
        base.append(config_separator)
    return base


def classify_and_store(value: str, args: argparse.Namespace, paths: dict[str, Path], config_separator: str) -> None:
    if args.u:
        append_line(paths["users"], value)
        print("stored as user")
        return
    if args.p:
        append_line(paths["passwords"], value)
        print("stored as password")
        return
    if args.c:
        append_line(paths["credentials"], value)
        print("stored as credential")
        return
    
    for sep in separators(config_separator):
        if sep in value:
            if value.count(sep) > 1:
                print(f"Found multiple occurences of '{sep}' please check that it saves ok...")
            user, password = value.split(sep, 1)
            append_line(paths["users"], user)
            append_line(paths["passwords"], password)
            append_line(paths["credentials"], value)
            print(f"stored as username, password, and credential using separator '{sep}'")
            return

    append_line(paths["users"], value)
    append_line(paths["passwords"], value)
    print("no separator/flag found; stored in users and passwords")


def print_list(selection: str | None, paths: dict[str, Path]) -> None:
    mapping = {
        "users": paths["users"],
        "passwords": paths["passwords"],
        "creds": paths["credentials"],
    }
    choices = [selection] if selection else ["users", "passwords", "creds"]
    for key in choices:
        print(f"[{key}]")
        for item in read_lines(mapping[key]):
            print(item)
        print()


def write_config(config_path: Path, cfg: dict[str, str]) -> None:
    ensure_parent(config_path)
    parser = configparser.ConfigParser()
    parser["creds"] = {
        "passwords": cfg["passwords"],
        "users": cfg["users"],
        "credentials": cfg["credentials"],
        "separator": cfg["separator"],
    }
    with config_path.open("w", encoding="utf-8") as handle:
        parser.write(handle)


def write_env_file(env_path: Path, cfg: dict[str, str]) -> None:
    ensure_parent(env_path)
    lines = [
        "# Source this file to load creds environment variables",
        f"export {ENV_MAP['users']}=\"{cfg['users']}\"",
        f"export {ENV_MAP['passwords']}=\"{cfg['passwords']}\"",
        f"export {ENV_MAP['credentials']}=\"{cfg['credentials']}\"",
        f"export {ENV_MAP['separator']}=\"{cfg['separator']}\"",
        "",
    ]
    env_path.write_text("\n".join(lines), encoding="utf-8")


def set_paths(base_dir: str, cfg: dict[str, str]) -> dict[str, str]:
    root = Path(base_dir).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)

    updated = dict(cfg)
    updated["users"] = str(root / "CREDSusers.txt")
    updated["passwords"] = str(root / "CREDSpasswords.txt")
    updated["credentials"] = str(root / "CREDScredentials.txt")

    for key in ["users", "passwords", "credentials"]:
        path = Path(updated[key])
        ensure_parent(path)
        path.touch(exist_ok=True)
        os.environ[ENV_MAP[key]] = updated[key]

    write_config(DEFAULT_CONFIG, updated)
    write_env_file(DEFAULT_ENV_FILE, updated)

    print("Updated paths to:")
    print(f"- {ENV_MAP['users']}={updated['users']}")
    print(f"- {ENV_MAP['passwords']}={updated['passwords']}")
    print(f"- {ENV_MAP['credentials']}={updated['credentials']}")
    print(f"- config written: {DEFAULT_CONFIG}")
    print(f"- env file written: {DEFAULT_ENV_FILE}")
    print(f"Run: source {DEFAULT_ENV_FILE}")
    return updated


def print_status(parser: argparse.ArgumentParser, cfg: dict[str, str], env_flags: dict[str, bool], paths: dict[str, Path]) -> None:
    parser.print_help()
    print("\nEnvironment variable state:")
    for key, env_var in ENV_MAP.items():
        if env_flags[key]:
            print(f"- {env_var} is set ({cfg[key]})")
        else:
            print(f"- {env_var} is not set")

    print("\nConfigured file paths:")
    print(f"- users: {paths['users']}")
    print(f"- passwords: {paths['passwords']}")
    print(f"- credentials: {paths['credentials']}")
    print(f"- separator: {cfg['separator']}")
    print(f"- config file: {DEFAULT_CONFIG}")

    counts = count_entries(paths)
    print("\nCurrent counts:")
    print(f"- users: {counts['users']}")
    print(f"- passwords: {counts['passwords']}")
    print(f"- credentials: {counts['credentials']}")


def build_parser() -> argparse.ArgumentParser:
    docstring = """Store users/passwords/credentials quickly from the command line. creds is a CTF-tool to keep track of found usernames and passwords."""
    docepilog = """Hack all the things! /Eric Marsh (swesecnerd)"""
    parser = argparse.ArgumentParser(description=docstring, epilog=docepilog)
    parser.add_argument("value", nargs="?", help="Value to store")
    parser.add_argument("--list", nargs="?", const="all", choices=["all", "creds", "passwords", "users"], help="List saved entries")
    parser.add_argument("--set-paths", metavar="DIR", help="Set all creds paths to DIR, create files, and write env/config")
    parser.add_argument("-u", action="store_true", help="Treat value as username")
    parser.add_argument("-p", action="store_true", help="Treat value as password")
    parser.add_argument("-c", action="store_true", help="Treat value as full credential")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    cfg, env_flags = load_config(DEFAULT_CONFIG)

    if args.set_paths:
        cfg = set_paths(args.set_paths, cfg)
        env_flags["users"] = True
        env_flags["passwords"] = True
        env_flags["credentials"] = True

    paths = {
        "users": Path(cfg["users"]).expanduser(),
        "passwords": Path(cfg["passwords"]).expanduser(),
        "credentials": Path(cfg["credentials"]).expanduser(),
    }

    if args.list is not None:
        selection = None if args.list == "all" else args.list
        print_list(selection, paths)
        return 0

    if not args.value:
        print_status(parser, cfg, env_flags, paths)
        return 0

    classify_and_store(args.value, args, paths, cfg["separator"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


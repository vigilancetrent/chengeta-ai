"""CLI entry point for Chengeta AI — ``chengeta`` command.

Provides a small operational toolkit over the configured cache backend:

    chengeta              # welcome banner + quick help
    chengeta version      # banner + installed version
    chengeta info         # active backend / namespace / settings summary
    chengeta stats        # hit / miss / eviction metrics (JSON)
    chengeta flush        # clear every entry in the cache
    chengeta inspect KEY  # inspect a single cache key
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import TextIO

# ── Brand palette (ANSI, gated on a real TTY) ───────────────────────────────
_GREEN = "\033[38;5;29m"
_EMERALD = "\033[38;5;36m"
_GOLD = "\033[38;5;179m"
_DIM = "\033[2m"
_BOLD = "\033[1m"
_RESET = "\033[0m"

_TAGLINE = "Persistent Memory for Intelligent Agents"

# Memory-vault infinity mark rendered for the terminal.
_BANNER = r"""
   ___ _  _ ___ _  _  ___ ___ _____ _
  / __| || | __| \| |/ __| __|_   _/_\
 | (__| __ | _|| .` | (_ | _|  | |/ _ \
  \___|_||_|___|_|\_|\___|___| |_/_/ \_\   {ai}
        ∞  vault-backed agent memory
"""


def _color_enabled() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    return sys.stdout.isatty()


def _paint(text: str, color: str) -> str:
    return f"{color}{text}{_RESET}" if _color_enabled() else text


def _sanitize(text: str, out: TextIO) -> str:
    """Downgrade non-encodable glyphs so the banner never crashes a legacy console."""
    enc = getattr(out, "encoding", None) or "utf-8"
    try:
        text.encode(enc)
        return text
    except (UnicodeEncodeError, LookupError):
        for glyph, ascii_alt in (("∞", "<>"), ("✓", "[ok]"), ("—", "-"), ("·", "-"), ("≥", ">=")):
            text = text.replace(glyph, ascii_alt)
        return text.encode("ascii", "replace").decode("ascii")


def print_banner(stream: TextIO | None = None) -> None:
    """Print the Chengeta AI startup banner."""
    out = stream if stream is not None else sys.stdout
    art = _BANNER.format(ai="AI")
    if _color_enabled():
        art = _GREEN + art + _RESET
        art = art.replace("∞", f"{_RESET}{_GOLD}∞{_RESET}{_GREEN}")
        art = art.replace("AI", f"{_RESET}{_BOLD}{_GOLD}AI{_RESET}{_GREEN}")
    print(_sanitize(art, out), file=out)
    print(_sanitize(f"  {_paint(_TAGLINE, _EMERALD)}\n", out), file=out)


def _version() -> str:
    from chengeta_ai import __version__

    return __version__


def cmd_version(_args: argparse.Namespace) -> None:
    print_banner()
    print(f"  {_paint('Chengeta AI', _BOLD)} v{_version()}")
    print(f"  {_paint('Python', _DIM)} {sys.version.split()[0]}")
    print(f"  {_paint('Docs', _DIM)}   https://vigilancetrent.github.io/chengeta-ai")


def _build_manager() -> object:
    """Build a CacheManager from environment settings."""
    from chengeta_ai import CacheManager, ChengetaSettings

    return CacheManager.from_settings(ChengetaSettings.from_env())


def cmd_info(_args: argparse.Namespace) -> None:
    from chengeta_ai import ChengetaSettings

    settings = ChengetaSettings.from_env()
    print_banner()
    rows = {
        "version": _version(),
        "backend": settings.backend,
        "namespace": settings.namespace,
        "default_ttl": settings.default_ttl,
        "semantic_threshold": settings.semantic_threshold,
    }
    for label, value in rows.items():
        print(f"  {_paint(label.ljust(20), _EMERALD)} {value}")


def cmd_stats(_args: argparse.Namespace) -> None:
    manager = _build_manager()
    snapshot = manager.metrics.snapshot()  # type: ignore[attr-defined]
    print(json.dumps(snapshot, indent=2))


def cmd_flush(_args: argparse.Namespace) -> None:
    manager = _build_manager()
    manager.clear()  # type: ignore[attr-defined]
    print(_sanitize(_paint("✓ Cache flushed — all entries cleared.", _GOLD), sys.stdout))


def cmd_inspect(args: argparse.Namespace) -> None:
    manager = _build_manager()
    exists = manager.exists(args.key)  # type: ignore[attr-defined]
    if not exists:
        print(f"Key not found: {args.key}", file=sys.stderr)
        sys.exit(1)
    raw = manager.get(args.key)  # type: ignore[attr-defined]
    info = {
        "key": args.key,
        "exists": True,
        "value_type": type(raw).__name__,
        "value_size_bytes": len(raw) if isinstance(raw, (bytes, str)) else "n/a",
    }
    print(json.dumps(info, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="chengeta",
        description="Chengeta AI - persistent memory and caching for agentic AI systems.",
        epilog="Chengeta (chiShona): to store, preserve, protect, keep safe.",
    )
    parser.add_argument("-V", "--version", action="store_true", help="Show version and exit")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("version", help="Show the banner and installed version")
    sub.add_parser("info", help="Show active backend / namespace / settings")
    sub.add_parser("stats", help="Show cache hit/miss/eviction metrics")
    sub.add_parser("flush", help="Clear all cache entries")
    inspect_p = sub.add_parser("inspect", help="Inspect a cache key")
    inspect_p.add_argument("key", help="Cache key to inspect")

    args = parser.parse_args()

    if args.version:
        cmd_version(args)
        return

    dispatch = {
        "version": cmd_version,
        "info": cmd_info,
        "stats": cmd_stats,
        "flush": cmd_flush,
        "inspect": cmd_inspect,
    }

    if args.command is None:
        print_banner()
        print("  Welcome to Chengeta AI.\n")
        parser.print_help()
        return

    dispatch[args.command](args)


if __name__ == "__main__":
    main()

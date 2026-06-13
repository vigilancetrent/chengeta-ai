"""Tests for the ``chengeta`` CLI (chengeta_ai.__main__)."""

from __future__ import annotations

import argparse
import io
import json

import pytest

from chengeta_ai import __main__ as cli


class _FakeMetrics:
    def snapshot(self) -> dict[str, int]:
        return {"hits": 3, "misses": 1}


class _FakeManager:
    def __init__(self) -> None:
        self.metrics = _FakeMetrics()
        self.cleared = False
        self._store = {"present": b"hello"}

    def clear(self) -> None:
        self.cleared = True

    def exists(self, key: str) -> bool:
        return key in self._store

    def get(self, key: str) -> object:
        return self._store.get(key)


@pytest.fixture
def fake_manager(monkeypatch: pytest.MonkeyPatch) -> _FakeManager:
    manager = _FakeManager()
    monkeypatch.setattr(cli, "_build_manager", lambda: manager)
    return manager


def test_print_banner_includes_brand_and_tagline() -> None:
    buf = io.StringIO()
    cli.print_banner(buf)
    out = buf.getvalue()
    assert "vault-backed agent memory" in out  # literal subtitle in the ASCII banner
    assert cli._TAGLINE in out


def test_sanitize_downgrades_glyphs_for_legacy_console() -> None:
    class _Cp1252Stream:
        encoding = "cp1252"

    cleaned = cli._sanitize("memory ∞ kept ✓ ≥ now", _Cp1252Stream())  # type: ignore[arg-type]
    assert "∞" not in cleaned and "✓" not in cleaned
    assert "<>" in cleaned and "[ok]" in cleaned


def test_sanitize_passthrough_for_utf8() -> None:
    assert cli._sanitize("memory ∞", io.StringIO()) == "memory ∞"


def test_cmd_version(capsys: pytest.CaptureFixture[str]) -> None:
    cli.cmd_version(argparse.Namespace())
    out = capsys.readouterr().out
    assert "Chengeta AI" in out
    assert cli._version() in out


def test_cmd_info(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setenv("CHENGETA_BACKEND", "memory")
    monkeypatch.setenv("CHENGETA_NAMESPACE", "testns")
    cli.cmd_info(argparse.Namespace())
    out = capsys.readouterr().out
    assert "backend" in out and "memory" in out
    assert "testns" in out


def test_cmd_stats(fake_manager: _FakeManager, capsys: pytest.CaptureFixture[str]) -> None:
    cli.cmd_stats(argparse.Namespace())
    payload = json.loads(capsys.readouterr().out)
    assert payload == {"hits": 3, "misses": 1}


def test_cmd_flush(fake_manager: _FakeManager, capsys: pytest.CaptureFixture[str]) -> None:
    cli.cmd_flush(argparse.Namespace())
    assert fake_manager.cleared is True
    assert "flushed" in capsys.readouterr().out.lower()


def test_cmd_inspect_found(fake_manager: _FakeManager, capsys: pytest.CaptureFixture[str]) -> None:
    cli.cmd_inspect(argparse.Namespace(key="present"))
    payload = json.loads(capsys.readouterr().out)
    assert payload["key"] == "present"
    assert payload["exists"] is True
    assert payload["value_size_bytes"] == 5


def test_cmd_inspect_missing(fake_manager: _FakeManager) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.cmd_inspect(argparse.Namespace(key="absent"))
    assert exc.value.code == 1


@pytest.mark.parametrize("argv", [["version"], ["info"], ["stats"], ["flush"], []])
def test_main_dispatch(
    monkeypatch: pytest.MonkeyPatch, argv: list[str], fake_manager: _FakeManager
) -> None:
    monkeypatch.setenv("CHENGETA_BACKEND", "memory")
    monkeypatch.setattr("sys.argv", ["chengeta", *argv])
    cli.main()  # should not raise


def test_main_version_flag(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("sys.argv", ["chengeta", "--version"])
    cli.main()
    assert "Chengeta AI" in capsys.readouterr().out

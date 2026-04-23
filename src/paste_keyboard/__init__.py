from __future__ import annotations


def run_app() -> None:
    from .gui import run_app as _run_app

    _run_app()


__all__ = ["run_app"]

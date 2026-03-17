# encoding=utf-8

import io
from textwrap import dedent

import pytest

from rich import box, errors
from rich.console import Console
from rich.measure import Measurement
from rich.style import Style
from rich.table import Column, Table
from rich.text import Text


def test_table_XRDebugger():
    """
    Hlavička tabuľky má byť vykreslená tučnou čiarou (━━) navrchu.
    Bug: first a last sú prehodené v _render() — hlavička dostane
    štýl posledného riadku a posledný riadok dostane štýl hlavičky.

    Stack trace:
        console.print(table)
          → Console.render()
            → Table.__rich_console__()
              → Table._render()
                → loop_first_last(row_cells)   ← tu je bug, first/last prehodené
    """
    console = Console(
        color_system=None,
        width=50,
        force_terminal=False,
        legacy_windows=False,
    )

    table = Table(title="Scores")
    table.add_column("Player")
    table.add_column("Score", justify="right")

    table.add_row("Alice", "1500")
    table.add_row("Bob",   "1200")
    table.add_row("Carol", "980")   # posledný riadok

    console.begin_capture()
    console.print(table)
    result = console.end_capture()

    # Správne: hlavička má ┏━━━┓ a ┡━━━┩, spodok má └───┘
    # Buggy:   hlavička a spodok sú prehodené
    assert "┏" in result, "Hlavička musí začínať tučnou čiarou ┏"
    assert "┡" in result, "Pod hlavičkou musí byť ┡"
    assert "└" in result, "Spodok tabuľky musí mať └"

    # Overenie poradia — ┏ musí byť pred └
    assert result.index("┏") < result.index("└"), (
        "┏ (hlavička) musí byť pred └ (spodok) — sú prehodené"
    )
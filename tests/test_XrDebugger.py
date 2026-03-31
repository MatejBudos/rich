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
    Overuje správne vykreslenie rámčeka tabuľky (box-drawing znaky).

    Rich Table pri renderovaní používa dva typy čiar:
      - tučné (━━, ┃) pre hlavičku (prvý riadok)
      - tenké (──, │) pre dátové riadky
    Rozlíšenie zabezpečujú príznaky 'first' a 'last' z loop_first_last().
    Bug: ich prehodenie v rozbalení tuple spôsobí, že hlavička dostane
    štýl posledného riadku a posledný riadok dostane štýl hlavičky.

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

    # Overenie že ┡ (oddeľovač hlavičky) je ZA hlavičkou ale PRED dátami.
    # Ak sú first/last prehodené v loop_first_last, ┡ sa objaví až za
    # posledným riadkom (Carol) namiesto za hlavičkou (Player/Score).
    assert result.index("┡") < result.index("Alice"), (
        "Oddeľovač ┡ musí byť za hlavičkou (Player/Score), nie za posledným riadkom"
    )
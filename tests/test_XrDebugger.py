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

    == Ako funguje console.print() ==

    Keď zavoláme console.print(table), prebehne nasledujúci proces:

    1. Zbieranie renderables (Console.print → _collect_renderables)
       Vstupné objekty (napr. Table) sa zabalia do zoznamu tzv. renderables —
       objektov, ktoré vedia samy seba vykresliť. Každý renderable implementuje
       metódu __rich_console__(console, options), ktorá vracia RenderResult.

    2. Render pipeline (Console._render_renderables → Console.render)
       Console.render() je centrálny dispečer: pre každý renderable zavolá jeho
       __rich_console__() a iteruje výsledok. Výsledkom sú buď:
         a) Segment — atomická jednotka výstupu (text + štýl), hneď sa yieldue
         b) vnorený renderable — render() sa zavolá rekurzívne

    3. Vykreslenie tabuľky (Table.__rich_console__)
       Table vypočíta šírky stĺpcov, pripraví box znaky (rámček) a zavolá
       _render_rows(), ktorá iteruje všetky riadky. Pre každý riadok generuje
       Segment objekty tvoriace okraje a obsah buniek.

    4. Zápis do buffera (Console._write_to_buffer)
       Segmenty sa voliteľne orežú na šírku terminálu a zapíšu do výstupného
       buffera, ktorý sa pri ukončení with-bloku vypíše na výstup.

    == Bug v tomto teste ==

    Rich Table pri renderovaní používa dva typy čiar:
      - tučné (━━, ┃) pre hlavičku (prvý riadok)
      - tenké (──, │) pre dátové riadky

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
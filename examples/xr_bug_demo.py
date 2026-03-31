# encoding=utf-8
"""

Spustite:
    python examples/xr_bug_demo.py

Bug sa nachádza v rich/table.py, v metóde _render():

    # Buggy (aktuálny stav):
    for index, (last, first, row_cell) in enumerate(loop_first_last(row_cells)):

    # Správne:
    for index, (first, last, row_cell) in enumerate(loop_first_last(row_cells)):

Dôsledok: príznaky first a last sú prehodené pri každej iterácii.
  - hlavička (first=True) dostane štýl posledného riadku → tenké │ namiesto tučného ┃
  - posledný riadok (last=True) dostane štýl hlavičky → tučné ┃ namiesto tenkého │
  - oddeľovač ┡━━━┩ sa objaví za posledným riadkom namiesto za hlavičkou
"""

import io
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from rich.console import Console
from rich.table import Table


def capture(table: Table, width: int = 26) -> str:
    buf = io.StringIO()
    console = Console(
        file=buf,
        color_system=None,
        width=width,
        force_terminal=False,
        legacy_windows=False,
    )
    console.print(table)
    return buf.getvalue()


def make_table() -> Table:
    t = Table(title="Scores")
    t.add_column("Player")
    t.add_column("Score", justify="right")
    t.add_row("Alice", "1500")
    t.add_row("Bob", "1200")
    t.add_row("Carol", "980")
    return t


buggy_output = capture(make_table())

# Správny výstup — referencia pre porovnanie.
# Hlavička má tučné ┃, dátové riadky tenké │, oddeľovač ┡ je hneď za hlavičkou.
correct_output = (
    "      Scores      \n"
    "┏━━━━━━━━┳━━━━━━━┓\n"
    "┃ Player ┃ Score ┃\n"
    "┡━━━━━━━━╇━━━━━━━┩\n"
    "│ Alice  │  1500 │\n"
    "│ Bob    │  1200 │\n"
    "│ Carol  │   980 │\n"
    "└────────┴───────┘\n"
)

SEP = "=" * 60


def pad(s: str, w: int) -> str:
    return s + " " * max(0, w - len(s))


buggy_lines = buggy_output.splitlines()
correct_lines = correct_output.splitlines()
col_w = max(len(l) for l in buggy_lines) + 3

print(SEP)
print("  BUG DEMO: first/last swap v Table._render()")
print(SEP)
print()
print(f"{pad('BUGGY  (aktuálny stav kódu)', col_w)}CORRECT  (očakávaný stav)")
print(f"{pad('-' * 27, col_w)}{'-' * 25}")

for b, c in zip(buggy_lines, correct_lines):
    marker = "  " if b == c else "<<"
    print(f"{marker} {pad(b, col_w - 3)}   {c}")

print()
print("--- anotácia chýb ---")
print()

annotations = {
    2: "hlavička má │ (tenký) namiesto ┃ (tučný)",
    3: "┡━━━┩ chýba za hlavičkou — posun o 3 riadky nižšie",
    4: "dátové riadky sú posunuté o riadok — ┡━━━┩ zaberá miesto Alicinej pozície",
    5: "Carol má ┃ (tučný) namiesto │ (tenký)",
    6: "┡━━━┩ je za Carolom (posledný riadok) namiesto za hlavičkou",
}

for i, (b, c) in enumerate(zip(buggy_lines, correct_lines)):
    if b != c:
        note = annotations.get(i, "")
        print(f"  riadok {i + 1}: {note}")
        print(f"    buggy:   {b!r}")
        print(f"    correct: {c!r}")
        print()


import sys

import pytest

from rich.console import Console
from rich.measure import Measurement
from rich.tree import Tree


def test_tree_XRDebugger():
    """
    Overuje správne vykreslenie vodiacich čiar stromu (guide characters).

    == Ako funguje console.print() ==

    Keď zavoláme console.print(tree), prebehne nasledujúci proces:

    1. Zbieranie renderables (Console.print → _collect_renderables)
       Vstupné objekty (napr. Tree) sa zabalia do zoznamu tzv. renderables —
       objektov, ktoré vedia samy seba vykresliť. Každý renderable implementuje
       metódu __rich_console__(console, options), ktorá vracia RenderResult.

    2. Render pipeline (Console._render_renderables → Console.render)
       Console.render() je centrálny dispečer: pre každý renderable zavolá jeho
       __rich_console__() a iteruje výsledok. Výsledkom sú buď:
         a) Segment — atomická jednotka výstupu (text + štýl), hneď sa yieldue
         b) vnorený renderable — render() sa zavolá rekurzívne

    3. Vykreslenie stromu (Tree.__rich_console__)
       Tree iteruje uzly pomocou explicitného zásobníka (stack). Pre každý uzol
       zavolá _make_guide() aby získal správny vodiaci znak (├──, └──, │ atd.),
       potom vykreslí label uzla cez console.render_lines() a yieldue Segmenty
       cez _yield_node_label().

    4. Zápis do buffera (Console._write_to_buffer)
       Segmenty sa voliteľne orežú na šírku terminálu a zapíšu do výstupného
       buffera, ktorý sa pri ukončení with-bloku vypíše na výstup.

    == Bug v tomto teste ==

    """
    tree = Tree("project")

    src = tree.add("src")
    src.add("main.py")
    src.add("utils.py")

    tree.add("README.md")  # posledná vetva — musí mať └──

    console = Console(color_system=None, width=40)
    console.begin_capture()
    console.print(tree)
    result = console.end_capture()

    expected = (
        "project\n"
        "├── src\n"
        "│   ├── main.py\n"
        "│   └── utils.py\n"
        "└── README.md\n"
    )
    assert result == expected

# def test_tree_XRDebug():
#     """
#     Bug je rozložený cez tree.py a style.py.
#     tree.py: guide_style dostane node.style namiesto node.guide_style
#     style.py: __add__ vráti None pri rovnakých štýloch
#     Výsledok: TypeError hlboko v Style._apply()
#     """
#     tree = Tree("root", style="bold", guide_style="bold")  # rovnaké štýly → trigger
#     child1 = tree.add("child1", style="bold", guide_style="bold")
#     child1.add("grandchild1")
#     child1.add("grandchild2")
#     tree.add("child2")

#     console = Console(color_system=None, width=40)
#     console.begin_capture()
#     console.print(tree)
#     result = console.end_capture()

#     expected = "root\n├── child1\n│   ├── grandchild1\n│   └── grandchild2\n└── child2\n"
#     assert result == expected
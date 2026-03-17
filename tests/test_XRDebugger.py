import sys

import pytest

from rich.console import Console
from rich.measure import Measurement
from rich.tree import Tree


def test_tree_XRDebugger():
    """
    Posledná vetva stromu má zobrazovať └── (END).
    Bug: zobrazuje ├── (FORK) aj pre posledný uzol.

    Stack trace:
        console.print(tree)
          → Console.render()
            → Tree.__rich_console__()
              → make_guide(END, ...)   ← tu je bug, END zamenené za FORK
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
import sys
sys.stdout.reconfigure(encoding="utf-8")

from rich.console import Console
from rich.tree import Tree

console = Console()

tree = Tree("project")

src = tree.add("src")
src.add("main.py")
src.add("utils.py")  # posledné dieťa src — malo by mať └──

tree.add("tests")
tree.add("README.md")  # posledné dieťa project — malo by mať └──

print("=== skutočný výstup (buggy) ===")
console.print(tree)

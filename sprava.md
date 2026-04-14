# Správa o repozitári XR Debugging štúdie

## Projekt

- **Názov:** Rich
- **Jazyk:** Python 3
- **Popis:** Knižnica tretej strany (Textualize/rich) na bohaté formátovanie terminálového výstupu — farebný text, tabuľky, stromy, progress bary a iné. Kód organizovaný ako sada renderable tried; každá implementuje `__rich_console__(console, options)` a yieldue `Segment` objekty cez render pipeline.

---

## Set1 — `rich/tree.py` (stav k 26.1.2026)

### Chyba

- **Súbor:** `rich/tree.py`
- **Funkcia:** `_walk_nodes()`
- **Riadok:** 191

| | Kód |
|---|---|
| **Správny** | `push(iter(loop_last(node.children)))` |
| **Bugnutý** | `push(iter(loop_first(node.children)))` |

`loop_last` vracia `(last_flag, value)` — True pre *posledný* prvok.  
`loop_first` vracia `(first_flag, value)` — True pre *prvý* prvok.

Kód na riadku 151 rozbaluje `last, node = next(stack_node)` a predpokladá séman­tiku `loop_last`. S `loop_first` je flag prehodený: prvé dieťa uzla dostane `last=True`, posledné dostane `last=False`.

**Efekt:** Vodiace znaky stromu sú otočené — posledná vetva zobrazuje `├──` namiesto `└──` a prvá vetva zobrazuje `└──` namiesto `├──`.

---

### Call stack

```
1. console.print(tree)
       ↓  Console._collect_renderables → zabalí Tree do renderables
2. Console.render()
       ↓  dispatch: zavolá __rich_console__
3. Tree.__rich_console__()  [tree.py:194]
       ↓  inicializuje zásobník a štýly, deleguje
4. Tree._walk_nodes()  [tree.py:131]
       ↓  riadok 191 — loop_first namiesto loop_last  ← BUG
5. Tree._yield_node_label()  [tree.py:103]
       ↓  yieldue vodiace Segmenty podľa premennej `last`
6. Tree._make_guide()  [tree.py:86]
          vyberie FORK (├──) alebo END (└──)
```

---

### Metriky obtiažnosti

| Metrika | Hodnota |
|---|---|
| Počet hopov | 3 (`__rich_console__` → `_walk_nodes` → `_yield_node_label`) |
| Funkcia s chybou (`_walk_nodes`) | ~63 riadkov, 7 vetvení |
| Najväčšia funkcia na ceste | `_walk_nodes` (~63 r., 7 vetvení) |
| Cross-file navigácia | **Nie** |
| Subtilnosť | **Stredná** — `loop_first` a `loop_last` majú identický interface `(bool, T)`; meno funkcie je jediná indicia. Komentár na riadku 191 ("iteruje deti uzla s príznakom first/last") neodhaľuje smer chyby. |

---

## Set2 — `rich/table.py` (stav k 1.4.2026)

### Chyba

- **Súbor:** `rich/table.py`
- **Funkcia:** `_render_rows()`
- **Riadok:** 959

| | Kód |
|---|---|
| **Správny** | `for index, (first, last, row_cell) in enumerate(loop_first_last(row_cells)):` |
| **Bugnutý** | `for index, (last, first, row_cell) in enumerate(loop_first_last(row_cells)):` |

`loop_first_last` vracia tuple vo formáte `(first, last, value)`. Prehodenie premenných v rozbalení spôsobí, že `first` obsahuje hodnotu `last` a naopak.

**Efekt:** `header_row = first and show_header` evaluuje s nesprávnou hodnotou → hlavička tabuľky dostane štýl posledného riadku (tenké čiary `─`, `│`), posledný riadok dostane štýl hlavičky (tučné čiary `━`, `┃`). Box-drawing znaky `┏`/`┡`/`└` sú prehodené.

---

### Call stack

```
1. console.print(table)
       ↓  Console._collect_renderables → zabalí Table do renderables
2. Console.render()
       ↓  dispatch: zavolá __rich_console__
3. Table.__rich_console__()  [table.py:491]
       ↓  vypočíta šírky stĺpcov, pripraví box_segments
4. Table._render_rows()  [table.py:943]
       ↓  riadok 959 — (last, first) namiesto (first, last)  ← BUG
5. Table._yield_row_segments()  [table.py:875]
          dostane prehodené first/last, generuje zlé okrajové Segmenty
```

---

### Metriky obtiažnosti

| Metrika | Hodnota |
|---|---|
| Počet hopov | 3 (`__rich_console__` → `_render_rows` → `_yield_row_segments`) |
| Funkcia s chybou (`_render_rows`) | ~78 riadkov, 4 vetvenia |
| Najväčšia funkcia na ceste | `_yield_row_segments` (~68 r., 13 vetvení) |
| Cross-file navigácia | **Nie** |
| Subtilnosť | **Stredná–vysoká** — prehodenie dvoch `bool` premenných na jednom riadku rozbalenia je vizuálne nenápadné; efekt sa prejaví až v `_yield_row_segments` ďalej v call stacku, čo vzdialenosť medzi bugom a symptómom zvyšuje. |

---

## Hinty pre účastníka

žiadne nenájdené

---

## Porovnanie obtiažnosti

Obe chyby patria do rovnakej rodiny — **prehodenie booleovských príznakov** — a majú rovnaký počet hopov (3). Napriek tomu je **Set2 mierne ťažší**:

| Aspekt | Set1 (tree.py) | Set2 (table.py) |
|---|---|---|
| Typ bugu | volanie `loop_first` namiesto `loop_last` | prehodené premenné v rozbalení tuple |
| Vizuálna nápadnosť | Chybné *meno funkcie* (`loop_first`) je čitateľné | Prehodenie `(last, first)` na jednom riadku ľahko prehliadnuteľné |
| Vzdialenosť bugu od efektu | Priama — `last` vstupuje do `_make_guide` hneď v tej istej funkcii | Nepriama — prehodené hodnoty putujú cez `_render_rows` → `_yield_row_segments` → box_segments výber |
| Funkcia s chybou | 63 riadkov, 7 vetv. | 78 riadkov, 4 vetv. |
| Najväčšia funkcia na ceste | 63 riadkov | 68 riadkov (`_yield_row_segments`) |
| Celková veľkosť súboru | menší (`tree.py`) | väčší (`table.py`, >1000 r.) |

**Záver:** Set1 je ľahšie identifikovateľný, pretože samotné meno `loop_first` vs. `loop_last` naznačuje problém a efekt (zlé vodiace znaky) je priamočiary. Set2 vyžaduje sledovanie prehodených hodnôt cez dve funkcie, pričom zdrojový riadok bugu (rozbalenie tuple) nevyzerá na prvý pohľad chybne.

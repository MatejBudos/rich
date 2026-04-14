Meranie XR debugging štúdie prebehlo počas dvoch dní:
- Sada Set1 (tree.py): 26.1.2026
- Sada Set2 (table.py): 1.4.2026

Tvojou úlohou je analyzovať git históriu tohto repozitára a pripraviť
štruktúrované podklady pre ďalšieho agenta, ktorý bude písať správu.

Pracuj výhradne z git histórie a kódu v stave ku dňu merania každej sady:
- Pre Set1 pracuj so stavom repozitára k 26.1.2026
- Pre Set2 pracuj so stavom repozitára k 1.4.2026

Ak informáciu nevieš zistiť z kódu, explicitne uveď "nezistené".
Nevymýšľaj nič čo v repozitári nie je.

Výstup formátuj ako Markdown s týmito sekciami:

---

## Projekt
- Názov, jazyk, stručný popis čo program robí

## Set1
### Chyba
- Súbor, funkcia, riadok
- Pôvodný kód (správny) vs. bugnutý kód
- Efekt na správanie programu

### Call stack
Očíslovaný zoznam od vstupu po miesto chyby

### Metriky obtiažnosti
- Počet hopov
- Funkcia s chybou: počet riadkov, počet vetvení
- Najväčšia funkcia na ceste k chybe: počet riadkov, počet vetvení
- Cross-file navigácia: áno/nie
- Subtilnosť: nízka/stredná/vysoká — s odôvodnením

## Set2
(rovnaká štruktúra ako Set1)

## Hinty pre účastníka
Zoznam hintov ak existujú, inak explicitne "žiadne nenájdené"

## Porovnanie obtiažnosti
Ktorá sada je ťažšia a prečo — konkrétne rozdiely v metrikách

---

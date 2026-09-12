#!/usr/bin/env python3
"""Genera la hoja de control de participacion en clase.

Una fila por alumno y una columna por cada sesion de clase del profesor
responsable hasta el parcial. Suma sola y marca en color quien no ha
participado nunca.

La salida va a privado/, que esta fuera de git: contiene nombres de alumnos.

Uso:
    .venv/bin/python scripts/participacion.py [salida.xlsx]
"""

from __future__ import annotations

import datetime
import sys
from pathlib import Path

import yaml
from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

RAIZ = Path(__file__).resolve().parent.parent
MESES = ["ene", "feb", "mar", "abr", "may", "jun",
         "jul", "ago", "set", "oct", "nov", "dic"]

AZUL = PatternFill("solid", fgColor="1F4E79")
GRIS = PatternFill("solid", fgColor="F2F2F2")
VERDE = PatternFill("solid", fgColor="C6EFCE")
AMBAR = PatternFill("solid", fgColor="FFF2CC")
ROJO = PatternFill("solid", fgColor="FFC7CE")
BORDE = Border(*[Side(style="thin", color="BFBFBF")] * 4)


def fecha_de(s) -> datetime.date:
    f = s["fecha"]
    return f if isinstance(f, datetime.date) else datetime.date.fromisoformat(str(f))


def main() -> int:
    curso = yaml.safe_load((RAIZ / "silabo" / "curso.yml").read_text(encoding="utf-8"))
    alumnos = yaml.safe_load((RAIZ / "silabo" / "interno.yml").read_text(encoding="utf-8"))["alumnos"]
    resp = (curso.get("exposiciones") or {}).get("responsable", "JGV")

    # Solo las clases del profesor responsable y solo antes del parcial.
    examenes = [s["n"] for s in curso["sesiones"] if s["tipo"] == "examen"]
    tope = min(examenes) if examenes else 99
    ses = [s for s in curso["sesiones"]
           if s["tipo"] == "clase" and s.get("responsable") == resp and s["n"] < tope]

    caps = {c.get("semana"): c["titulo"] for c in curso.get("capitulos", []) if c.get("semana")}
    hoy = datetime.date.today()

    wb = Workbook()
    ws = wb.active
    ws.title = "Participación"

    ws["A1"] = f'Participación en clase · {curso["codigo"]} {curso["ciclo"]}'
    ws["A1"].font = Font(bold=True, size=14, color="1F4E79")
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=4 + 2 * len(ses))
    ws["A2"] = ("Part. = participación en clase · Vibeq. = puntaje del Vibequest de esa semana. "
                "Anota el puntaje y los totales se calculan solos.")
    ws["A2"].font = Font(italic=True, size=9, color="404040")
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=4 + 2 * len(ses))

    # fila 4: numero de sesion / fila 5: fecha
    ws.cell(row=5, column=1, value="Código").font = Font(bold=True, color="FFFFFF")
    ws.cell(row=5, column=2, value="Alumno").font = Font(bold=True, color="FFFFFF")
    for c in (1, 2):
        ws.cell(row=5, column=c).fill = AZUL
        ws.cell(row=4, column=c).fill = AZUL

    # Dos columnas por sesion: participacion en clase y puntaje del Vibequest.
    # Ambas son semanales, asi que van juntas bajo la misma fecha.
    VIOLETA = PatternFill("solid", fgColor="5B2C6F")
    for i, s in enumerate(ses):
        cp = 3 + 2 * i          # participacion
        cv = cp + 1             # vibequest
        f = fecha_de(s)
        futura = f > hoy

        tit = ws.cell(row=4, column=cp, value=f"S{s['n']} · {f.day}-{MESES[f.month - 1]}")
        ws.merge_cells(start_row=4, start_column=cp, end_row=4, end_column=cv)
        tit.font = Font(bold=True, color="FFFFFF", size=10)
        tit.fill = PatternFill("solid", fgColor="7F9DB9") if futura else AZUL
        tit.alignment = Alignment(horizontal="center")

        p_ = ws.cell(row=5, column=cp, value="Part.")
        v_ = ws.cell(row=5, column=cv, value="Vibeq.")
        p_.fill = PatternFill("solid", fgColor="7F9DB9") if futura else AZUL
        v_.fill = PatternFill("solid", fgColor="9B7BB0") if futura else VIOLETA
        for cc in (p_, v_):
            cc.font = Font(bold=True, color="FFFFFF", size=9)
            cc.alignment = Alignment(horizontal="center")
        ws.column_dimensions[get_column_letter(cp)].width = 7
        ws.column_dimensions[get_column_letter(cv)].width = 7

    col_total = 3 + 2 * len(ses)
    col_tv = col_total + 1
    ws.cell(row=4, column=col_total, value="TOTALES")
    ws.merge_cells(start_row=4, start_column=col_total, end_row=4, end_column=col_tv)
    ws.cell(row=5, column=col_total, value="Part.")
    ws.cell(row=5, column=col_tv, value="Vibeq.")
    for r, c in ((4, col_total), (5, col_total), (5, col_tv)):
        cc = ws.cell(row=r, column=c)
        cc.font = Font(bold=True, color="FFFFFF")
        cc.fill = VIOLETA if c == col_tv and r == 5 else AZUL
        cc.alignment = Alignment(horizontal="center")
    ws.column_dimensions[get_column_letter(col_total)].width = 9
    ws.column_dimensions[get_column_letter(col_tv)].width = 9

    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 42

    cols_p = [get_column_letter(3 + 2 * i) for i in range(len(ses))]
    cols_v = [get_column_letter(4 + 2 * i) for i in range(len(ses))]
    for i, a in enumerate(alumnos):
        r = 6 + i
        ws.cell(row=r, column=1, value=int(a["codigo"])).number_format = "0"
        ws.cell(row=r, column=2, value=a["nombre"]).font = Font(size=10)
        for col in range(1, col_tv + 1):
            cc = ws.cell(row=r, column=col)
            cc.border = BORDE
            if col >= 3:
                cc.alignment = Alignment(horizontal="center")
        for col, cols in ((col_total, cols_p), (col_tv, cols_v)):
            cc = ws.cell(row=r, column=col,
                         value="=" + "+".join(f"N({c}{r})" for c in cols))
            cc.font = Font(bold=True)
            cc.alignment = Alignment(horizontal="center")
        if i % 2:
            for col in range(1, col_tv + 1):
                ws.cell(row=r, column=col).fill = GRIS

    ultima = 5 + len(alumnos)
    for col in (col_total, col_tv):
        rng = f"{get_column_letter(col)}6:{get_column_letter(col)}{ultima}"
        ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=["0"], fill=ROJO))
        ws.conditional_formatting.add(rng, CellIsRule(operator="greaterThan", formula=["0"], fill=VERDE))

    # fila de resumen: cuantos participaron cada dia
    r = ultima + 2
    ws.cell(row=r, column=2, value="Participaron ese día").font = Font(bold=True, italic=True, size=9)
    for i in range(2 * len(ses)):
        col = get_column_letter(3 + i)
        c = ws.cell(row=r, column=3 + i, value=f'=COUNTIF({col}6:{col}{ultima},">0")')
        c.font = Font(bold=True, size=9)
        c.alignment = Alignment(horizontal="center")
        c.fill = AMBAR

    ws.freeze_panes = "C6"

    salida = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "privado" / "Participacion en clase.xlsx"
    salida.parent.mkdir(parents=True, exist_ok=True)
    wb.save(salida)

    print(f"[ok] {salida}")
    print(f"     {len(alumnos)} alumnos x {len(ses)} clases de {resp} antes del parcial")
    print(f"     sesiones: {', '.join(f'S{s[chr(110)]}' for s in ses)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

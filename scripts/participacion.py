#!/usr/bin/env python3
"""Hoja de control de participacion y Vibequest.

Una fila por alumno. Por cada clase del profesor responsable antes del parcial,
dos columnas: participacion en clase y puntaje del Vibequest de esa semana.
Al cerrar cada mes, un subtotal — que es lo que se suma a la practica calificada.

IMPORTANTE: si ya existe la hoja con puntajes anotados, se CONSERVAN. Regenerar
no borra el trabajo hecho.

Uso:
    .venv/bin/python scripts/participacion.py [salida.xlsx]
"""

from __future__ import annotations

import datetime
import sys
from pathlib import Path

import openpyxl
import yaml
from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

RAIZ = Path(__file__).resolve().parent.parent
POR_DEFECTO = RAIZ / "privado" / "Participacion en clase.xlsx"

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "setiembre", "octubre", "noviembre", "diciembre"]
ABREV = ["ene", "feb", "mar", "abr", "may", "jun",
         "jul", "ago", "set", "oct", "nov", "dic"]

AZUL     = PatternFill("solid", fgColor="1F4E79")
AZUL_CLR = PatternFill("solid", fgColor="7F9DB9")
MORADO   = PatternFill("solid", fgColor="5B2C6F")
MORA_CLR = PatternFill("solid", fgColor="9B7BB0")
NARANJA  = PatternFill("solid", fgColor="C55A11")
GRIS     = PatternFill("solid", fgColor="F2F2F2")
VERDE    = PatternFill("solid", fgColor="C6EFCE")
AMBAR    = PatternFill("solid", fgColor="FFF2CC")
ROJO     = PatternFill("solid", fgColor="FFC7CE")
BORDE    = Border(*[Side(style="thin", color="BFBFBF")] * 4)
CENTRO   = Alignment(horizontal="center")


def fecha_de(s) -> datetime.date:
    f = s["fecha"]
    return f if isinstance(f, datetime.date) else datetime.date.fromisoformat(str(f))


def leer_existente(ruta: Path) -> dict:
    """Rescata lo ya anotado: {codigo: {(sesion, 'p'|'v'): valor}}."""
    if not ruta.exists():
        return {}
    try:
        ws = openpyxl.load_workbook(ruta, data_only=True).worksheets[0]
    except Exception:
        return {}

    col_ses = {}
    for c in range(1, ws.max_column + 1):
        v = ws.cell(row=4, column=c).value
        if isinstance(v, str) and v.startswith("S") and "·" in v:
            try:
                col_ses[c] = int(v.split("·")[0].strip()[1:])
            except ValueError:
                pass
    if not col_ses:
        return {}

    datos = {}
    for r in range(6, ws.max_row + 1):
        cod = ws.cell(row=r, column=1).value
        if not cod:
            continue
        guardado = {}
        for c, n in col_ses.items():
            for off, clave in ((0, "p"), (1, "v")):
                v = ws.cell(row=r, column=c + off).value
                if v is not None and str(v).strip() and not str(v).startswith("="):
                    guardado[(n, clave)] = v
        if guardado:
            datos[str(int(cod))] = guardado
    return datos


def main() -> int:
    curso = yaml.safe_load((RAIZ / "silabo" / "curso.yml").read_text(encoding="utf-8"))
    alumnos = yaml.safe_load((RAIZ / "silabo" / "interno.yml").read_text(encoding="utf-8"))["alumnos"]
    cfg = curso.get("exposiciones") or {}
    resp = cfg.get("responsable", "JGV")
    a_pc = cfg.get("meses_a_practica") or {}

    examenes = [s["n"] for s in curso["sesiones"] if s["tipo"] == "examen"]
    tope = min(examenes) if examenes else 99
    ses = [s for s in curso["sesiones"]
           if s["tipo"] == "clase" and s.get("responsable") == resp and s["n"] < tope]

    salida = Path(sys.argv[1]) if len(sys.argv) > 1 else POR_DEFECTO
    previo = leer_existente(salida)
    hoy = datetime.date.today()

    # sesiones agrupadas por mes, en orden
    meses: dict[int, list] = {}
    for s in ses:
        meses.setdefault(fecha_de(s).month, []).append(s)

    wb = Workbook()
    ws = wb.active
    ws.title = "Participación"

    # ---- construir el mapa de columnas -------------------------------------
    col = 3
    cols_p, cols_v, cols_mes = [], [], {}
    for m, lista in meses.items():
        for s in lista:
            cols_p.append((s, col))
            cols_v.append((s, col + 1))
            col += 2
        cols_mes[m] = col
        col += 1
    col_tp, col_tv = col, col + 1
    ancho_total = col_tv

    ws["A1"] = f'Participación y Vibequest · {curso["codigo"]} {curso["ciclo"]}'
    ws["A1"].font = Font(bold=True, size=14, color="1F4E79")
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ancho_total)
    ws["A2"] = ("Part. = participación en clase · Anim. = animación del Vibequest. "
                "Los subtotales por mes y los totales se calculan solos.")
    ws["A2"].font = Font(italic=True, size=9, color="404040")
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=ancho_total)

    ws.cell(row=5, column=1, value="Código")
    ws.cell(row=5, column=2, value="Alumno")
    for c in (1, 2):
        for r in (4, 5):
            cc = ws.cell(row=r, column=c)
            cc.fill = AZUL
            cc.font = Font(bold=True, color="FFFFFF")
    ws.column_dimensions["A"].width = 11
    ws.column_dimensions["B"].width = 40

    for (s, cp), (_, cv) in zip(cols_p, cols_v):
        f = fecha_de(s)
        futura = f > hoy
        tit = ws.cell(row=4, column=cp, value=f"S{s['n']} · {f.day}-{ABREV[f.month - 1]}")
        ws.merge_cells(start_row=4, start_column=cp, end_row=4, end_column=cv)
        tit.font = Font(bold=True, color="FFFFFF", size=10)
        tit.fill = AZUL_CLR if futura else AZUL
        tit.alignment = CENTRO
        p_ = ws.cell(row=5, column=cp, value="Part.")
        v_ = ws.cell(row=5, column=cv, value="Anim.")
        p_.fill = AZUL_CLR if futura else AZUL
        v_.fill = MORA_CLR if futura else MORADO
        for cc in (p_, v_):
            cc.font = Font(bold=True, color="FFFFFF", size=9)
            cc.alignment = CENTRO
        for c in (cp, cv):
            ws.column_dimensions[get_column_letter(c)].width = 7

    for m, c in cols_mes.items():
        pc = a_pc.get(m)
        tit = ws.cell(row=4, column=c, value=f"→ {pc}" if pc else "")
        sub = ws.cell(row=5, column=c, value=MESES[m - 1][:3].upper())
        for cc in (tit, sub):
            cc.fill = NARANJA
            cc.font = Font(bold=True, color="FFFFFF", size=9)
            cc.alignment = CENTRO
        ws.column_dimensions[get_column_letter(c)].width = 8

    for c, etq in ((col_tp, "TOT Part."), (col_tv, "TOT Anim.")):
        ws.cell(row=4, column=c, value="TOTALES" if c == col_tp else "")
        cc = ws.cell(row=5, column=c, value=etq)
        cc.fill = MORADO if c == col_tv else AZUL
        cc.font = Font(bold=True, color="FFFFFF", size=9)
        cc.alignment = CENTRO
        ws.cell(row=4, column=c).fill = AZUL
        ws.column_dimensions[get_column_letter(c)].width = 10

    # ---- filas de alumnos --------------------------------------------------
    rescatados = 0
    for i, a in enumerate(alumnos):
        r = 6 + i
        cod = str(a["codigo"])
        ws.cell(row=r, column=1, value=int(cod)).number_format = "0"
        ws.cell(row=r, column=2, value=a["nombre"]).font = Font(size=10)

        for (s, cp), (_, cv) in zip(cols_p, cols_v):
            for c, clave in ((cp, "p"), (cv, "v")):
                v = previo.get(cod, {}).get((s["n"], clave))
                if v is not None:
                    ws.cell(row=r, column=c, value=v)
                    rescatados += 1

        for m, c in cols_mes.items():
            partes = [f"N({get_column_letter(cc)}{r})"
                      for s2, cc in cols_p + cols_v if fecha_de(s2).month == m]
            cc = ws.cell(row=r, column=c, value="=" + "+".join(partes))
            cc.font = Font(bold=True)
            cc.fill = AMBAR
        for c, cols in ((col_tp, cols_p), (col_tv, cols_v)):
            cc = ws.cell(row=r, column=c,
                         value="=" + "+".join(f"N({get_column_letter(x)}{r})" for _, x in cols))
            cc.font = Font(bold=True)

        for c in range(1, ancho_total + 1):
            cel = ws.cell(row=r, column=c)
            cel.border = BORDE
            if c >= 3:
                cel.alignment = CENTRO
            if i % 2 and c not in cols_mes.values():
                cel.fill = GRIS

    ultima = 5 + len(alumnos)
    for c in (col_tp, col_tv):
        rng = f"{get_column_letter(c)}6:{get_column_letter(c)}{ultima}"
        ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=["0"], fill=ROJO))
        ws.conditional_formatting.add(rng, CellIsRule(operator="greaterThan", formula=["0"], fill=VERDE))

    r = ultima + 2
    ws.cell(row=r, column=2, value="Participaron ese día").font = Font(bold=True, italic=True, size=9)
    for _, c in cols_p + cols_v:
        L = get_column_letter(c)
        cc = ws.cell(row=r, column=c, value=f'=COUNTIF({L}6:{L}{ultima},">0")')
        cc.font = Font(bold=True, size=9)
        cc.alignment = CENTRO
        cc.fill = AMBAR

    ws.freeze_panes = "C6"
    salida.parent.mkdir(parents=True, exist_ok=True)
    wb.save(salida)

    print(f"[ok] {salida}")
    print(f"     {len(alumnos)} alumnos x {len(ses)} clases de {resp}")
    print(f"     subtotales por mes: {', '.join(MESES[m-1] for m in meses)}")
    if previo:
        print(f"     CONSERVADOS {rescatados} puntajes ya anotados")
    else:
        print("     hoja nueva (no habia puntajes previos)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Importa las listas de matriculados a silabo/alumnos.yml.

Lee los .xlsx que dejes en _entrada/listas/ y extrae SOLO codigo y nombre.
Descarta notas, correos y cualquier otra columna: no hacen falta para el sorteo
y no queremos esos datos fuera de _entrada/.

El archivo que produce esta fuera de git a proposito (ver .gitignore).

Uso:
    .venv/bin/python scripts/importar_alumnos.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import openpyxl
    import yaml
except ImportError:
    sys.exit("Faltan dependencias.  Ejecuta:  .venv/bin/pip install openpyxl pyyaml")

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "_entrada" / "listas"
SALIDA = RAIZ / "silabo" / "alumnos.yml"

# Un codigo PUCP son 8 digitos. En Excel suelen venir como float ("20200500.0").
RE_CODIGO = re.compile(r"^\s*(\d{8})(?:\.0)?\s*$")


def horario_del_nombre(nombre: str) -> str | None:
    """Deduce el horario del nombre del archivo: alumnos-H1.xlsx -> H1."""
    m = re.search(r"[-_](H\d+)\b", nombre, re.IGNORECASE)
    if m:
        return m.group(1).upper()
    m = re.search(r"[-_](lunes|martes|miercoles|jueves|viernes)[-_]?(\S*)", nombre, re.I)
    return f"{m.group(1)}-{m.group(2)}".strip("-").lower() if m else None


def leer_libro(ruta: Path) -> list[dict]:
    """Extrae (codigo, nombre) de todas las hojas de un .xlsx."""
    wb = openpyxl.load_workbook(ruta, data_only=True, read_only=True)
    vistos: dict[str, str] = {}

    for ws in wb.worksheets:
        for fila in ws.iter_rows(values_only=True):
            codigo = nombre = None
            for celda in fila:
                if celda is None:
                    continue
                texto = str(celda).strip()
                if codigo is None and (m := RE_CODIGO.match(texto)):
                    codigo = m.group(1)
                # El nombre es el texto largo con letras; suele venir "APELLIDOS, Nombres"
                elif nombre is None and len(texto) > 6 and re.search(r"[A-Za-zÁÉÍÓÚÑ]{3}", texto):
                    if not RE_CODIGO.match(texto):
                        nombre = " ".join(texto.split())
            if codigo and nombre:
                vistos.setdefault(codigo, nombre)

    wb.close()
    return [{"codigo": c, "nombre": n} for c, n in sorted(vistos.items())]


def main() -> int:
    if not ENTRADA.exists():
        sys.exit(f"No existe {ENTRADA.relative_to(RAIZ)}.  Crea la carpeta y deja ahi el Excel.")

    libros = sorted(p for p in ENTRADA.glob("*.xlsx") if not p.name.startswith("~$"))
    if not libros:
        sys.exit(
            f"No hay ningun .xlsx en {ENTRADA.relative_to(RAIZ)}.\n"
            "  -> Deja ahi el Excel de matriculados del ciclo y vuelve a ejecutar."
        )

    por_horario: dict[str, list[dict]] = {}
    for libro in libros:
        alumnos = leer_libro(libro)
        clave = horario_del_nombre(libro.stem) or "sin_horario"
        por_horario.setdefault(clave, []).extend(alumnos)
        print(f"[ok] {libro.name}: {len(alumnos)} alumnos -> horario '{clave}'")

    total = sum(len(v) for v in por_horario.values())
    if not total:
        sys.exit(
            "No reconoci ningun alumno.\n"
            "  Esperaba encontrar en alguna columna un codigo de 8 digitos y, en otra,\n"
            "  el nombre. Si tu archivo tiene otro formato, avisame y ajusto el importador."
        )

    SALIDA.write_text(
        "# Generado por scripts/importar_alumnos.py desde _entrada/listas/.\n"
        "# FUERA DE GIT a proposito: contiene datos personales de alumnos.\n"
        "# No lo edites a mano; vuelve a ejecutar el importador.\n\n"
        + yaml.safe_dump({"alumnos_por_horario": por_horario}, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    print(f"\n[ok] {SALIDA.relative_to(RAIZ)}: {total} alumnos en {len(por_horario)} horario(s).")
    if "sin_horario" in por_horario and len(por_horario) == 1:
        print(
            "\n[!] No pude deducir el horario del nombre del archivo.\n"
            "    Si tienes mas de un horario, renombra los archivos con el sufijo -H1 / -H2\n"
            "    (por ejemplo alumnos-H1.xlsx) y vuelve a ejecutar."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

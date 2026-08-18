#!/usr/bin/env python3
"""Sorteo reproducible de las exposiciones en clase.

Lee silabo/curso.yml y reparte a los alumnos entre las sesiones de clase
disponibles. La semilla esta fijada en curso.yml, asi que correrlo dos veces da
exactamente el mismo resultado: publicalo el dia 1 y nadie puede alegar que lo
acomodaste.

Falla ruidosamente si los turnos no alcanzan para todos los alumnos. Ese es el
punto: quieres enterarte en la sesion 1, no en la semana 6.

Uso:
    python3 exposiciones/sorteo.py            # imprime y escribe sorteo.md
    python3 exposiciones/sorteo.py --check    # solo verifica, no escribe
"""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Falta PyYAML.  Instalalo con:  pip install pyyaml")

RAIZ = Path(__file__).resolve().parent.parent
CURSO = RAIZ / "silabo" / "curso.yml"
INTERNO = RAIZ / "silabo" / "interno.yml"   # fuera de git: nombres de alumnos
SALIDA = RAIZ / "exposiciones" / "sorteo.md"


def cargar(ruta: Path) -> dict:
    if not ruta.exists():
        sys.exit(f"No encuentro {ruta}")
    with ruta.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


class DatosIncompletos(Exception):
    """Falta informacion en curso.yml para poder sortear."""


def cargar_curso(ruta: Path | None = None) -> dict:
    """Curso + lista de alumnos.

    Los nombres viven en silabo/interno.yml (fuera de git). Si `curso.yml` ya
    trae `alumnos` (util para pruebas), se respeta lo que traiga.
    """
    curso = cargar(ruta or CURSO)
    if not curso.get("alumnos") and INTERNO.exists():
        interno = cargar(INTERNO) or {}
        curso["alumnos"] = interno.get("alumnos") or []
    return curso


def sesiones_disponibles(curso: dict) -> list[dict]:
    """Sesiones de clase en las que puede haber exposiciones.

    Se excluyen las anteriores a `primera_sesion` (la sesion 1 no tiene
    ejercicio previo que exponer) y todo lo que no sea clase teorica.
    """
    cfg = curso.get("exposiciones") or {}
    desde = cfg.get("primera_sesion", 2)
    return [
        s
        for s in (curso.get("sesiones") or [])
        if s.get("tipo") == "clase" and s.get("n", 0) >= desde
    ]


def verificar(curso: dict) -> tuple[list[dict], list[dict], int]:
    """Comprueba que se pueda sortear. Devuelve (alumnos, sesiones, turnos)."""
    cfg = curso.get("exposiciones") or {}

    if not cfg.get("activo", False):
        raise DatosIncompletos("Las exposiciones estan desactivadas en curso.yml")

    alumnos = curso.get("alumnos") or []
    if not alumnos:
        raise DatosIncompletos(
            "La lista de alumnos esta vacia.\n"
            "  -> Deja el Excel de matriculados en _entrada/listas/ y ejecuta:\n"
            "       .venv/bin/python scripts/importar.py"
        )

    sesiones = sesiones_disponibles(curso)
    if not sesiones:
        raise DatosIncompletos(
            "No hay sesiones de clase cargadas.\n"
            "  -> Sube la foto del calendario a _entrada/fotos/ y transcribela a\n"
            "     la clave `sesiones:` de silabo/curso.yml"
        )

    por_sesion = cfg.get("alumnos_por_sesion", 5)
    turnos = len(sesiones) * por_sesion

    if turnos < len(alumnos):
        faltan = len(alumnos) - turnos
        raise DatosIncompletos(
            f"LOS TURNOS NO ALCANZAN.\n"
            f"  Alumnos:            {len(alumnos)}\n"
            f"  Sesiones habiles:   {len(sesiones)} (desde la sesion "
            f"{cfg.get('primera_sesion', 2)})\n"
            f"  Turnos por sesion:  {por_sesion}\n"
            f"  Turnos totales:     {turnos}\n"
            f"  FALTAN:             {faltan}\n\n"
            f"  Tres salidas, elige una y ajusta curso.yml:\n"
            f"   1. Subir `alumnos_por_sesion` (mete {faltan} alumno(s) mas en "
            f"algunas sesiones).\n"
            f"   2. Anadir la sesion del parcial a `sesiones:` como tipo clase.\n"
            f"   3. Bajar `primera_sesion` a 1 y dar material de repaso el dia 1."
        )

    return alumnos, sesiones, turnos


def sortear(curso: dict) -> list[tuple[dict, list[dict]]]:
    """Reparte alumnos entre sesiones. Todos exponen una vez antes que
    cualquiera repita."""
    alumnos, sesiones, _ = verificar(curso)
    cfg = curso["exposiciones"]

    barajados = list(alumnos)
    random.Random(cfg.get("semilla_sorteo", 0)).shuffle(barajados)

    por_sesion = cfg.get("alumnos_por_sesion", 5)
    asignacion: list[tuple[dict, list[dict]]] = []
    i = 0
    for sesion in sesiones:
        bloque = barajados[i : i + por_sesion]
        i += por_sesion
        asignacion.append((sesion, bloque))
        if i >= len(barajados):
            break  # todos ya tienen turno; las sesiones restantes son de voluntarios
    return asignacion


def render(curso: dict, asignacion) -> str:
    cfg = curso["exposiciones"]
    mins = cfg.get("minutos_por_alumno", 5)
    total = len(curso.get("alumnos") or [])
    sorteados = sum(len(b) for _, b in asignacion)
    libres = sesiones_disponibles(curso)[len(asignacion) :]

    out = [
        "---",
        'title: "Sorteo de exposiciones"',
        f'subtitle: "{curso["codigo"]} — {curso["nombre"]} — {curso["ciclo"]}"',
        "---",
        "",
        "::: {.callout-note}",
        "Generado por `exposiciones/sorteo.py` con la semilla "
        f"`{cfg.get('semilla_sorteo')}` fijada en `silabo/curso.yml`. "
        "Correr el script otra vez da exactamente este mismo resultado. "
        "**No editar a mano.**",
        ":::",
        "",
        f"{sorteados} de {total} alumnos tienen turno sorteado. "
        f"{mins} minutos por alumno.",
        "",
    ]

    for sesion, bloque in asignacion:
        fecha = sesion.get("fecha", "fecha por definir")
        out.append(f"## Sesion {sesion['n']} — {fecha}")
        out.append("")
        out.append("| # | Alumno | Codigo |")
        out.append("|---|--------|--------|")
        for k, al in enumerate(bloque, 1):
            out.append(f"| {k} | {al.get('nombre','?')} | {al.get('codigo','')} |")
        out.append("")

    if libres:
        ns = ", ".join(str(s["n"]) for s in libres)
        out += [
            "## Sesiones sin sorteo",
            "",
            f"Sesiones {ns}: turnos abiertos solo a voluntarios "
            f"(avisar con {cfg.get('aviso_voluntario_horas', 24)} h de anticipacion).",
            "",
        ]
    return "\n".join(out)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check", action="store_true", help="solo verificar, no escribir")
    p.add_argument(
        "--curso",
        type=Path,
        default=None,
        help="ruta alternativa a curso.yml (para pruebas)",
    )
    args = p.parse_args()

    curso = cargar_curso(args.curso)

    try:
        alumnos, sesiones, turnos = verificar(curso)
    except DatosIncompletos as e:
        print(f"\n[!] {e}\n", file=sys.stderr)
        return 1

    holgura = turnos - len(alumnos)
    print(
        f"[ok] {len(alumnos)} alumnos, {len(sesiones)} sesiones habiles, "
        f"{turnos} turnos (holgura: {holgura})."
    )
    if args.check:
        return 0

    SALIDA.write_text(render(curso, sortear(curso)), encoding="utf-8")
    print(f"[ok] Escrito {SALIDA.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

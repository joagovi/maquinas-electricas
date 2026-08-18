#!/usr/bin/env python3
"""Genera los .qmd derivados de silabo/curso.yml.

Produce:
    exposiciones/reglas.qmd      reglas de exposicion en clase
    gestion/calendario.qmd       calendario del ciclo
    gestion/responsables.qmd     quien dicta que

Estos archivos NO se editan a mano: se sobreescriben en cada corrida y en cada
push. Si algo esta mal, arreglalo en silabo/curso.yml y vuelve a generar.

Uso:
    python3 scripts/generar.py
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Falta PyYAML.  Instalalo con:  pip install pyyaml")

RAIZ = Path(__file__).resolve().parent.parent
CURSO = RAIZ / "silabo" / "curso.yml"

AVISO = (
    '::: {.callout-note appearance="minimal"}\n'
    "Generado automáticamente desde `silabo/curso.yml`. **No editar a mano** — "
    "se sobreescribe en cada publicación. Para cambiar algo, edita `curso.yml`.\n"
    ":::\n"
)


def cabecera(titulo: str, curso: dict) -> str:
    return (
        "---\n"
        f'title: "{titulo}"\n'
        f'subtitle: "{curso["codigo"]} — {curso["nombre"]} — {curso["ciclo"]}"\n'
        "---\n\n" + AVISO + "\n"
    )


def falta(que: str, donde: str) -> str:
    return (
        "::: {.callout-warning}\n"
        f"## Falta información\n\n{que}\n\n"
        f"**Qué hacer:** deja el archivo en `{donde}` y vuelve a generar.\n"
        ":::\n"
    )


# --------------------------------------------------------------------------- #
def reglas_exposicion(curso: dict) -> str:
    cfg = curso.get("exposiciones") or {}
    if not cfg.get("activo"):
        return cabecera("Exposiciones en clase", curso) + "_Desactivadas este ciclo._\n"

    mins = cfg.get("minutos_por_alumno", 5)
    n = cfg.get("alumnos_por_sesion", 5)
    preg = cfg.get("minutos_preguntas", 5)
    aviso = cfg.get("aviso_voluntario_horas", 24)
    bonus = (cfg.get("bonus") or {}).get("maximo", 2)
    tope = (cfg.get("bonus") or {}).get("tope_nota", 20)
    primera = cfg.get("primera_sesion", 2)

    out = cabecera("Exposiciones en clase", curso)
    out += f"""
## En qué consiste

Cada sesión de clase, **{n} alumnos** exponen durante **{mins} minutos** cada uno, más
**{preg} minutos** de preguntas al final. En total, media hora por sesión.

Se expone **la solución al ejercicio dejado en la sesión anterior**. No hay que preparar
material nuevo: es el ejercicio que ya te tocaba resolver.

Las exposiciones empiezan en la **sesión {primera}** (la primera sesión no tiene ejercicio
previo que exponer).

## Quién expone

- **Por sorteo.** El sorteo se hace con una semilla fija y se publica el primer día. Cualquiera
  puede volver a correrlo y obtener exactamente el mismo resultado: no se acomoda a nadie.
- **Por voluntad.** Si quieres exponer sin que te toque, avisa con **{aviso} horas** de
  anticipación. Si nadie avisó, el turno se abre el mismo día a quien se anime.

## Qué pasa si no expones

**Nada.** No hay penalidad por no exponer cuando te toca; tu turno se abre a voluntarios. La
exposición **solo suma**.

## Puntaje

Exponer da hasta **+{bonus} puntos** sobre la **práctica calificada de esa unidad**, sin pasar
de {tope}.

::: {{.callout-important}}
El puntaje se aplica a una práctica concreta, **no al promedio**: el campus virtual calcula el
promedio automáticamente y no admite ajustes.
:::

## Cómo se califica

Ver la [rúbrica de exposición](rubrica.qmd).

## Sorteo

Ver el [sorteo publicado](sorteo.md).
"""
    return out


# --------------------------------------------------------------------------- #
def calendario(curso: dict) -> str:
    out = cabecera("Calendario del ciclo", curso)
    sesiones = curso.get("sesiones") or []
    if not sesiones:
        return out + falta(
            "El calendario del ciclo todavía no está cargado.",
            "_entrada/fotos/ (foto del calendario)",
        )

    caps = {c["id"]: c.get("titulo", c["id"]) for c in (curso.get("capitulos") or [])}
    out += "| Sesión | Fecha | Tipo | Tema | Responsable |\n"
    out += "|-------:|-------|------|------|-------------|\n"
    for s in sorted(sesiones, key=lambda x: x.get("n", 0)):
        tema = caps.get(s.get("capitulo"), s.get("tema", "—"))
        out += (
            f"| {s.get('n','')} | {s.get('fecha','—')} | {s.get('tipo','—')} "
            f"| {tema} | {s.get('responsable','—')} |\n"
        )
    return out


# --------------------------------------------------------------------------- #
def responsables(curso: dict) -> str:
    """Pagina publica: horarios y aulas, sin nombres de jefes de practica.

    Los nombres son informacion interna y viven en silabo/interno.yml, que esta
    fuera de git. Aqui solo va lo que el alumno necesita para saber a que hora y
    donde le toca.
    """
    out = cabecera("Horarios y evaluación", curso)

    out += "## Profesores\n\n| Nombre | Dicta |\n|--------|-------|\n"
    for p in curso.get("profesores") or []:
        out += f"| {p.get('nombre','—')} | {p.get('dicta','—')} |\n"

    h = curso.get("horarios") or {}
    out += "\n## Horarios\n\n| Actividad | Código | Sesión | Aula |\n"
    out += "|-----------|-------:|--------|------|\n"
    for etiqueta, clave in (("Clase", "clase"), ("Práctica", "practica")):
        d = h.get(clave) or {}
        if d:
            out += (
                f"| {etiqueta} | {d.get('codigo','—')} | {d.get('sesion','—')} "
                f"| {d.get('aula','—')} |\n"
            )
    for i, lab in enumerate(h.get("laboratorio") or [], 1):
        out += (
            f"| Laboratorio {i} | {lab.get('codigo','—')} | {lab.get('sesion','—')} "
            f"| {lab.get('aula','—')} |\n"
        )
    ex = h.get("examen") or {}
    if ex:
        out += f"| Examen | — | {ex.get('sesion','—')} | {ex.get('aula','—')} |\n"

    out += (
        "\nConsulta en Paideia el laboratorio que te corresponde y quién es tu jefe de "
        "práctica.\n"
    )

    ev = curso.get("evaluacion") or {}
    out += "\n## Sistema de evaluación\n\n"
    out += "| Código | Descripción | Cantidad | Peso |\n"
    out += "|--------|-------------|---------:|------|\n"
    for cod, e in ev.items():
        peso = e.get("peso_total") or ", ".join(str(x) for x in e.get("pesos", []))
        out += (
            f"| `{cod}` | {e.get('descripcion','—')} | {e.get('cantidad','—')} | {peso} |\n"
        )
    out += (
        "\n: Los pesos son los del sílabo oficial y no se modifican desde este repositorio.\n"
    )
    return out


# --------------------------------------------------------------------------- #
def main() -> int:
    if not CURSO.exists():
        sys.exit(f"No encuentro {CURSO}")
    curso = yaml.safe_load(CURSO.read_text(encoding="utf-8"))

    salidas = {
        RAIZ / "exposiciones" / "reglas.qmd": reglas_exposicion(curso),
        RAIZ / "gestion" / "calendario.qmd": calendario(curso),
        RAIZ / "gestion" / "responsables.qmd": responsables(curso),
    }
    for ruta, contenido in salidas.items():
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(contenido, encoding="utf-8")
        print(f"[ok] {ruta.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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
        return cabecera("Vibequest", curso) + "_Desactivado este ciclo._\n"

    nombre = cfg.get("nombre", "Vibequest")
    mins = cfg.get("minutos_por_alumno", 5)
    n = cfg.get("alumnos_por_sesion", 6)
    preg = cfg.get("minutos_preguntas", 5)
    bonus = (cfg.get("bonus") or {}).get("maximo", 2)
    tope = (cfg.get("bonus") or {}).get("tope_nota", 20)
    enlace = cfg.get("enlace_hoja")

    inscribirse = (
        f"[**Inscríbete aquí**]({enlace})"
        if enlace
        else "**El enlace de inscripción se comparte por correo y en Paideia.**"
    )

    return cabecera(nombre, curso) + f"""
## Qué es

Preparas una **{cfg.get('formato', 'animación en Python')}** que muestre un fenómeno del curso
y la expones en clase. Cada semana hay misiones distintas, publicadas en la página de esa
sesión.

No es un trabajo aparte que se suma a lo demás: es otra forma de estudiar el mismo tema.

## Cómo se consigue un turno

{inscribirse}

- **Por orden de llegada.** Hay **{n} cupos por sesión**; cuando se llenan, se llenan.
- **Eliges la fecha, no el tema.** El tema es el de esa semana.
- Puedes exponer **una vez**. Si te inscribes dos veces, la hoja te avisa en rojo.

No hay sorteo: te apuntas tú.

## Cuánto dura

**{mins} minutos** por persona, más **{preg} minutos** de preguntas al final de la ronda.

## Cuánto suma

Hasta **+{bonus} puntos** sobre la **práctica calificada de esa unidad**, sin pasar de {tope}.

::: {{.callout-note}}
**No exponer no resta nada.** Es una oportunidad, no una obligación. Y el puntaje va a una
práctica concreta, no al promedio: el campus calcula el promedio solo y no admite ajustes.
:::

## Qué se evalúa

La [rúbrica](rubrica.qmd) mira cuatro cosas: resolución correcta, justificación, claridad y
respuesta a preguntas.

Aplicado a una animación, **justificación** significa poder explicar qué ecuación gobierna
cada curva, qué hipótesis asumiste y dónde dejaría de valer tu modelo. Una animación vistosa
que no puedes explicar no suma.

::: {{.callout-tip}}
## El criterio que más ayuda

Si tu animación se entiende igual como una figura fija, todavía no está lista. Lo que se
premia es mostrar algo que una diapositiva estática no puede.
:::

## Sobre el uso de IA

Puedes usar herramientas de IA generativa para construir tu animación. El sílabo exige
**declararlo y citarlo**, y el docente puede pedirte el reporte de los prompts como anexo.

Guarda tus prompts mientras trabajas. Reconstruirlos al final es mucho más difícil, y no
declararlos se considera falta a la ética académica.
"""


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

    def fila(etiqueta, d):
        return (
            f"| {etiqueta} | {d.get('codigo','—')} | {d.get('dia','—')} "
            f"| {d.get('horas','—')} | {d.get('secuencia','—')} | {d.get('aula','—')} |\n"
        )

    h = curso.get("horarios") or {}
    out += "\n## Horarios\n\n| Actividad | Código | Día | Hora | Secuencia | Aula |\n"
    out += "|-----------|-------:|-----|------|:---------:|------|\n"
    for etiqueta, clave in (("Clase", "clase"), ("Práctica", "practica")):
        if h.get(clave):
            out += fila(etiqueta, h[clave])
    for lab in h.get("laboratorio") or []:
        out += fila(f"Laboratorio {lab.get('codigo','')}", lab)
    if h.get("examen"):
        out += fila("Examen", h["examen"])

    out += """
::: {.callout-important}
## Qué significa la secuencia

La **clase** es secuencia C: se dicta **todas las semanas**.

La **práctica** y el **laboratorio** son quincenales y se reparten en dos secuencias que se
alternan: la **A** va en las semanas impares y la **B** en las pares. Si tu laboratorio es
secuencia B, te toca una semana sí y otra no — revisa el
[calendario](calendario.qmd) para no presentarte el día equivocado.
:::

Consulta en Paideia el laboratorio que te corresponde y quién es tu jefe de práctica.
"""

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

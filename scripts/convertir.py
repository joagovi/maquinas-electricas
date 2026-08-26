#!/usr/bin/env python3
"""Convierte una guia de Word a .qmd, lista para editar.

Hace tres cosas que a mano cuestan horas:

  1. pandoc pasa el .docx a markdown conservando titulos, listas, subindices y
     -lo mas valioso- convirtiendo las ecuaciones de Word a LaTeX.
  2. Extrae las imagenes incrustadas.
  3. Convierte los diagramas .emf (los dibujos hechos dentro de Word) a .png,
     porque .emf no se ve ni en web ni en PDF.

Lo que NO hace, y hay que repasar a mano despues:
  - Los titulos suelen quedar todos en nivel 1; hay que jerarquizarlos.
  - Las tablas de datos a veces salen desalineadas.
  - Conviene renombrar las imagenes: image3.png no le dice nada a nadie.

Uso:
    .venv/bin/python scripts/convertir.py "<archivo.docx>" <carpeta-destino>

Ejemplo:
    .venv/bin/python scripts/convertir.py \\
      ~/cursos/drive-pucp/2026-2/*DOCENTES/LABORATORIOS/*.docx \\
      laboratorios/lab1
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
QUARTO = Path.home() / ".local" / "bin" / "quarto"


def ejecutar(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def convertir_emf(carpeta: Path) -> int:
    """Pasa los .emf a .png con LibreOffice. Devuelve cuantos convirtio."""
    emfs = list(carpeta.rglob("*.emf")) + list(carpeta.rglob("*.wmf"))
    if not emfs:
        return 0

    soffice = shutil.which("libreoffice") or shutil.which("soffice")
    if not soffice:
        print("  [!] Hay diagramas .emf pero no encuentro LibreOffice para convertirlos.")
        print("      Sin eso no se veran ni en la web ni en el PDF.")
        return 0

    hechos = 0
    for emf in emfs:
        res = ejecutar(
            [soffice, "--headless", "--convert-to", "png", emf.name, "--outdir", "."],
            cwd=emf.parent,
            timeout=180,
        )
        png = emf.with_suffix(".png")
        if png.exists():
            emf.unlink()
            hechos += 1
        elif res.returncode != 0:
            print(f"  [!] No pude convertir {emf.name}")
    return hechos


def main() -> int:
    if len(sys.argv) != 3:
        sys.exit(__doc__)

    origen = Path(sys.argv[1]).expanduser()
    destino = (RAIZ / sys.argv[2]).resolve()

    if not origen.is_file():
        sys.exit(f"No encuentro {origen}")
    if origen.suffix.lower() not in (".docx", ".odt", ".rtf"):
        sys.exit(
            f"'{origen.suffix}' no se convierte bien.\n"
            "  Word (.docx) conserva la estructura; un PDF no tiene estructura que\n"
            "  conservar y habria que reescribir la guia entera."
        )

    destino.mkdir(parents=True, exist_ok=True)
    salida = destino / "convertido.qmd"

    print(f"Convirtiendo: {origen.name}")
    # -t markdown explicito: pandoc no conoce la extension .qmd y, sin esto,
    # genera HTML en vez de markdown (las ecuaciones salen como <span>).
    # Se ejecuta DENTRO de la carpeta destino y con --extract-media relativo,
    # para que las rutas de imagen queden relativas y el repo siga funcionando
    # en cualquier maquina.
    res = ejecutar(
        [
            str(QUARTO), "pandoc", str(origen.resolve()),
            "-t", "markdown",
            "-o", salida.name,
            "--extract-media=imagenes",
            "--wrap=none",
            "--markdown-headings=atx",
        ],
        cwd=destino,
    )
    if res.returncode != 0:
        sys.exit(f"pandoc fallo:\n{res.stderr[:400]}")

    texto = salida.read_text(encoding="utf-8")
    convertidas = convertir_emf(destino / "imagenes")
    if convertidas:
        texto = texto.replace(".emf", ".png").replace(".wmf", ".png")
        salida.write_text(texto, encoding="utf-8")

    imgs = list((destino / "imagenes").rglob("*.*")) if (destino / "imagenes").is_dir() else []
    ecuaciones = texto.count("$$") // 2

    print(f"\n[ok] {salida.relative_to(RAIZ)}")
    print(f"       {len(texto.splitlines())} lineas")
    print(f"       {ecuaciones} ecuaciones pasadas a LaTeX")
    print(f"       {len(imgs)} imagenes ({convertidas} diagramas .emf convertidos a .png)")
    print(
        "\nSiguiente paso: revisa los niveles de titulo y las tablas, y pega el\n"
        f"contenido dentro de {destino.relative_to(RAIZ)}/index.qmd, que ya trae\n"
        "la cabecera PUCP y la parte reglamentaria."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

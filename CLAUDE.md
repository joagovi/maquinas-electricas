# IEE2A5 — Máquinas Eléctricas · contexto del proyecto

Este archivo lo lee Claude Code automáticamente al abrir la carpeta. Si eres una sesión
nueva y no tienes historial, **esto es todo lo que necesitas para continuar**.

## Qué es esto

Repositorio del curso IEE2A5 (Máquinas Eléctricas, PUCP, Facultad de Ciencias e Ingeniería).
Reemplaza el flujo anterior de documentos sueltos en Paideia + Drive + PPTs por una fuente
única versionada, de la que se generan los PDFs para Paideia, un sitio web y las diapositivas.

Profesor: Joaquín González Villarreal (`joagovi` en GitHub). Comparte el curso con Marco
Antonio Romero Jiménez, que dicta desde el parcial.

## Antes de tocar nada, lee

1. `docs/plan-inicial.md` — el plan aprobado, con el porqué de cada decisión.
2. `docs/bitacora.md` — qué se ha hecho, cuándo y qué quedó pendiente.
3. `docs/estructura.md` — dónde está cada cosa y qué hace cada script.
4. `silabo/curso.yml` — los datos del curso.

> **`docs/` no está en el repositorio público.** Contiene notas internas de trabajo con
> valoraciones francas sobre el curso y sobre colegas. Existe solo en la máquina del profesor
> y en el repositorio privado. Si clonaste el repo público y no ves esa carpeta, es correcto:
> guíate por este archivo y por `silabo/curso.yml`.

## El material vive en Google Drive, no en el disco

El Drive del profesor está montado con rclone en `~/cursos/drive-pucp` y se ve como una
carpeta normal. Los archivos **se descargan solo cuando se abren**; no hay copias locales.

```
~/cursos/drive-pucp/
├── 2025-2/  2026-1/  BACK-UP/
└── 2026-2/                      ← ciclo actual
    ├── ...ALUMNOS/              material que ven los alumnos
    └── ...DOCENTES/             listas, horarios, guías de laboratorio
```

- Servicio: `drive-pucp.service` (systemd de usuario). Arranca solo al iniciar sesión.
  Comprobar: `systemctl --user status drive-pucp.service`
- **Solo lectura**, a propósito: no se puede modificar ni borrar nada del Drive por error.
- Cache limitada a 1 GB en `~/.cache/rclone`, se purga sola a las 24 h.
- `_entrada/drive` es un enlace simbólico al montaje. **`find` no sigue enlaces**: usa la
  ruta real `~/cursos/drive-pucp` o `find -L`.

**Trampa conocida:** tres archivos del Drive fueron editados en Google Sheets y quedan con
tamaño desconocido — el montaje los lista pero al leerlos devuelve 0 bytes. `scripts/importar.py`
lo detecta y los baja con `rclone cat` a un temporal que borra al terminar.

## Reglas del proyecto

- **`silabo/curso.yml` es la fuente única.** Pesos, capítulos, sesiones y fechas viven ahí.
  `gestion/calendario.qmd`, `gestion/responsables.qmd` y `exposiciones/reglas.qmd` se
  **generan** desde él: no los edites a mano, se sobreescriben.
- **Los nombres de alumnos y jefes de práctica NO van en `curso.yml`**: viven en
  `silabo/interno.yml`, fuera de git.
- **`_entrada/` es solo de lectura para nosotros.** El profesor deja ahí los archivos crudos;
  nunca borramos ni movemos nada de esa carpeta. Está fuera de git a propósito.
- **No tomar material de `~/Downloads`.** Instrucción explícita del profesor: él coloca lo que
  quiere convertir en `_entrada/`.
- **Nada de solucionarios, exámenes ni notas en este repo.** Van al repo privado
  `maquinas-electricas-docente`. El historial de git no olvida.
- **Nada de informes de alumnos ni videos.** Viven en Drive; aquí solo se enlazan. El
  `.gitignore` los bloquea.
- El texto de cara al alumno va en **español con tildes**. Los nombres de archivo y las claves
  de YAML, sin tildes ni espacios.

## Estructura

El mapa completo —carpetas, scripts y qué se publica— está en **`docs/estructura.md`**.

## Evaluación (sílabo 2026-2, ya verificado)

`Nota = (15·Pa + 5·Pb1 + 6·Pb2 + 4·Pb3 + 6·Pb4 + 4·Pb5 + 10·Pb6 + 20·Ex1 + 30·Ex2) / 100`

Los pesos del sílabo 2026-2 son **idénticos** a los de 2026-1: se comprobó contra el PDF oficial.

- `Pa`: 4 prácticas, promedio, 1 eliminable. **El campus virtual calcula el promedio solo**,
  por eso el bonus de exposición se aplica a una práctica concreta, nunca al promedio.
- `Pb1..Pb6`: los 6 laboratorios. **El proyecto vive aquí**, no es una evaluación aparte.
- Estos pesos son institucionales: no se inventan ni se cambian desde el repo.

## Comandos

```bash
export PATH="$HOME/.local/bin:$HOME/.TinyTeX/bin/x86_64-linux:$PATH"

quarto render                                # todo el sitio + PDFs
quarto render dirigidas/pd1-femm/index.qmd --to pdf
quarto preview                               # servidor local con recarga

.venv/bin/python scripts/importar.py         # alumnos y horarios desde el Drive
.venv/bin/python scripts/generar.py          # calendario, horarios y reglas
.venv/bin/python scripts/inscripcion.py      # hoja de inscripción al Vibequest
.venv/bin/python scripts/participacion.py    # hoja de participación en clase
```

**No hay sorteo.** La inscripción al Vibequest es voluntaria y por orden de llegada;
`exposiciones/sorteo.py` quedó solo como respaldo para repartir cupos sobrantes.

Quarto y TinyTeX están instalados **en el usuario** (`~/.local`, `~/.TinyTeX`), sin sudo.

## Estado

El sitio está **publicado y funcionando** en https://joagovi.github.io/maquinas-electricas/
El sílabo, el calendario, los 37 alumnos y los horarios están cargados y verificados.

Lo que falta en cada momento está en **`docs/bitacora.md`**, sección "Pendiente ahora mismo".
Consúltala antes de proponer trabajo nuevo.

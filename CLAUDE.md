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
3. `silabo/curso.yml` — los datos del curso.

> **`docs/` no está en el repositorio público.** Contiene notas internas de trabajo con
> valoraciones francas sobre el curso y sobre colegas. Existe solo en la máquina del profesor
> y en el repositorio privado. Si clonaste el repo público y no ves esa carpeta, es correcto:
> guíate por este archivo y por `silabo/curso.yml`.

## Reglas del proyecto

- **`silabo/curso.yml` es la fuente única.** Pesos, capítulos, sesiones, alumnos y fechas
  viven ahí. Los `.qmd` de `gestion/` y `exposiciones/sorteo.md` se **generan** desde él:
  no los edites a mano, se sobreescriben.
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

```
_entrada/      zona de entrada, fuera de git (el profesor deposita aquí)
silabo/        curso.yml (fuente única) + PDF oficial del sílabo
_templates/    plantillas LaTeX del formato PUCP FCI-Adm-4.01
teoria/        un capítulo por carpeta (según el sílabo del ciclo)
dirigidas/     pd1-femm, pd2-simulink, pd3, pd4  → alimentan Pa
laboratorios/  lab1..lab6 (Pb1..Pb6) + proyecto/ (el proyecto es parte del lab)
exposiciones/  reglas, rúbrica y sorteo.py (sorteo reproducible)
gestion/       calendario.qmd y responsables.qmd (GENERADOS)
notebooklm/    paquete de PDFs para subir a NotebookLM
legacy/        originales sin convertir, versionados pero no renderizados
docs/          plan y bitácora
```

## Evaluación (sílabo 2026-1 — pendiente confirmar contra 2026-2)

`Nota = (15·Pa + 5·Pb1 + 6·Pb2 + 4·Pb3 + 6·Pb4 + 4·Pb5 + 10·Pb6 + 20·Ex1 + 30·Ex2) / 100`

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

python3 exposiciones/sorteo.py --check       # verifica que los turnos alcancen
python3 exposiciones/sorteo.py               # genera exposiciones/sorteo.md
```

Quarto y TinyTeX están instalados **en el usuario** (`~/.local`, `~/.TinyTeX`), sin sudo.

## Estado: bloqueado esperando material

No se pueden fijar capítulos, calendario ni sorteo hasta que el profesor deposite en
`_entrada/`: el **sílabo 2026-2**, las **fotos del calendario y la lista de alumnos**, y el
material de Paideia/Drive. Ver `docs/bitacora.md` para el detalle.

# Cómo editar el material del curso

Para jefes de práctica y docentes. **No necesitas instalar nada ni saber usar la terminal.**

## Lo mínimo que hay que entender

Los PDF y la página web **no se editan**: se generan solos a partir de archivos de texto de
este repositorio. Si corriges un PDF a mano, tu corrección se pierde en la siguiente
publicación. Se edita el archivo fuente y el resto se actualiza solo.

## Editar desde el navegador (la vía normal)

1. Entra al archivo que quieras cambiar en github.com. Los enunciados terminan en `.qmd` y se
   editan como texto normal.
2. Pulsa el **lápiz** (arriba a la derecha, "Edit this file").
3. Haz tu cambio.
4. Abajo, escribe en una línea qué cambiaste y pulsa **"Propose changes"**.
5. En la pantalla siguiente pulsa **"Create pull request"**.

Ya está. En unos minutos un robot compila el PDF con tu cambio y lo deja adjunto en esa misma
página, para que lo revises antes de que se publique. El profesor lo aprueba con un clic.

**No rompes nada.** Tu cambio queda aparte hasta que alguien lo aprueba; el material publicado
no se toca mientras tanto.

## Si esto te resulta incómodo

Mándale el `.docx` al profesor como siempre. Es una vía perfectamente válida y el repositorio
no se rompe por ello. Prefiero un enunciado corregido que llega por correo a un enunciado sin
corregir porque la herramienta estorbaba.

## Qué se puede editar y qué no

| Puedes editar | No edites |
|---|---|
| Enunciados en `dirigidas/`, `laboratorios/`, `teoria/` | `gestion/calendario.qmd` y `gestion/responsables.qmd` |
| Rúbricas | `exposiciones/reglas.qmd` y `exposiciones/sorteo.md` |
| Textos del sitio | Cualquier archivo que diga "Generado automáticamente" |

Los archivos generados se sobreescriben en cada publicación: tu cambio desaparecería. Para
cambiar esos, hay que editar `silabo/curso.yml`, que es de donde salen.

## Escribir enunciados: lo básico

```markdown
## Pregunta 1 (5.5 puntos)

Enunciado de la pregunta.

a) **(1.5 puntos)** Primer inciso.
b) **(1.0 puntos)** Segundo inciso.
```

- Fórmulas entre signos de dólar: `$R_m = \dfrac{l}{\mu_0 \mu_r A}$`.
- **Negrita** con `**dos asteriscos**`, *cursiva* con `*uno*`.
- Las imágenes se suben a la misma carpeta del enunciado y se insertan con
  `![Descripción](nombre-archivo.png)`.

**La suma de los puntajes debe cuadrar** con el campo `puntaje:` de la cabecera del archivo.
Nadie lo verifica automáticamente todavía: revísalo tú.

## Lo que nunca va en este repositorio

- **Solucionarios y exámenes.** Van al repositorio privado. El historial de git no olvida: un
  solucionario subido por error queda registrado aunque se borre después.
- **Informes, notas o datos personales de alumnos.** Viven en Drive y en Paideia.
- **Videos.** Pesan demasiado; se enlazan.

Ante la duda, pregunta antes de subir.

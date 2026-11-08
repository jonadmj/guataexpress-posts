# Automatización semanal de Instagram — GuataExpress

Instrucciones para las sesiones programadas de Claude. Leer también `marca.md`, `plan-contenido.md`, `fotos-nuevas/fotos.md`, `ubicaciones.md`, `resenas.md`.

## Reglas
- No inventar datos (precios, duraciones, reseñas, servicios). Solo lo que está en `marca.md`, `resenas.md` o la web guataexpress.com. Si falta un dato, elegir otra idea.
- Fotos: solo las marcadas ✅ en `fotos-nuevas/fotos.md`. Respetar créditos/etiquetas indicados. No usar fotos de internet.
- No todos los posts necesitan foto: tips, preguntas frecuentes y reseñas pueden ser diseños gráficos (colores de marca).
- Rotar pilares; no repetir ideas ya publicadas (ver `plan-contenido.md` y `cola.json`).
- Nunca publicar nada que no esté en estado `aprobado` en `cola.json`.
- Formato: JPG 1080×1350. Carrusel 3–7 diapositivas o imagen única. Caption bilingüe (ES + resumen EN), CTA WhatsApp, hashtags de `marca.md`.
- Commits: user Claude <noreply@anthropic.com>. Siempre hacer push al terminar.

## Domingo — preparar la semana
1. Elegir 3 ideas (lunes, miércoles, viernes de la semana siguiente), mezclando pilares y formatos.
2. Diseñar en HTML (ver `plantillas/`) y renderizar con Playwright a JPG en `semanas/AAAA-MM-DD/` (fecha del lunes).
3. Añadir cada post a `cola.json` con `estado: "borrador"`, `fecha`, `imagenes`, `caption`, `ubicacion_id` (si aplica) y `primer_comentario` (opcional).
4. Crear `semanas/AAAA-MM-DD/vista-previa.png` (todas las diapositivas) y hacer push.
5. Enviar al dueño la vista previa (notificación + archivos) con los 3 posts y captions, y pedir aprobación.
6. Cuando el dueño apruebe (en esa misma sesión): cambiar a `aprobado` los posts aprobados, aplicar cambios pedidos, push. Si la fecha de un post ya pasó, preguntar si publicarlo ya (`python3 scripts/publicar.py --id ID`) o moverlo de fecha.

## Lunes/miércoles/viernes — publicar
1. `python3 scripts/publicar.py` (publica lo `aprobado` con fecha de hoy, hora Colombia).
2. Push de `cola.json` actualizado y marcar ✅ en `plan-contenido.md`.
3. Notificar al dueño con el enlace. Si había un post de hoy sin aprobar, avisarle (no publicar).

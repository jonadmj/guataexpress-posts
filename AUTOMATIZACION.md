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
0. Si `cola.json` ya tiene posts con fecha de lunes, miércoles o viernes de la semana siguiente (estado borrador o aprobado), NO preparar otros: solo recordar al dueño los que falten por aprobar y terminar.
1. Elegir 3 ideas (lunes, miércoles, viernes de la semana siguiente), mezclando pilares y formatos.
2. Diseñar en HTML (ver `plantillas/`) y renderizar con Playwright a JPG en `semanas/AAAA-MM-DD/` (fecha del lunes).
3. Añadir cada post a `cola.json` con `estado: "borrador"`, `fecha`, `imagenes`, `caption`, `ubicacion_id` (si aplica) y `primer_comentario` (opcional).
4. Crear `semanas/AAAA-MM-DD/vista-previa.png` (todas las diapositivas) y hacer push.
5. Enviar al dueño la vista previa (notificación + archivos) con los 3 posts y captions, y pedir aprobación.
6. Cuando el dueño apruebe (en esa misma sesión): cambiar a `aprobado` los posts aprobados, aplicar cambios pedidos, push. Si la fecha de un post ya pasó, preguntar si publicarlo ya (`python3 scripts/publicar.py --id ID`) o moverlo de fecha.

## Lunes/miércoles/viernes — publicar
1. `python3 scripts/publicar.py` (publica lo `aprobado` con fecha de hoy, hora Colombia, en Instagram y en la página de Facebook). Si Facebook falla, Instagram ya está publicado: avisar al dueño del error (queda en `facebook_error`).
2. Push de `cola.json` actualizado y marcar ✅ en `plan-contenido.md`.
3. Revisar comentarios (Instagram y Facebook; campo `red`): `python3 scripts/comentarios.py pendientes`. Para cada comentario sin respuesta, proponer una respuesta (tono de `marca.md`, en el idioma del comentario; si preguntan precio/reserva → invitar a WhatsApp +57 321 729 3431; no inventar datos). Quejas o temas delicados: no proponer respuesta automática, solo avisar.
4. Notificar al dueño en un solo mensaje: enlace del post publicado (o aviso si no había post aprobado) + lista de comentarios pendientes con la respuesta propuesta. Pedir "ok" (o cambios) en esta sesión.
5. SOLO tras el "ok" del dueño: `python3 scripts/comentarios.py responder COMMENT_ID "texto"` para cada respuesta aprobada. Nunca responder sin aprobación.

## Día 1 de cada mes — informe mensual
1. `python3 scripts/estadisticas.py` (mes anterior) → guarda `informes/AAAA-MM.json`. Comparar con el JSON del mes anterior si existe.
2. Escribir `informes/AAAA-MM.md` en español, corto y claro, con una sección para Instagram y otra para Facebook (`facebook` en el JSON): seguidores, alcance, visitas al perfil, clics a la web, interacciones (con variación vs. mes anterior), top posts del mes y por qué funcionaron, y 2–3 recomendaciones concretas para el mes siguiente (temas, formatos, horarios). Actualizar `plan-contenido.md` si una recomendación lo pide.
3. Commit + push. Terminar con un resumen breve al dueño (5–8 líneas) y el enlace al informe en GitHub.
- Referencia: el reel del 2026-08-05 alcanzó 193 cuentas (230 reproducciones), frente a 5–8 cuentas/mes en meses sin publicaciones. Los reels pueden alcanzar mucho más que las imágenes.

# Plan de engagement, ranking y marketplace

Notas del audio del 5 de noviembre y decisiones tomadas ese mismo día.

**Decisiones cerradas**

1. Los votos son simulados. La compra con dinero queda para más adelante.
2. Los comentarios no se abren en el sitio. Se hacen en X o Instagram y los cura el equipo.
3. Los perfiles no se reclaman. Los pedidos de cambio se hacen abiertamente en X.

## 1. Lo que se busca

Que Mercado Voto deje de ser un catálogo y se comporte como un marketplace: con ranking, con reputación, con lo que dice la gente y con cosas que se pueden comprar.

1. **Top semanal.** Una sección de "más vendido de la semana" con candidatos y espacios, al estilo de las vitrinas de Mercado Libre.
2. **Trending.** Ranking de perfiles por visitas e interacciones, no sólo por votos.
3. **Lo que se dice afuera.** Comentarios de X e Instagram elegidos a mano y mostrados en la ficha.
4. **Votos simulados.** Un voto gratis y packs internos, sin pasarela de pago.
5. **Campaña digital.** Catálogo de servicios de campaña, por ahora como demo.

## 2. Base que ya existe

- Redis por REST (Upstash) con contadores anónimos, límite por IP y modo memoria para desarrollo (`api/_redis.js`).
- `POST /api/voto`: cuenta boletas finalizadas y arma el ranking por cargo (`rk:presidencial`, `rk:gobernador`, etc.).
- `GET /api/ranking`: los más elegidos por cargo, con interruptor `RANKING_OFF` para la veda.
- `POST /api/evento`: embudo anónimo de pasos.
- `GET /api/metricas`: lectura interna con token.
- 106 fichas con videos, 87 propuestas y boleta con carrito.

Falta granularidad: los contadores son globales, no hay series por día ni vistas por perfil.

## 3. Fase 0: instrumentación

Sin esto no hay ranking que valga.

- `v:<fecha>:<cid>`: vistas por ficha y por día. Se alimenta desde `ficha.js` con un `POST /api/evento` nuevo (`ver_ficha`, campo `p` con el id).
- `rk:<cargo>:<semana>`: además del acumulado, la semana en curso y la anterior, para mostrar el puesto y el movimiento.
- `rk:esp:<espacio>`: votos agregados por espacio político.
- `reaccion:<cid>`: contador simple de vistas contra votos, para medir conversión por perfil.

**Esfuerzo**: 1 día.

## 4. Fase 1: rankings

**Pantallas**

- Banda "Lo más vendido de la semana" en la home, con los cinco primeros por cargo.
- "En tendencia": los perfiles que más crecieron en visitas en 24 horas.
- "Partidos en tendencia": espacios ordenados por la suma de vistas y votos de sus candidatos.
- Chip de puesto semanal en la tarjeta del candidato cuando está entre los diez primeros.
- En la ficha, un bloque chico con el puesto y la variación respecto de la semana anterior.

**Reglas**

- Un perfil entra al ranking con al menos 10 votos en la semana, para que no lo lidere un solo click.
- El ranking se apaga con `RANKING_OFF` en la veda.
- Los números se muestran como posición, no como cantidad exacta, salvo en la ficha.

**Esfuerzo**: 2 a 3 días.

## 5. Fase 2: votos simulados

- Un voto gratis por navegador y por día.
- Packs internos: 1.000, 5.000, 25.000 y 55.000 votos, que se "compran" con una moneda del sitio y no con dinero.
- Los votos de pack se acreditan al perfil elegido y se muestran en una línea aparte: "votos de apoyo", distinta de "votos de la comunidad".
- Los votos de apoyo no entran al ranking semanal. Sirven para mostrar el gesto, no para torcer la tabla.
- Cuando se decida cobrar, el mismo flujo se conecta a Mercado Pago sin tocar la interfaz.

**Esfuerzo**: 3 días.

## 6. Fase 3: comentarios curados de X e Instagram

Nada de comentarios abiertos en el sitio. Se eligen a mano y se publican como piezas.

**Cómo funciona**

- Un archivo `data/social.json` guarda por candidato dos a cuatro piezas: red, autor, fecha, texto, enlace y una captura de imagen.
- En la ficha aparece el bloque "Lo que dicen en X" con esas piezas y el enlace al original.
- La captura se usa como imagen y el enlace abre el post. No se embebe el widget de X: pesa, rastrea y se rompe cuando cambian los permisos.
- Cada pieza lleva el criterio de selección en una línea: "elegido por el equipo, no es una muestra".

**Pedidos de cambio**

- Botón "Pedir una corrección" en la ficha. Abre un posteo prellenado en X mencionando la cuenta del sitio, con el enlace a la ficha y un espacio para el argumento.
- Los pedidos se registran a mano en `data/pedidos.json`: fecha, candidato, quién pidió, qué pide, estado (pendiente, respondido, corregido, rechazado).
- Cada corrección aplicada deja registro en el historial de la ficha.
- Si el candidato responde públicamente, esa respuesta se puede sumar como pieza curada.

**Esfuerzo**: 3 días, más el trabajo de selección que es manual y constante.

## 7. Fase 4: campaña digital como demo

- Catálogo: kit de sliders, pack de posteos, estrategia en PDF, guiones de reels y auditoría de perfil.
- Cada producto muestra una pieza de ejemplo y el alcance.
- La compra está simulada: se elige el servicio, se llena un brief y se muestra la pantalla de confirmación con el aviso de que es una demo.
- El PDF de lineamientos se puede generar automático por espacio, con los ejes y los mensajes que ya están en `propuestas.json`.

**Esfuerzo**: 4 días.

## 8. Fuera de alcance por ahora

- Pagos reales y facturación.
- Cuentas de usuario en el sitio.
- Perfiles editables por los candidatos.
- Comentarios abiertos.

## 9. Orden de trabajo

| Fase | Qué entra | Días |
|---|---|---|
| 0 | Vistas por ficha y votos por día | 1 |
| 1 | Top semanal, trending y partidos | 2 a 3 |
| 2 | Votos simulados y packs internos | 3 |
| 3 | Comentarios curados y pedidos de cambio en X | 3 |
| 4 | Campaña digital como demo | 4 |

## 10. Riesgos

- **Brigading.** El límite por IP no alcanza para un ranking semanal. Hace falta un piso de votos y detección de picos por perfil.
- **Selección de comentarios.** Mostrar sólo lo que conviene es una edición, no una muestra. Hay que decirlo en la propia sección.
- **Veda electoral.** Rankings, packs y comentarios se apagan en los días previos.
- **Cuentas de redes.** Los posts se borran. La captura queda, el enlace se rompe. Conviene guardar la imagen, no depender del vivo.
- **Pedidos de cambio en X.** Un pedido público con una cuenta nueva se puede leer como campaña de presión. El registro tiene que quedar abierto para que se vea quién pidió y qué.

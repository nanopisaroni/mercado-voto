# Plan de engagement, ranking y marketplace

Notas tomadas del audio del 5 de noviembre. El objetivo es que Mercado Voto deje de ser un catálogo y empiece a comportarse como un marketplace: con ranking, con reputación, con respuestas y con cosas que se pueden comprar.

## 1. Lo que se pidió

1. **Top semanal.** Una sección de "más vendido de la semana" con los candidatos y los espacios que más movimiento tienen, al estilo de las vitrinas de Mercado Libre.
2. **Trending.** Un ranking de perfiles por ingresos, visitas e interacciones, no sólo por votos.
3. **Críticas con respuesta.** Que las críticas de cada ficha reciban interacción: acuerdo, desacuerdo y una defensa oficial del candidato o del espacio.
4. **Compra de votos.** Un voto gratis y después packs pagos: 1.000 votos por $1.000, 5.000 por $5.000, hasta 25.000 o 55.000.
5. **Campaña digital.** Un catálogo de servicios de campaña que se pueda comprar desde el sitio: sliders, posteos, estrategia con PDF de lineamientos.
6. **Perfiles editables.** Que un candidato pueda reclamar su página, editarla y responder, con un mecanismo de rectificación cuando la ficha dice algo que no le cierra.

## 2. Base que ya existe

No se arranca de cero. El sitio ya tiene:

- Redis por REST (Upstash) con contadores anónimos, límite por IP y un modo memoria para desarrollo (`api/_redis.js`).
- `POST /api/voto`: cuenta boletas finalizadas y arma el ranking por cargo (`rk:presidencial`, `rk:gobernador`, etc.).
- `GET /api/ranking`: devuelve los más elegidos por cargo, con un interruptor `RANKING_OFF` pensado para la veda.
- `POST /api/evento`: embudo anónimo de pasos (visita, agrega, completa, finaliza, comparte).
- `GET /api/metricas`: lectura interna con token.
- 106 fichas con videos, 87 propuestas y boleta con carrito.

Lo que falta es granularidad: hoy los contadores son globales y no hay series por día, ni vistas por perfil.

## 3. Módulo 1: rankings semanales

**Datos nuevos**

- `v:<fecha>:<cid>` contador de vistas por ficha y por día, alimentado desde `ficha.js` con un `POST /api/evento` nuevo (`ver_ficha` con `p=cid`).
- `rk:<cargo>:<semana>` además del acumulado, para poder mostrar la semana en curso y comparar con la anterior.
- `rk:esp:<espacio>` para el ranking de partidos, sumando los votos de sus candidatos.
- `delta` por perfil: posición de esta semana contra la anterior.

**Pantallas**

- Banda "Lo más vendido de la semana" en la home, con los cinco primeros por cargo y el badge de puesto.
- "En tendencia" con los perfiles que más crecieron en visitas en 24 horas.
- "Partidos en tendencia", ordenado por suma de vistas y votos de sus candidatos.
- En cada tarjeta, un chip chico con el puesto semanal cuando está entre los diez primeros.

**Esfuerzo**: 2 a 3 días. Es el módulo más simple y el que más rápido se ve.

## 4. Módulo 2: críticas, respuestas y rectificaciones

Tres niveles, de menor a mayor riesgo.

**Nivel 1, reacciones.** Cada crítica de la ficha tiene dos botones, "de acuerdo" y "no me convence", con contador anónimo y límite por IP. Sin texto libre, sin moderación. Sirve para saber qué crítica pega más.

**Nivel 2, respuesta oficial.** El espacio puede publicar una réplica a una crítica puntual desde su cuenta verificada. La crítica original queda visible y la réplica aparece debajo, firmada. Se registra la fecha. Ninguna de las dos se puede borrar, sólo actualizar con historial.

**Nivel 3, comentarios abiertos.** Cualquiera puede escribir. Requiere cola de moderación, filtro de insultos, límite por cuenta y una política de baja. Es el nivel que más trabajo de operación pide y el que puede contaminar el sitio en una semana.

**Rectificaciones.** Formulario público donde el candidato pide corregir un dato concreto, con evidencia y plazo de respuesta. Cada pedido genera un ticket y una edición visible en el historial de la ficha.

**Recomendación**: arrancar por el nivel 1 y el formulario de rectificación. El nivel 2 recién cuando existan las cuentas. El nivel 3, sólo si hay alguien moderando todos los días.

## 5. Módulo 3: compra de votos

**Mecánica propuesta**

- Un voto gratis por navegador y por día, para que la mecánica se entienda.
- Packs: 1.000 por $1.000, 5.000 por $5.000, 25.000 por $25.000, 55.000 por $55.000.
- Los votos comprados se acreditan al perfil elegido y se muestran en una línea aparte: "votos de apoyo", distinta de "votos de la comunidad".

**Decisión de fondo.** Si el dinero entra al sitio y se traduce en votos para un candidato, el proyecto deja de ser un simulador y pasa a parecerse a una colecta política. La Ley 26.215 regula el financiamiento de campañas y un aporte a un candidato tiene reglas. Dos caminos posibles:

1. **Votos simbólicos sin dinero.** Los packs se compran con una moneda interna y no hay pasarela. Se mantiene la sátira y desaparece el riesgo legal.
2. **Votos con dinero real.** Requiere cuenta de Mercado Pago del proyecto, facturación, términos y condiciones explícitos de que no es una donación ni un voto real, y que el dinero no se gira al candidato. Los votos comprados no deberían entrar al ranking principal sin etiqueta.

**Técnico, si va el camino 2**

- Checkout Pro de Mercado Pago con preferencia por pack.
- Webhook con verificación de firma, idempotencia por `payment_id` y acreditación en Redis.
- Ledger por usuario y por perfil, con reversos.
- Ambiente de prueba antes de producción.

**Esfuerzo**: 3 días para la mecánica simbólica, 2 semanas para producción con pagos reales y legales.

## 6. Módulo 4: campaña digital

**Catálogo**

- Kit de sliders (10 piezas, 1080x1350 y 1080x1920).
- Pack de posteos (20 piezas con copy).
- Estrategia de campaña digital: PDF con ejes, mensajes, calendario y segmentación.
- Guion de reels y spots cortos.
- Auditoría de perfil: qué dice hoy el candidato, qué le falta y qué conviene cambiar.

**Flujo**

1. Se elige el servicio y el candidato al que aplica.
2. Formulario de brief: distrito, eje prioritario, tono, qué no quiere decir.
3. Pago.
4. Entrega en 5 días hábiles.

**Contenido de referencia**: el método de campaña digital que ya se trabajó en Jannones, con la lógica del ejército digital, adaptado a un PDF de lineamientos que se pueda leer en veinte minutos.

**Riesgo editorial**: vender servicios a campañas convierte al sitio en proveedor político. Si eso pasa, hay que decirlo en el pie y separar la marca del servicio. La alternativa es ofrecerlo como demo: se ve el producto, se simula la compra y el interesado deja contacto.

## 7. Módulo 5: perfiles que se pueden reclamar

- Cuenta con magic link por mail, sin contraseñas.
- Verificación por dominio del espacio, mail oficial o revisión manual.
- Edición de bio, foto, videos y links, con historial público de cambios.
- Respuesta oficial a críticas y pedidos de rectificación.
- Perfiles sin reclamar muestran la etiqueta "sin reclamar" y un botón para iniciar el trámite.
- Para los candidatos que no tienen cuenta, la cuenta de X del sitio los etiqueta pidiendo que reclamen su perfil. Eso hay que coordinarlo con el calendario de publicaciones para no spamear.

**Esfuerzo**: 1 semana para cuentas y edición, 3 días más para rectificaciones.

## 8. Orden de trabajo

| Fase | Qué entra | Días |
|---|---|---|
| 0 | Vistas por ficha y votos por día | 1 |
| 1 | Top semanal, trending y partidos | 2 a 3 |
| 2 | Reacciones a críticas y formulario de rectificación | 2 |
| 3 | Cuentas, reclamo y respuesta oficial | 6 a 8 |
| 4 | Packs de votos simbólicos | 3 |
| 5 | Pagos reales y campaña digital | 10 a 15 |

Las fases 0 y 1 se pueden publicar sin decisión previa. De la 2 en adelante hay decisiones de producto y de riesgo que conviene cerrar antes de escribir código.

## 9. Decisiones pendientes

1. Los votos se compran con plata real o son simbólicos.
2. Los votos comprados entran al ranking principal o van en una línea aparte.
3. Las críticas abiertas al público o sólo respuestas oficiales.
4. La campaña digital se vende de verdad o se muestra como demo.
5. Las cuentas se abren con magic link para todos o sólo con reclamo verificado.

## 10. Riesgos a tener presentes

- **Difamación.** Una crítica con nombre propio y sin evidencia expone al sitio. Las críticas actuales tienen fuente; las que escriba el público no.
- **Suplantación.** Sin verificación, cualquiera puede abrir la cuenta de un candidato.
- **Brigading.** Un espacio organizado puede inflar reacciones. El límite por IP no alcanza: hace falta límite por cuenta y detección de picos.
- **Veda electoral.** El ranking ya tiene interruptor. Las compras y los rankings semanales tienen que apagarse en los días previos.
- **Datos personales.** Si hay cuentas, hay mails y hay que declarar el tratamiento.

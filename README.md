# Mercado Voto

Simulador tipo marketplace para elegir candidatos. Cada candidato tiene su página con perfil, trayectoria, composición ideológica en radar, promesas cumplidas e incumplidas y las críticas con su evidencia.

Sitio: https://mercado-voto.vercel.app

No es una encuesta ni un padrón. No se envía nada a ningún servidor: la boleta vive en el `localStorage` del navegador.

## Estructura

```
build.py              genera todo el HTML y los datos para el cliente desde el JSON
style.css             estilos
data/candidatos.json  fuente de verdad
assets/fotos/         fotos descargadas de Wikipedia
assets/app.js         boleta en localStorage, barra inferior, toasts, links para compartir
assets/catalogo.js    filtros, orden, banners, "Sorprendeme"
assets/ficha.js       compra y compartir desde la ficha
assets/boleta.js      checkout, perfil de la boleta, boletas compartidas, confeti
assets/share.js       imagen de la boleta en canvas (post 4:5 e historia 9:16)
assets/data.js        datos compactos para el cliente (generado)
api/og.js             imágenes de preview 1200x630 para links (portada, candidato, boleta)
api/b.js              /b?p=..&g=..&i=..&l=..: link corto con preview que redirige a /boleta
api/_data.js          mismos datos para las funciones (generado)
api/_fonts/           Inter para las previews (licencia OFL)
c/<slug>.html         una página por candidato (generadas)
index.html            catálogo (generado)
boleta.html           checkout (generado)
vercel.json           cleanUrls y rewrite de /b
```

## Regenerar

```bash
python3 build.py
```

Escribe `index.html`, `boleta.html`, las fichas de `c/`, `assets/data.js` y `api/_data.js`. No toca las fotos. Las funciones de `api/` necesitan `npm install` (usan `@vercel/og`).

Cuando cambies CSS o JS, subí `V` en `build.py` para romper la caché de los assets.

## Cómo se arma el catálogo

El catálogo no lista personas: lista **candidaturas**. Un mismo dirigente puede competir en la presidencial y en la gobernación de su provincia, y aparece dos veces con distinto cargo.

- `candidatos[]`: la ficha de cada persona.
- `candidaturas[]`: cada postulación, con `cid` (id del candidato), `cargo` (`presidencial`, `gobernador`, `intendente`, `legislador`) y `jur` (provincia o ciudad; `Nacional` para la presidencial y los legisladores nacionales).

Reparto actual: 15 presidenciales, 15 gobernadores (3 por provincia en cinco provincias), 11 intendentes (en cuatro ciudades) y 32 legisladores. La mayoría del padrón va como legislador porque es donde entran las listas.

La boleta se arma con un presidente, un gobernador, un intendente y hasta cinco legisladores. El almacenamiento vive en `localStorage` bajo `mv_boleta_v2`, como lista de objetos `{i, c, j}`.

## Compartir

- La boleta se comparte como link: `/b?p=<id>&g=<id>&i=<id>&l=<id>,<id>`. Esa ruta devuelve las etiquetas Open Graph con una imagen generada de esa boleta (`/api/og?...`) y redirige a `/boleta?...`, que la muestra en modo "te compartieron" con la opción de usarla como base.
- Cada ficha tiene su preview (`/api/og?c=<id>`).
- Desde el checkout se descarga la imagen en formato post o historia, o se comparte con el menú nativo del teléfono.
- El "perfil" de la boleta sale de la dispersión promedio de los seis ejes entre los candidatos elegidos: pura sangre, coherente, ensalada mixta o Frankenstein.

## Agregar o editar un candidato

Todo vive en `data/candidatos.json`. Campos por candidato:

- `id`, `nombre`, `slug` (el slug define la URL `/c/<slug>`)
- `rol`, `tag`, `partido`, `provincia`
- `color` (hex, se usa en el radar y en el avatar de respaldo)
- `foto` (ruta relativa o vacío para avatar con iniciales)
- `bio`, `trayectoria[]` (`fecha`, `evento`)
- `partido`, `provincia`
- `ejes[6]`: enteros 0 a 100, en este orden: Economía (Estado→Mercado), Sociedad (Conservador→Progresista), Poder (Institucional→Personalista), Federalismo (Centralista→Federal), Cambio (Continuidad→Ruptura), Exterior (Autonomía→Occidente)
- `promesas_cumplidas[]`, `promesas_incumplidas[]`, `cumplidas`, `incumplidas` (conteos)
- `criticas[]`: `area`, `tesis`, `cuerpo`, `evidencia`, `fuerza` (`letal`, `fuerte`, `media-fuerte`, `media`), `tipo`, `respuesta_esperada`, `refutacion`
- `vulnerabilidades[]`
- `gancho`: el "título de producto" en una línea, con humor.
- `a_favor[]`: los argumentos de quienes lo apoyan (alimenta "Lo bueno").
- `badge`: `NUEVO` (outsider), `CLÁSICO` o `REACONDICIONADO` (cambió de espacio). Vacío para el resto.

Los `ejes` son una estimación editorial, no una medición. La página lo dice explícitamente.

## Alcance actual

Cinco provincias para gobernación: Buenos Aires, Córdoba, Santa Fe, Mendoza y San Luis.
Cuatro ciudades para intendencia: CABA, Córdoba, Rosario y Mendoza.
La presidencial tiene a todos los perfiles cargados, incluidos los candidateables de Democracia S.A. (Hadad, Gebel, Galperín, Brito, Rebord).

## Lo que falta
- El precio ("1 voto") es parte del chiste, no un cálculo.
- Ocho perfiles no tienen foto y usan iniciales. Se descartaron fotos de Commons que no correspondían a la persona.
- Las fotos vienen de Wikipedia y se sirven locales. Si se agrega un candidato sin foto, el avatar usa iniciales sobre el color asignado.
- No hay backend ni base de usuarios. Si se quiere guardar la boleta o comparar entre dispositivos, hace falta una API.

## Deploy

```bash
vercel --prod --scope leandro-9726s-projects
```

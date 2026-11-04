# Mercado Voto

Simulador tipo marketplace para elegir candidatos. Cada candidato tiene su página con perfil, trayectoria, composición ideológica en radar, promesas cumplidas e incumplidas y las críticas con su evidencia.

Sitio: https://mercado-voto.vercel.app

No es una encuesta ni un padrón. No se envía nada a ningún servidor: la boleta vive en el `localStorage` del navegador.

## Estructura

```
build.py              genera todo el HTML desde el JSON
style.css             estilos (paleta Mercado Libre)
data/candidatos.json  fuente de verdad
assets/fotos/         fotos descargadas de Wikipedia
c/<slug>.html         una página por candidato (generadas)
index.html            catálogo con filtros (generado)
boleta.html           carrito (generado)
vercel.json           cleanUrls
```

## Regenerar

```bash
python3 build.py
```

Escribe `index.html`, `boleta.html` y las 25 fichas de `c/`. No toca las fotos.

## Cómo se arma el catálogo

El catálogo no lista personas: lista **candidaturas**. Un mismo dirigente puede competir en la presidencial y en la gobernación de su provincia, y aparece dos veces con distinto cargo.

- `candidatos[]`: la ficha de cada persona.
- `candidaturas[]`: cada postulación, con `cid` (id del candidato), `cargo` (`presidencial`, `gobernador`, `intendente`, `legislador`) y `jur` (provincia o ciudad; `Nacional` para la presidencial y los legisladores nacionales).

Reparto actual: 15 presidenciales, 15 gobernadores (3 por provincia en cinco provincias), 11 intendentes (en cuatro ciudades) y 32 legisladores. La mayoría del padrón va como legislador porque es donde entran las listas.

La boleta se arma con un presidente, un gobernador, un intendente y hasta cinco legisladores. El almacenamiento vive en `localStorage` bajo `mv_boleta_v2`, como lista de objetos `{i, c, j}`.

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

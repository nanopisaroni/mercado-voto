// Banda de la semana: los más vendidos (boletas de los últimos 7 días) y lo que está en tendencia
// por visitas de las últimas 48 horas. Se arma desde /api/ranking.
(() => {
  const $ = id => document.getElementById(id);
  const CARGO_N = { presidencial: 'Presidente', gobernador: 'Gobernador', intendente: 'Intendente', legislador: 'Legislador' };
  const fmt = n => n.toLocaleString('es-AR');
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  function fecha(iso) {
    const [a, m, d] = iso.split('-').map(Number);
    return new Date(a, m - 1, d).toLocaleDateString('es-AR', { day: 'numeric', month: 'short' });
  }

  function avatar(c) {
    if (c.f) return '<img src="/' + c.f + '" alt="" loading="lazy">';
    return '<span class="sem-ini" style="--c:' + c.col + '">' + esc(c.i) + '</span>';
  }

  fetch('/api/ranking').then(r => r.ok ? r.json() : null).then(d => {
    if (!d || d.off) return;
    const filas = [];
    Object.keys(d.sem || {}).forEach(cg => (d.sem[cg] || []).forEach(([id, jur, n]) => {
      if (MV.c[id]) filas.push({ id, cg, jur, n });
    }));
    filas.sort((a, b) => b.n - a.n);
    const top = filas.slice(0, 4);
    const tend = (d.tend || []).filter(([id]) => MV.c[id]).slice(0, 8);
    if (!top.length && !tend.length) return;

    if (top.length) {
      $('sem-sub').textContent = 'Del ' + fecha(d.desde) + ' al ' + fecha(d.hasta) + ' · ' + (d.semTotal === 1 ? '1 boleta armada' : fmt(d.semTotal) + ' boletas armadas');
      $('sem-lista').innerHTML = top.map((x, k) => {
        const c = MV.c[x.id];
        return '<li><a class="sem-item" href="/c/' + c.s + '">' +
          '<span class="sem-pos' + (k === 0 ? ' uno' : '') + '">' + (k + 1) + '</span>' +
          avatar(c) +
          '<span class="sem-txt" title="' + esc(c.n) + '"><b>' + esc(c.n) + '</b><small>' + CARGO_N[x.cg] + (x.jur && x.jur !== 'Nacional' ? ' · ' + esc(x.jur) : '') + '</small></span>' +
          '<span class="sem-n">' + fmt(x.n) + '<small>boleta' + (x.n === 1 ? '' : 's') + '</small></span>' +
          '</a></li>';
      }).join('');
      $('sem-bloque').hidden = false;
    }

    if (tend.length) {
      $('tend-chips').innerHTML = tend.map(([id, n]) => {
        const c = MV.c[id];
        return '<a class="tend-chip" href="/c/' + c.s + '">' + esc(c.n) + ' <span>' + fmt(n) + ' visitas</span></a>';
      }).join('');
      $('tend').hidden = false;
    }

    $('semana').hidden = false;
  }).catch(() => {});
})();

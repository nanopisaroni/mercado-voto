// Campaña digital: elegir un plan, sumar extras, pedirlo.
// No se cobra en el sitio: el pedido se registra y el pago se coordina por transferencia.
(() => {
  const $ = id => document.getElementById(id);
  const est = { plan: null, extras: [] };
  const fmt = n => '$' + n.toLocaleString('es-AR');

  const datos = () => {
    const p = est.plan ? document.querySelector('.ccard[data-plan="' + est.plan + '"]') : null;
    const extras = est.extras.map(id => document.querySelector('.addon[data-addon="' + id + '"]')).filter(Boolean);
    const total = (p ? +p.dataset.precio : 0) + extras.reduce((s, e) => s + +e.dataset.precio, 0);
    return { plan: p, extras, total };
  };

  function pintar() {
    document.querySelectorAll('.ccard').forEach(c => c.classList.toggle('elegido', c.dataset.plan === est.plan));
    document.querySelectorAll('.ccard .add-camp').forEach(b => {
      b.textContent = b.dataset.plan === est.plan ? '✓ Elegido' : 'Contratar';
    });
    document.querySelectorAll('.addon').forEach(a => {
      const on = est.extras.includes(a.dataset.addon);
      a.classList.toggle('elegido', on);
      a.querySelector('.addon-add').textContent = on ? '✓ Sumado' : 'Sumar';
    });
    const { plan, extras, total } = datos();
    const bar = $('camp-bar');
    if (!plan) { bar.hidden = true; return; }
    bar.hidden = false;
    $('cb-txt').innerHTML = '<b>' + plan.dataset.nombre + '</b>' + (extras.length ? ' + ' + extras.length + ' extra' + (extras.length > 1 ? 's' : '') : '');
    $('cb-total').textContent = fmt(total);
  }

  document.addEventListener('click', e => {
    const add = e.target.closest('.add-camp');
    if (add) {
      est.plan = est.plan === add.dataset.plan ? null : add.dataset.plan;
      pintar();
      if (est.plan) track('ver_campana', 'plan-' + est.plan);
      return;
    }
    const ex = e.target.closest('.addon-add');
    if (ex) {
      const id = ex.closest('.addon').dataset.addon;
      est.extras = est.extras.includes(id) ? est.extras.filter(x => x !== id) : est.extras.concat(id);
      pintar();
    }
  });

  // ---------- pedido ----------
  function resumen() {
    const { plan, extras, total } = datos();
    if (!plan) return '';
    return '<ul class="ped-lista"><li>' + plan.dataset.nombre + '<b>' + fmt(+plan.dataset.precio) + '</b></li>' +
      extras.map(x => '<li>' + x.dataset.nombre + '<b>' + fmt(+x.dataset.precio) + '</b></li>').join('') +
      '</ul><div class="ped-total">Total <b>' + fmt(total) + '</b></div>';
  }

  function abrir() {
    if (!est.plan) return;
    $('m-pedido').hidden = false;
    document.body.classList.add('sin-scroll');
    $('ped-resumen').innerHTML = resumen();
    setTimeout(() => $('p-nombre').focus(), 50);
  }
  function cerrar() {
    $('m-pedido').hidden = true;
    document.body.classList.remove('sin-scroll');
  }

  document.addEventListener('click', e => {
    if (e.target.closest('#cb-seguir')) abrir();
    if (e.target.closest('[data-cerrar-pedido]')) cerrar();
  });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && !$('m-pedido').hidden) cerrar(); });

  $('ped-form').addEventListener('submit', async ev => {
    ev.preventDefault();
    const btn = $('p-enviar');
    const err = $('p-error');
    err.hidden = true;
    btn.disabled = true;
    btn.textContent = 'Enviando…';
    try {
      const r = await fetch('/api/pedido', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          plan: est.plan,
          addons: est.extras,
          nombre: $('p-nombre').value,
          contacto: $('p-contacto').value,
          espacio: $('p-espacio').value,
          notas: $('p-notas').value,
        }),
      });
      const d = await r.json().catch(() => ({}));
      if (!r.ok || !d.ok) throw new Error(d.motivo || 'error');
      $('ped-form').hidden = true;
      const ok = $('ped-ok');
      ok.hidden = false;
      ok.innerHTML = '<div class="ok-ico">✓</div><h3>Pedido registrado</h3>' +
        '<p>Tu código es <b>' + d.codigo + '</b>. Guardalo.</p>' +
        '<p>Total: <b>' + fmt(d.total) + '</b>. Te escribimos a ' + esc($('p-contacto').value) + ' para coordinar el pago y arrancar.</p>' +
        '<p class="ok-nota">Todavía no se cobró nada.</p><button class="btn" type="button" data-cerrar-pedido>Listo</button>';
    } catch (e) {
      const m = { limite: 'Probaste varias veces seguidas. Esperá un minuto.', plan: 'Elegí un plan.', nombre: 'Falta tu nombre.', contacto: 'Falta un contacto.', guardado: 'No pudimos guardar el pedido. Probá de nuevo.' };
      err.textContent = m[e.message] || 'No pudimos registrar el pedido. Probá de nuevo.';
      err.hidden = false;
    } finally {
      btn.disabled = false;
      btn.textContent = 'Confirmar pedido';
    }
  });

  function esc(s) { return String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])); }

  track('ver_campana', 'campanas');
  pintar();
})();

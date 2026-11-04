/* filtros y catálogo */
const state = { cargo: "", jur: "", partido: "", prov: "", eco: 0, q: "", orden: "" };

function candidaturas() { return [...document.querySelectorAll('.card')]; }

function llenarJurisdicciones() {
  const sel = document.getElementById('f-jur');
  const vals = new Set();
  candidaturas().forEach(t => {
    if (state.cargo && t.dataset.cargo !== state.cargo) return;
    if (t.dataset.jur && t.dataset.jur !== 'Nacional') vals.add(t.dataset.jur);
  });
  const actual = sel.value;
  sel.innerHTML = '<option value="">Todas</option>' +
    [...vals].sort().map(v => `<option value="${v}">${v}</option>`).join('');
  sel.style.display = vals.size ? '' : 'none';
  sel.value = vals.has(actual) ? actual : '';
  state.jur = sel.value;
}

function aplicar() {
  let n = 0;
  candidaturas().forEach(t => {
    const d = t.dataset;
    const ok = (!state.cargo || d.cargo === state.cargo)
      && (!state.jur || d.jur === state.jur)
      && (!state.partido || d.partido === state.partido)
      && (!state.q || d.nombre.includes(state.q) || d.partido.toLowerCase().includes(state.q) || d.jur.toLowerCase().includes(state.q))
      && (state.eco === 0 || Math.abs(+d.eco - state.eco) <= 25);
    t.style.display = ok ? '' : 'none';
    if (ok) n++;
  });
  const grid = document.getElementById('grid');
  const arr = [...grid.children].filter(x => x.style.display !== 'none');
  if (state.orden === 'cumplimiento') arr.sort((a, b) => (+b.dataset.cum || 0) - (+a.dataset.cum || 0));
  if (state.orden === 'ruptura') arr.sort((a, b) => (+b.dataset.rupt || 0) - (+a.dataset.rupt || 0));
  if (state.orden === 'nombre') arr.sort((a, b) => a.dataset.nombre.localeCompare(b.dataset.nombre));
  arr.forEach(x => grid.appendChild(x));
  document.getElementById('cuenta').textContent = n + (n === 1 ? ' resultado' : ' resultados');
}

document.addEventListener('DOMContentLoaded', () => {
  const q = new URLSearchParams(location.search);
  if (q.get('cargo')) {
    const r = document.querySelector(`input[name=cargo][value="${q.get('cargo')}"]`);
    if (r) { r.checked = true; state.cargo = q.get('cargo'); }
  }
  if (q.get('jur')) state.jur = q.get('jur');
  if (q.get('orden')) { state.orden = q.get('orden'); document.getElementById('orden').value = q.get('orden'); }
  llenarJurisdicciones();
  aplicar();

  document.querySelectorAll('input[name=cargo]').forEach(r => r.addEventListener('change', () => {
    state.cargo = r.value; state.jur = ''; llenarJurisdicciones(); aplicar();
  }));
  document.getElementById('f-jur').addEventListener('change', e => { state.jur = e.target.value; aplicar(); });
  document.getElementById('f-partido').addEventListener('change', e => { state.partido = e.target.value; aplicar(); });
  document.getElementById('f-eco').addEventListener('input', e => { state.eco = +e.target.value; aplicar(); });
  document.getElementById('q').addEventListener('input', e => { state.q = e.target.value.toLowerCase().trim(); aplicar(); });
  document.getElementById('orden').addEventListener('change', e => { state.orden = e.target.value; aplicar(); });
});

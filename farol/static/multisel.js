/* Seleção múltipla do Farol: um botão que abre uma lista de caixas de marcação,
   com "Todos" e "Nenhum". Usado nos filtros da busca e da Teia.

   const ms = MultiSel(host, {nome:'tema', plural:'temas', opcoes:[{v:'graduação', l:'graduação', n:120}], aoMudar:fn, inline:false});
   ms.aceita(valor)  → true se o filtro deixa passar (todos marcados, ou valor marcado)
   ms.todos()        → true quando nada está filtrado (estado inicial)
   ms.nenhum()       → true quando nada está marcado
   ms.valores()      → Set dos valores marcados (vazio quando "todos")
   ms.reset()        → volta a "todos"
   ms.marcar(['a','b']) → marca só esses */
(function (global) {
  'use strict';
  var abertos = [];
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function norm(s) { return String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); }

  function MultiSel(host, o) {
    if (typeof host === 'string') host = document.getElementById(host);
    o = o || {};
    var opcoes = o.opcoes || [];
    var todos = true, sel = new Set();
    host.classList.add('msel');
    if (o.inline) host.classList.add('inline');
    host.innerHTML = '<button type="button" class="msel-btn" aria-haspopup="listbox" aria-expanded="false"><span class="msel-txt"></span><span class="msel-caret" aria-hidden="true">▾</span></button>'
      + '<div class="msel-pop" hidden><div class="msel-acts"><button type="button" data-a="todos">Todos</button><button type="button" data-a="nenhum">Nenhum</button>'
      + (opcoes.length > 8 ? '<input type="search" placeholder="filtrar a lista…" aria-label="Filtrar a lista">' : '') + '</div>'
      + '<div class="msel-list" role="listbox" aria-multiselectable="true">' + opcoes.map(function (op, i) {
        return '<label><input type="checkbox" data-i="' + i + '" checked> <span class="l">' + esc(op.l != null ? op.l : op.v) + '</span>' + (op.n != null ? '<span class="n">' + op.n + '</span>' : '') + '</label>';
      }).join('') + '</div></div>';
    var btn = host.querySelector('.msel-btn'), txt = host.querySelector('.msel-txt'), pop = host.querySelector('.msel-pop'),
      list = host.querySelector('.msel-list'), filtro = host.querySelector('input[type=search]');
    var caixas = Array.prototype.slice.call(list.querySelectorAll('input[type=checkbox]'));

    function rotulo() {
      var plural = o.plural || 'itens', sing = o.nome || 'item';
      if (todos) return (o.rotuloTodos || ('Todos os ' + plural));
      if (!sel.size) return 'Nenhum ' + sing;
      if (sel.size === 1) { var v = sel.values().next().value; var op = opcoes.filter(function (x) { return x.v === v; })[0]; return op ? (op.l != null ? op.l : op.v) : v; }
      return sel.size + ' ' + plural;
    }
    function pintar() {
      caixas.forEach(function (c) { c.checked = todos || sel.has(opcoes[+c.dataset.i].v); });
      txt.textContent = rotulo();
      host.classList.toggle('filtrando', !todos);
    }
    function mudou() { pintar(); if (o.aoMudar) o.aoMudar(api); }
    function abrir(on) {
      if (on) { abertos.forEach(function (a) { if (a !== api) a.fechar(); }); }
      pop.hidden = !on; btn.setAttribute('aria-expanded', String(on));
      if (on && filtro) { filtro.value = ''; filtrar(''); setTimeout(function () { filtro.focus(); }, 0); }
    }
    function filtrar(s) {
      var k = norm(s);
      caixas.forEach(function (c) { var op = opcoes[+c.dataset.i]; c.parentElement.hidden = !!k && norm(op.l != null ? op.l : op.v).indexOf(k) < 0; });
    }
    btn.addEventListener('click', function () { abrir(pop.hidden); });
    pop.querySelector('[data-a=todos]').addEventListener('click', function () { todos = true; sel = new Set(); mudou(); });
    pop.querySelector('[data-a=nenhum]').addEventListener('click', function () { todos = false; sel = new Set(); mudou(); });
    if (filtro) filtro.addEventListener('input', function () { filtrar(filtro.value); });
    list.addEventListener('change', function (ev) {
      var c = ev.target; if (!c || c.type !== 'checkbox') return;
      if (todos) { todos = false; sel = new Set(opcoes.map(function (x) { return x.v; })); }
      var v = opcoes[+c.dataset.i].v;
      if (c.checked) sel.add(v); else sel.delete(v);
      if (sel.size === opcoes.length) { todos = true; sel = new Set(); }
      mudou();
    });
    document.addEventListener('click', function (ev) { if (!host.contains(ev.target) && !pop.hidden) abrir(false); });
    host.addEventListener('keydown', function (ev) { if (ev.key === 'Escape' && !pop.hidden) { abrir(false); btn.focus(); } });

    var api = {
      host: host,
      aceita: function (v) { return todos || sel.has(v); },
      aceitaAlgum: function (lista) { if (todos) return true; if (!sel.size) return false; return (lista || []).some(function (v) { return sel.has(v); }); },
      todos: function () { return todos; },
      nenhum: function () { return !todos && !sel.size; },
      valores: function () { return new Set(sel); },
      reset: function () { todos = true; sel = new Set(); pintar(); },
      marcar: function (vals) { todos = false; sel = new Set(vals); if (sel.size === opcoes.length) { todos = true; sel = new Set(); } pintar(); },
      fechar: function () { abrir(false); }
    };
    abertos.push(api);
    pintar();
    return api;
  }
  global.MultiSel = MultiSel;
})(window);

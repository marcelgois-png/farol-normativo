/* Tabelas do Farol: clique no título da coluna ordena (crescente, decrescente, original).
   Reconhece números em pt-BR (1.234), datas dd/mm/aaaa, códigos (D45, N7) e texto. */
(function () {
  'use strict';
  var col = new Intl.Collator('pt-BR', { numeric: true, sensitivity: 'base' });

  function chave(txt) {
    var t = (txt || '').trim();
    if (!t) return { tipo: 2, v: '' };
    var m = /^(\d{1,2})\/(\d{2})\/(\d{4})$/.exec(t);
    if (m) return { tipo: 0, v: +(m[3] + m[2] + m[1]) };
    if (/^-?\d{1,3}(\.\d{3})*(,\d+)?$|^-?\d+(,\d+)?$/.test(t)) return { tipo: 0, v: parseFloat(t.replace(/\./g, '').replace(',', '.')) };
    return { tipo: 1, v: t };
  }

  function comparar(a, b, dir) {
    if (a.tipo !== b.tipo) return (a.tipo - b.tipo) * (a.tipo === 2 || b.tipo === 2 ? 1 : dir);
    if (a.tipo === 0) return (a.v - b.v) * dir;
    return col.compare(a.v, b.v) * dir;
  }

  function preparar(tabela) {
    var thead = tabela.tHead, tbody = tabela.tBodies[0];
    if (!thead || !tbody) return;
    var ths = thead.rows[0].cells;
    var original = Array.prototype.slice.call(tbody.rows);
    Array.prototype.forEach.call(ths, function (th, i) {
      th.classList.add('ord');
      th.tabIndex = 0;
      th.title = 'Ordenar por ' + th.textContent.trim();
      function acionar() {
        var atual = th.getAttribute('aria-sort');
        Array.prototype.forEach.call(ths, function (o) { o.removeAttribute('aria-sort'); });
        var linhas;
        if (atual === 'descending') {
          linhas = original;
        } else {
          var dir = atual === 'ascending' ? -1 : 1;
          th.setAttribute('aria-sort', dir === 1 ? 'ascending' : 'descending');
          linhas = original.map(function (tr, k) { return { tr: tr, k: k, c: chave(tr.cells[i] ? tr.cells[i].textContent : '') }; })
            .sort(function (x, y) { return comparar(x.c, y.c, dir) || (x.k - y.k); })
            .map(function (x) { return x.tr; });
        }
        linhas.forEach(function (tr) { tbody.appendChild(tr); });
        if (tabela.parentElement && tabela.parentElement.classList.contains('tabela')) tabela.parentElement.scrollTop = 0;
      }
      th.addEventListener('click', acionar);
      th.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); acionar(); } });
    });
  }

  document.querySelectorAll('table').forEach(preparar);
})();

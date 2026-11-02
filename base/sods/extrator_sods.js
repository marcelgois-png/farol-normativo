// Extrator de texto das páginas da SODS (site WordPress da UFPB).
// Uso: abrir a página oficial no navegador, colar este arquivo no console
// e chamar extrairSODS(). Devolve {texto, links, sha256} — o texto é o que
// vai para base/sods/extracoes/<pagina>.txt, e o hash confere a cópia.
//
// Regras (as mesmas registradas em base/sods/extracoes.json):
// - raiz: div.the-content-container; blocos (p, h1-h6, summary, listas,
//   células de tabela) separados por linha em branco; <br> vira quebra;
// - <s>/<del>/<strike> (redação revogada no consolidado) vira ~~...~~ por linha;
// - <ol>/<ul> numeradas pelo estilo CSS aplicado (decimal "1. ", romano
//   "I – ", alfabético "a) "), sublistas achatadas na sequência;
// - <sup>o</sup> e <sup>a</sup> viram º e ª; NBSP vira espaço; espaços
//   repetidos colapsados; linhas vazias removidas; Unicode NFC;
// - <summary> de blocos recolhíveis vira linha "=== título ===".
// Nada é corrigido ou digitado à mão.

function extrairSODS(root) {
  root = root || document.querySelector('div.the-content-container');
  const links = [];
  function tacha(i) {
    return i.split('\n').map(l => { const m = l.match(/^(\s*)(.*?)(\s*)$/); return m[2] ? m[1] + '~~' + m[2] + '~~' + m[3] : l; }).join('\n');
  }
  function inline(node) {
    let s = '';
    for (const c of node.childNodes) {
      if (c.nodeType === 3) s += c.nodeValue;
      else if (c.nodeType === 1) {
        const t = c.tagName.toLowerCase();
        if (t === 'br') s += '\n';
        else if (t === 's' || t === 'del' || t === 'strike') { const i = inline(c).replace(/ /g, ' '); s += i.trim() ? tacha(i) : i; }
        else if (t === 'sup') { const i = inline(c); s += (i.trim() === 'o' ? 'º' : i.trim() === 'a' ? 'ª' : i); }
        else if (t === 'a') { const i = inline(c); const h = c.getAttribute('href'); if (h) links.push({ texto: i.replace(/\s+/g, ' ').trim(), href: h }); s += i; }
        else if (t === 'script' || t === 'style' || t === 'img') { }
        else s += inline(c);
      }
    }
    return s;
  }
  function norm(s) {
    s = s.replace(/ /g, ' ').replace(/[​﻿­]/g, '');
    for (let k = 0; k < 3; k++) s = s.replace(/~~([ \t]*)~~/g, '$1'); // funde tachados adjacentes
    return s.split('\n').map(l => l.replace(/\s+/g, ' ').trim()).filter(l => l).join('\n');
  }
  const rom = v => { const t = [[1000, 'M'], [900, 'CM'], [500, 'D'], [400, 'CD'], [100, 'C'], [90, 'XC'], [50, 'L'], [40, 'XL'], [10, 'X'], [9, 'IX'], [5, 'V'], [4, 'IV'], [1, 'I']]; let r = ''; for (const [k, s] of t) { while (v >= k) { r += s; v -= k; } } return r; };
  function marcador(style, n) {
    if (style === 'decimal') return n + '. ';
    if (style === 'lower-alpha' || style === 'lower-latin') return String.fromCharCode(96 + n) + ') ';
    if (style === 'upper-alpha' || style === 'upper-latin') return String.fromCharCode(64 + n) + '. ';
    if (style === 'upper-roman') return rom(n) + ' – ';
    if (style === 'lower-roman') return rom(n).toLowerCase() + '. ';
    if (style === 'none') return '';
    return '- ';
  }
  const blocos = [];
  function lista(node, itens) {
    const style = getComputedStyle(node).listStyleType; let n = parseInt(node.getAttribute('start') || '1', 10);
    for (const li of node.children) {
      if (li.tagName.toLowerCase() !== 'li') continue;
      const sub = [...li.children].filter(k => /^(ol|ul)$/i.test(k.tagName));
      const clone = li.cloneNode(true); clone.querySelectorAll('ol,ul').forEach(x => x.remove());
      const s = norm(inline(clone)); if (s) itens.push(marcador(style, n) + s.replace(/\n/g, ' ')); n++;
      for (const sl of sub) lista(sl, itens);
    }
  }
  function bloco(node) {
    const t = node.tagName.toLowerCase();
    if (t === 'p' || /^h[1-6]$/.test(t) || t === 'summary') { const s = norm(inline(node)); if (s) blocos.push(t === 'summary' ? '=== ' + s + ' ===' : s); }
    else if (t === 'ol' || t === 'ul') { const itens = []; lista(node, itens); if (itens.length) blocos.push(itens.join('\n')); }
    else if (t === 'table') { for (const cell of node.querySelectorAll('td,th')) { const kids = [...cell.children].filter(k => /^(p|ol|ul|table|div|h[1-6])$/i.test(k.tagName)); if (kids.length) kids.forEach(k => bloco(k)); else { const s = norm(inline(cell)); if (s) blocos.push(s); } } }
    else if (t === 'figure' || t === 'div' || t === 'section' || t === 'blockquote' || t === 'article' || t === 'details') { for (const k of node.children) bloco(k); }
    else if (t === 'hr' || t === 'script' || t === 'style' || t === 'img' || t === 'figcaption') { }
    else { const s = norm(inline(node)); if (s) blocos.push(s); }
  }
  for (const k of root.children) bloco(k);
  const texto = blocos.join('\n\n').normalize('NFC') + '\n';
  return crypto.subtle.digest('SHA-256', new TextEncoder().encode(texto)).then(d => ({
    texto, links, sha256: [...new Uint8Array(d)].map(x => x.toString(16).padStart(2, '0')).join('')
  }));
}

// Construtor de fluxogramas draw.io no padrão ALM001 (skill ajuda-ct-procedimentos, seção 5).
(function (g) {
  const COLX = { '-1': 310, '0': 600, '1': 890 }, ROWH = 100, W = 180;
  const ST = {
    start: 'ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=#d5e8d4;strokeColor=#82b366;fontFamily=Helvetica;container=0;shadow=0;',
    end: 'ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=#f8cecc;strokeColor=#b85450;fontFamily=Helvetica;container=0;shadow=0;',
    set: 'rounded=0;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontFamily=Helvetica;container=0;glass=0;shadow=0;',
    req: 'rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontFamily=Helvetica;container=0;glass=0;shadow=0;',
    info: 'rounded=0;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontFamily=Helvetica;container=0;glass=0;shadow=0;fontColor=#333333;',
    dec: 'rhombus;html=1;fillColor=#fff2cc;strokeColor=#d6b656;container=0;fontFamily=Helvetica;fontSize=11;labelPosition=left;verticalLabelPosition=bottom;align=right;verticalAlign=top;spacingRight=-4;spacingTop=-6;'
  };
  const FLOW = 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;fontFamily=Helvetica;endArrow=classic;endFill=1;fontSize=11;labelBackgroundColor=#ffffff;';
  const DOT = 'endArrow=none;dashed=1;html=1;dashPattern=1 3;strokeWidth=2;rounded=0;';
  const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#x27;');
  const lines = t => { let n = 0, c = 0; for (const w of t.split(/\s+/).filter(Boolean)) { if (c === 0) { c = w.length; n++; } else if (c + 1 + w.length <= 25) c += 1 + w.length; else { n++; c = w.length; } } return n; };
  const LEG = [['lg', '', 'group', null, [234, -200, 733, 131]],
    ['lg0', '', 'rounded=1;whiteSpace=wrap;html=1;strokeWidth=2;dashed=1;dashPattern=1 2;fillColor=none;arcSize=12;', 'lg', [0, 0, 733, 131]],
    ['lg1', 'LEGENDAS:', 'rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=none;fontFamily=Helvetica;container=0;fontStyle=1;', 'lg', [0, 8, 110, 30]],
    ['lg2', 'INÍCIO', ST.start, 'lg', [90, 48, 50, 50]], ['lg3', 'FIM', ST.end, 'lg', [186, 48, 50, 50]],
    ['lg4', 'SE', 'rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontFamily=Helvetica;container=0;', 'lg', [277, 49, 56, 50]],
    ['lg5', 'Tarefa do setor', ST.set, 'lg', [370, 48, 80, 50]], ['lg6', 'Tarefa do requisitante', ST.req, 'lg', [490, 48, 80, 50]],
    ['lg7', 'Informações Adicionais', ST.info, 'lg', [610, 48, 80, 50]]];
  // nodes: [id, tipo(start|end|set|req|info|dec), coluna, linha, texto]; edges: [origem, destino, rótulo?, {dot, exit, entry, points}?]
  function build(nodes, edges) {
    const N = {}, cells = ['<mxCell id="0"/>', '<mxCell id="1" parent="0"/>'];
    for (const [id, val, style, parent, [x, y, w, h]] of LEG)
      cells.push(`<mxCell id="${id}" value="${esc(val)}" style="${style}" vertex="1"${style === 'group' ? ' connectable="0"' : ''} parent="${parent || 1}"><mxGeometry x="${x}" y="${y}" width="${w}" height="${h}" as="geometry"/></mxCell>`);
    for (const [id, kind, col, row, text] of nodes) {
      let w, h, val;
      if (kind === 'start' || kind === 'end') { w = h = 50; val = kind === 'start' ? 'INÍCIO' : 'FIM'; }
      else if (kind === 'dec') { w = h = 40; val = text; }
      else { w = W; h = Math.max(60, 15 * lines(text) + 16); val = text; }
      const x = COLX[String(col)] - w / 2, y = row * ROWH - h / 2;
      N[id] = { kind, col, row };
      const v = kind === 'dec' ? esc(val.split('<br>').map(esc).join('<br>')) : esc(val);
      cells.push(`<mxCell id="${id}" value="${v}" style="${ST[kind]}" vertex="1" parent="1"><mxGeometry x="${x}" y="${y}" width="${w}" height="${h}" as="geometry"/></mxCell>`);
    }
    edges.forEach((e, i) => {
      const [src, dst, label] = e, opt = e[3] || {}, a = N[src], b = N[dst];
      const dotted = opt.dot || a.kind === 'info' || b.kind === 'info';
      let ex, en;
      if (opt.exit) { ex = opt.exit; en = opt.entry; }
      else if (a.col === b.col) [ex, en] = b.row > a.row ? [[0.5, 1], [0.5, 0]] : [[0.5, 0], [0.5, 1]];
      else if (a.row === b.row) [ex, en] = b.col > a.col ? [[1, 0.5], [0, 0.5]] : [[0, 0.5], [1, 0.5]];
      else if (b.col === 0) { ex = b.row > a.row ? [0.5, 1] : [0.5, 0]; en = a.col < 0 ? [0, 0.5] : [1, 0.5]; }
      else { ex = b.col > a.col ? [1, 0.5] : [0, 0.5]; en = b.row > a.row ? [0.5, 0] : [0.5, 1]; }
      const style = (dotted ? DOT : FLOW) + `exitX=${ex[0]};exitY=${ex[1]};exitDx=0;exitDy=0;entryX=${en[0]};entryY=${en[1]};entryDx=0;entryDy=0;`;
      const pts = opt.points ? '<Array as="points">' + opt.points.map(([px, py]) => `<mxPoint x="${px}" y="${py}"/>`).join('') + '</Array>' : '';
      let ga = 'relative="1"', off = '';
      if (label) { if (ex[1] === 0.5) { ga = 'x="-0.45" relative="1"'; off = '<mxPoint y="-10" as="offset"/>'; } else { ga = 'x="-0.3" relative="1"'; off = '<mxPoint x="14" as="offset"/>'; } }
      cells.push(`<mxCell id="e${i}" value="${esc(label || '')}" style="${style}" edge="1" parent="1" source="${src}" target="${dst}"><mxGeometry ${ga} as="geometry">${pts}${off}</mxGeometry></mxCell>`);
    });
    return '<mxGraphModel dx="1200" dy="1400" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="0" pageScale="1" pageWidth="1169" pageHeight="1654" math="0" shadow="0"><root>' + cells.join('') + '</root></mxGraphModel>';
  }
  const dilig = (check, dec, row, red, blue) => [
    [[dec + 'r', 'set', 1, row, red], [dec + 'b', 'req', 1, row - 1, blue]],
    [[dec, dec + 'r', 'Não'], [dec + 'r', dec + 'b'], [dec + 'b', check]]];
  const mxfile = (name, model) => `<mxfile host="Ajuda CT"><diagram id="${esc(name)}" name="${esc(name)}">${model}</diagram></mxfile>`;
  g.FB = { build, dilig, mxfile };
})(typeof window !== 'undefined' ? window : globalThis);

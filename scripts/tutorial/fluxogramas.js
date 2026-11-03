// Fluxogramas dos tutoriais do Farol Normativo no Ajuda CT (padrão ALM001).
// Uso: node scripts/tutorial/fluxogramas.js  → docs/tutorial/fluxogramas/FAROLnn.drawio e fluxos.json
// nós: [id, tipo(start|end|set|req|info|dec), coluna(-1|0|1), linha, texto]; arestas: [origem, destino, rótulo?]
require('./fb.js');
const fs = require('fs'), path = require('path');

const F = {
  FAROL00: [[
    ['s', 'start', 0, 0, ''],
    ['a', 'req', 0, 1, 'Buscar a norma pelo número, pelo assunto ou pelo órgão (FAROL02)'],
    ['d', 'dec', 0, 2, 'Está no<br>acervo?'],
    ['n1', 'req', -1, 2, 'Conferir a norma na Fila de coleta (FAROL10)'],
    ['n2', 'req', -1, 3, 'Pedir a inclusão no Atendimento CT – Direção de Centro'],
    ['n3', 'set', -1, 4, 'Direção do CT: conferir na fonte oficial e incluir na fila de coleta'],
    ['b', 'req', 0, 3, 'Abrir a ficha: situação, quem a altera e em que se funda (FAROL03)'],
    ['bi', 'info', 1, 3, 'Toda ficha traz o link para o texto oficial'],
    ['c', 'req', 0, 4, 'Ler o texto integral e as anotações dos artigos (FAROL04)'],
    ['e', 'req', 0, 5, 'Seguir a cadeia de normas na Teia (FAROL05 e FAROL06)'],
    ['ei', 'info', 1, 5, 'Sugestões aparecem em pontilhado e não são relação normativa'],
    ['f', 'dec', 0, 6, 'Há conflito<br>ou dúvida?'],
    ['g', 'req', 1, 6, 'Conferir o Quadro de vigência e as Divergências (FAROL08 e FAROL09)'],
    ['z', 'end', 0, 7, '']],
  [['s', 'a'], ['a', 'd'], ['d', 'b', 'Sim'], ['d', 'n1', 'Não'], ['n1', 'n2'], ['n2', 'n3'], ['n3', 'z'],
   ['b', 'bi'], ['b', 'c'], ['c', 'e'], ['e', 'ei'], ['e', 'f'], ['f', 'g', 'Sim'], ['f', 'z', 'Não'], ['g', 'z']]],

  FAROL01: [[
    ['s', 'start', 0, 0, ''],
    ['a', 'req', 0, 1, 'Acessar o Farol Normativo no navegador'],
    ['ai', 'info', 1, 1, 'Público: sem login nem senha'],
    ['b', 'req', 0, 2, 'Conhecer a barra de título, o menu e o tema claro ou escuro'],
    ['bi', 'info', 1, 2, 'A escolha do tema fica guardada no navegador'],
    ['d', 'dec', 0, 3, 'Já sabe qual<br>norma procura?'],
    ['e', 'req', -1, 3, 'Abrir um dos oito exemplos da página inicial'],
    ['f', 'req', 0, 4, 'Buscar pelo número, pelo assunto ou pelo órgão (FAROL02)'],
    ['g', 'req', 0, 5, 'Consultar os símbolos e as cores na página Sobre'],
    ['z', 'end', 0, 6, '']],
  [['s', 'a'], ['a', 'ai'], ['a', 'b'], ['b', 'bi'], ['b', 'd'], ['d', 'f', 'Sim'], ['d', 'e', 'Não'], ['e', 'g'], ['f', 'g'], ['g', 'z']]],

  FAROL02: [[
    ['s', 'start', 0, 0, ''],
    ['a', 'req', 0, 1, 'Digitar o número, o assunto ou o órgão e clicar em Buscar'],
    ['ai', 'info', 1, 1, 'Ex.: 29/2020 · estágio · consepe 2015 · orgao:cne ano:2019'],
    ['d1', 'dec', 0, 2, 'Encontrou<br>resultados?'],
    ['n1', 'req', -1, 2, 'Tentar só o número, outra palavra ou o órgão e o ano'],
    ['n1i', 'info', -1, 3, 'Sem resultado: a norma pode não estar no acervo (FAROL10)'],
    ['d2', 'dec', 0, 3, 'Muitos<br>resultados?'],
    ['r', 'req', 1, 3, 'Refinar com prefixos, filtros e Ordenar por'],
    ['f', 'req', 0, 4, 'Clicar no rótulo da norma para abrir a ficha (FAROL03)'],
    ['z', 'end', 0, 5, '']],
  [['s', 'a'], ['a', 'ai'], ['a', 'd1'], ['d1', 'd2', 'Sim'], ['d1', 'n1', 'Não'], ['n1', 'a'], ['n1', 'n1i'],
   ['d2', 'r', 'Sim'], ['d2', 'f', 'Não'], ['r', 'f'], ['f', 'z']]],

  FAROL03: [[
    ['s', 'start', 0, 0, ''],
    ['a', 'req', 0, 1, 'Abrir a ficha pela busca, por um exemplo ou por um link'],
    ['b', 'req', 0, 2, 'Ler a situação de vigência e a base da situação'],
    ['d', 'dec', 0, 3, 'Texto<br>por OCR?'],
    ['o', 'req', 1, 3, 'Conferir números e datas no PDF oficial (Fonte)'],
    ['c', 'req', 0, 4, 'Ver quem a altera, revoga ou supera e em que ela se funda'],
    ['e', 'req', 0, 5, 'Consultar as relações por dispositivo desta norma'],
    ['ei', 'info', 1, 5, 'Irmãs e paralelas são sugestão, não relação normativa'],
    ['f', 'req', 0, 6, 'Abrir o texto integral (FAROL04) ou a Teia (FAROL05)'],
    ['z', 'end', 0, 7, '']],
  [['s', 'a'], ['a', 'b'], ['b', 'd'], ['d', 'o', 'Sim'], ['d', 'c', 'Não'], ['o', 'c'], ['c', 'e'], ['e', 'ei'], ['e', 'f'], ['f', 'z']]],

  FAROL04: [[
    ['s', 'start', 0, 0, ''],
    ['a', 'req', 0, 1, 'Clicar em Ir ao texto integral, na ficha da norma'],
    ['b', 'req', 0, 2, 'Ler na barra a origem do texto e os avisos'],
    ['bi', 'info', 1, 2, 'Texto por OCR: conferir números no PDF oficial'],
    ['c', 'req', 0, 3, 'Ir ao artigo pelo campo Ir ao art.'],
    ['d', 'req', 0, 4, 'Ler sob o caput a anotação de vigência do artigo'],
    ['k', 'dec', 0, 5, 'Texto<br>consolidado?'],
    ['k1', 'req', 1, 5, 'Ler a redação vigente, logo após o trecho tachado'],
    ['k2', 'req', 0, 6, 'Abrir a norma alteradora para ler a redação nova'],
    ['f', 'req', 0, 7, 'Abrir as normas citadas pelos links do texto'],
    ['z', 'end', 0, 8, '']],
  [['s', 'a'], ['a', 'b'], ['b', 'bi'], ['b', 'c'], ['c', 'd'], ['d', 'k'], ['k', 'k1', 'Sim'], ['k', 'k2', 'Não'], ['k1', 'f'], ['k2', 'f'], ['f', 'z']]],

  FAROL05: [[
    ['s', 'start', 0, 0, ''],
    ['a', 'req', 0, 1, 'Abrir a Teia pelo menu ou por Ver na Teia, na ficha'],
    ['d', 'dec', 0, 2, 'A partida é a<br>norma certa?'],
    ['n', 'req', -1, 2, 'Buscar a norma na barra da Teia ou abrir um mapa de exemplo'],
    ['di', 'info', 1, 2, 'Duplo clique num nó ou Tornar partida também trocam a partida'],
    ['c', 'req', 0, 3, 'Ajustar a Direção e a Profundidade da vizinhança'],
    ['e', 'req', 0, 4, 'Clicar num nó para ver a ficha no painel'],
    ['ei', 'info', 1, 4, 'Nós tracejados: normas citadas e ainda sem texto'],
    ['f', 'req', 0, 5, 'Abrir a ficha completa e o texto (FAROL03 e FAROL04)'],
    ['z', 'end', 0, 6, '']],
  [['s', 'a'], ['a', 'd'], ['d', 'c', 'Sim'], ['d', 'n', 'Não'], ['d', 'di'], ['n', 'c'], ['c', 'e'], ['e', 'ei'], ['e', 'f'], ['f', 'z']]],

  FAROL06: [[
    ['s', 'start', 0, 0, ''],
    ['a', 'req', 0, 1, 'Escolher a norma de partida (FAROL05)'],
    ['b', 'req', 0, 2, 'Marcar os filtros: relação, nível, situação, tipo, tema e órgão'],
    ['bi', 'info', 1, 2, 'Os filtros se somam; a norma de partida aparece sempre'],
    ['d1', 'dec', 0, 3, 'Ver por ano<br>e nível?'],
    ['v', 'req', -1, 3, 'Escolher a vista Cronológico-hierárquica'],
    ['d2', 'dec', 0, 4, 'Ver uma data<br>passada?'],
    ['m', 'req', 1, 4, 'Ajustar a Máquina do tempo ou usar o Play'],
    ['mi', 'info', 1, 3, 'Normas que ainda não existiam aparecem tracejadas em azul'],
    ['sv', 'req', 0, 5, 'Salvar o mapa com um nome em Seus mapas'],
    ['svi', 'info', -1, 5, 'Os mapas salvos ficam só neste navegador'],
    ['z', 'end', 0, 6, '']],
  [['s', 'a'], ['a', 'b'], ['b', 'bi'], ['b', 'd1'], ['d1', 'v', 'Sim'], ['d1', 'd2', 'Não'], ['v', 'd2'],
   ['d2', 'm', 'Sim'], ['d2', 'sv', 'Não'], ['m', 'mi'], ['m', 'sv'], ['sv', 'svi'], ['sv', 'z']]],

  FAROL07: [[
    ['s', 'start', 0, 0, ''],
    ['a', 'req', 0, 1, 'Abrir Estatuto e regimentos no menu'],
    ['b', 'req', 0, 2, 'Localizar o quadro: Estatuto, regimentos comuns, minuta ou unidades'],
    ['bi', 'info', 1, 2, 'Minuta do novo Estatuto (NT): sem força normativa'],
    ['d', 'dec', 0, 3, 'A norma tem<br>texto?'],
    ['f', 'req', 1, 3, 'Ver a norma na Fila de coleta (FAROL10)'],
    ['t', 'req', 0, 4, 'Abrir o texto integral e ler as anotações (FAROL04)'],
    ['z', 'end', 0, 5, '']],
  [['s', 'a'], ['a', 'b'], ['b', 'bi'], ['b', 'd'], ['d', 't', 'Sim'], ['d', 'f', 'Não'], ['t', 'z'], ['f', 'z']]],

  FAROL08: [[
    ['s', 'start', 0, 0, ''],
    ['a', 'req', 0, 1, 'Abrir Vigência no menu'],
    ['b', 'req', 0, 2, 'Filtrar a tabela pelo número ou pelo assunto da norma'],
    ['bi', 'info', 1, 2, 'Clique no título da coluna para ordenar'],
    ['d', 'dec', 0, 3, 'Em conflito ou<br>a verificar?'],
    ['c1', 'req', 1, 3, 'Ler as leituras e as fontes em Divergências (FAROL09)'],
    ['c2', 'set', 1, 4, 'Procuradoria Federal ou conselho: decidir qual leitura prevalece'],
    ['e', 'req', 0, 4, 'Ler a base e abrir a norma que altera ou revoga'],
    ['f', 'req', 0, 5, 'Conferir o artigo no texto integral (FAROL04)'],
    ['z', 'end', 0, 6, '']],
  [['s', 'a'], ['a', 'b'], ['b', 'bi'], ['b', 'd'], ['d', 'c1', 'Sim'], ['d', 'e', 'Não'], ['c1', 'c2'], ['c2', 'z'], ['e', 'f'], ['f', 'z']]],

  FAROL09: [[
    ['s', 'start', 0, 0, ''],
    ['a', 'req', 0, 1, 'Abrir Divergências no menu'],
    ['b', 'req', 0, 2, 'Filtrar pela norma, pelo subtipo ou por uma palavra'],
    ['bi', 'info', 1, 2, 'Ex.: CONSUNI 07/2002 · D1- · revogada'],
    ['c', 'req', 0, 3, 'Ordenar por Gravidade e ler a observação e o encaminhamento'],
    ['ci', 'info', -1, 3, 'Legenda das categorias e da gravidade: página Sobre'],
    ['d', 'dec', 0, 4, 'Encontrou erro<br>não registrado?'],
    ['r1', 'req', 1, 4, 'Informar no Atendimento CT – Direção de Centro, com a norma e o trecho'],
    ['r2', 'set', 1, 5, 'Direção do CT: conferir na fonte oficial e registrar a divergência'],
    ['z', 'end', 0, 6, '']],
  [['s', 'a'], ['a', 'b'], ['b', 'bi'], ['b', 'c'], ['c', 'ci'], ['c', 'd'], ['d', 'r1', 'Sim'], ['d', 'z', 'Não'], ['r1', 'r2'], ['r2', 'z']]],

  FAROL10: [[
    ['s', 'start', 0, 0, ''],
    ['a', 'req', 0, 1, 'Abrir Fila no menu'],
    ['b', 'req', 0, 2, 'Filtrar o quadro pelo número, pelo ano ou pelo órgão da norma'],
    ['bi', 'info', 1, 2, 'Fora da fila: normas sem texto fora do escopo da coleta'],
    ['d', 'dec', 0, 3, 'Encontrou<br>a norma?'],
    ['n1', 'req', 1, 3, 'Sugerir a inclusão no Atendimento CT – Direção de Centro'],
    ['n2', 'set', 1, 4, 'Direção do CT: conferir na fonte oficial e incluir na fila de coleta'],
    ['e', 'req', 0, 4, 'Ler a vigência registrada e quantas normas a citam'],
    ['z', 'end', 0, 5, '']],
  [['s', 'a'], ['a', 'b'], ['b', 'bi'], ['b', 'd'], ['d', 'e', 'Sim'], ['d', 'n1', 'Não'], ['n1', 'n2'], ['n2', 'z'], ['e', 'z']]],
};

// conferência: no máximo 4 linhas por caixa (25 caracteres por linha), para não encostar na vizinha
const linhas = t => { let n = 0, c = 0; for (const w of t.split(/\s+/).filter(Boolean)) { if (c === 0) { c = w.length; n++; } else if (c + 1 + w.length <= 25) c += 1 + w.length; else { n++; c = w.length; } } return n; };
const saida = path.join(__dirname, '..', '..', 'docs', 'tutorial', 'fluxogramas');
fs.mkdirSync(saida, { recursive: true });
const json = {};
for (const [cod, [nos, arestas]] of Object.entries(F)) {
  const ids = new Set(nos.map(n => n[0]));
  for (const [a, b] of arestas) if (!ids.has(a) || !ids.has(b)) throw new Error(`${cod}: aresta ${a}→${b} sem nó`);
  const pos = new Set();
  for (const n of nos) {
    const k = n[2] + ':' + n[3]; if (pos.has(k)) throw new Error(`${cod}: dois nós em ${k}`); pos.add(k);
    if (!['start', 'end', 'dec'].includes(n[1]) && linhas(n[4]) > 4) console.warn(`${cod}/${n[0]}: ${linhas(n[4])} linhas`);
  }
  const xml = FB.mxfile(cod, FB.build(nos, arestas));
  fs.writeFileSync(path.join(saida, cod + '.drawio'), xml);
  json[cod] = xml;
}
fs.writeFileSync(path.join(saida, 'fluxos.json'), JSON.stringify(json));
console.log(Object.keys(json).length, 'fluxogramas em', saida);

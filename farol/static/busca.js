// Busca do Farol: índice estático (dados/fichas.json) consultado no navegador.
(function(){
const $=id=>document.getElementById(id);
const norm=s=>(s||'').normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase();
const SIT={vigente:'vigente',alterada:'alterada',revogada:'revogada',nao_localizada:'não localizada',tramitacao:'em tramitação',conflito:'conflito de vigência',verificar:'a verificar',desconhecida:'situação não registrada'};
const SITKEY={vigente:'vigente',alterada:'alterada',revogada:'revogada','nao localizada':'nao_localizada',fantasma:'nao_localizada','em tramitacao':'tramitacao',tramitacao:'tramitacao',conflito:'conflito',verificar:'verificar'};
const LEVELS=['N1','N2','N3','N4','N5','N6','N7','N8','N9','N10','NT','MA','?'];
const LVLNAME={N1:'Constituição',N2:'Leis',N3:'Decretos',N4:'MEC e órgãos federais',N5:'Estatuto',N6:'Regimentos comuns',N7:'Conselhos superiores',N8:'Regimentos de unidades',N9:'Conselhos de centro e colegiados',N10:'Reitoria e pró-reitorias',NT:'Em tramitação',MA:'Material de apoio','?':'Nível não identificado'};
const raiz=document.querySelector('link[rel=stylesheet][href$="farol.css"]').getAttribute('href').replace('assets/farol.css','');
let IDX=[];
function parseQuery(txt){const c={toks:[],org:'',niv:'',ano1:0,ano2:0,sit:'',tema:'',num:''};
  norm(txt.trim()).split(/\s+/).filter(Boolean).forEach(t=>{const m=t.match(/^(orgao|org|ano|nivel|n|tema|situacao|sit|num|numero):(.+)$/);
    if(!m){c.toks.push(t);return;}const k=m[1],v=m[2];
    if(k==='orgao'||k==='org')c.org=v;else if(k==='ano'){const r=v.match(/^(\d{4})(?:-(\d{4}))?$/);if(r){c.ano1=+r[1];c.ano2=+(r[2]||r[1]);}}
    else if(k==='nivel'||k==='n')c.niv=v.toUpperCase().replace(/^(\d)/,'N$1');else if(k==='tema')c.tema=v;else if(k==='situacao'||k==='sit')c.sit=SITKEY[v]||v;else c.num=v;});
  c.toks=c.toks.filter(t=>{if(/^(19|20)\d\d$/.test(t)&&!c.ano1){c.ano1=c.ano2=+t;return false;}return true;});
  return c;}
function criterios(){const c=parseQuery($('q').value);
  if($('fOrg').value)c.org=norm($('fOrg').value);if($('fNiv').value)c.niv=$('fNiv').value;
  if(+$('fAno1').value)c.ano1=+$('fAno1').value;if(+$('fAno2').value)c.ano2=+$('fAno2').value;
  if($('fSit').value)c.sit=$('fSit').value;if($('fTema').value)c.tema=$('fTema').value;c.col=$('fCol').value;c.ord=$('fOrd').value;return c;}
function run(c){let hits=IDX.filter(x=>{const n=x.n;
    if(c.toks.length&&!c.toks.every(k=>x.k.includes(k)))return false;
    if(c.org&&!norm(n.o).includes(c.org))return false;
    if(c.niv&&n.nv!==c.niv)return false;
    if(c.ano1&&(!x.yr||x.yr<c.ano1))return false;if(c.ano2&&(!x.yr||x.yr>c.ano2))return false;
    if(c.sit&&n.s!==c.sit)return false;
    if(c.tema&&!n.t.some(t=>norm(t).includes(norm(c.tema))))return false;
    if(c.num&&!norm(n.n).includes(c.num)&&!norm(n.l).includes(c.num))return false;
    if(c.col==='texto'&&n.g)return false;if(c.col==='fantasma'&&!n.g)return false;return true;});
  if(c.ord==='data')hits.sort((a,b)=>(b.n.d||'').localeCompare(a.n.d||''));else if(c.ord==='datao')hits.sort((a,b)=>(a.n.d||'z').localeCompare(b.n.d||'z'));
  else if(c.ord==='nome')hits.sort((a,b)=>a.n.l.localeCompare(b.n.l,'pt'));else hits.sort((a,b)=>(b.n.g?0:1)-(a.n.g?0:1)||(b.n.deg-a.n.deg));
  return hits;}
function esc(s){return (s||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
function show(){if(!IDX.length)return;const c=criterios();const vazio=!c.toks.length&&!c.org&&!c.niv&&!c.ano1&&!c.sit&&!c.tema&&!c.num&&!c.col;
  const hits=vazio?[]:run(c);
  $('cnt').textContent=vazio?`${IDX.length.toLocaleString('pt-BR')} normas no índice. Digite algo ou escolha um filtro.`:`${hits.length.toLocaleString('pt-BR')} norma${hits.length===1?'':'s'} encontrada${hits.length===1?'':'s'}${hits.length>60?' · mostrando 60':''}`;
  $('res').innerHTML=hits.slice(0,60).map(x=>{const n=x.n;return `<div class="r"><a href="${raiz}norma/${n.id.replace(/\?/g,'_')}/">${esc(n.l)}</a> <span class="hint">${n.nv} · ${esc(n.o||'?')} · ${n.dy||'s/ data'} · ${SIT[n.s]||n.s}${n.g?' · sem texto':''}</span><div class="e">${esc(n.e||'(sem ementa no acervo)')}</div></div>`;}).join('');}
fetch(raiz+'dados/fichas.json').then(r=>r.json()).then(D=>{
  IDX=D.nodes.map(n=>({n,k:norm(n.l+' '+n.id.replace(/-/g,' ')+' '+n.e+' '+n.o+' '+n.n+' '+n.t.join(' ')),yr:+n.dy||0}));
  const orgs=new Map(),temas=new Map();D.nodes.forEach(n=>{if(n.o)orgs.set(n.o,(orgs.get(n.o)||0)+1);n.t.forEach(t=>temas.set(t,(temas.get(t)||0)+1));});
  [...orgs].sort((a,b)=>b[1]-a[1]).forEach(([o,c])=>$('fOrg').insertAdjacentHTML('beforeend',`<option value="${esc(o)}">${esc(o)} (${c})</option>`));
  LEVELS.forEach(l=>$('fNiv').insertAdjacentHTML('beforeend',`<option value="${l}">${l} · ${LVLNAME[l]}</option>`));
  Object.keys(SIT).forEach(k=>$('fSit').insertAdjacentHTML('beforeend',`<option value="${k}">${SIT[k]}</option>`));
  [...temas].sort((a,b)=>b[1]-a[1]).forEach(([t,c])=>$('fTema').insertAdjacentHTML('beforeend',`<option value="${esc(t)}">${esc(t)} (${c})</option>`));
  const q=new URLSearchParams(location.search).get('q');if(q)$('q').value=q;
  show();$('q').focus();
}).catch(e=>{$('cnt').textContent='Não foi possível carregar o índice: '+e;});
$('q').addEventListener('input',show);
['fOrg','fNiv','fSit','fTema','fCol','fOrd'].forEach(id=>$(id).addEventListener('change',show));
['fAno1','fAno2'].forEach(id=>$(id).addEventListener('input',show));
})();

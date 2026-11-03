// Busca do Farol: índice estático (dados/fichas.json) consultado no navegador.
// Filtros de seleção múltipla (static/multisel.js); resultados das normas mais novas para as mais antigas.
(function(){
const $=id=>document.getElementById(id);
const norm=s=>(s||'').normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase();
const SIT={vigente:'vigente',alterada:'alterada',revogada:'revogada',nao_localizada:'não localizada',tramitacao:'em tramitação',conflito:'conflito de vigência',verificar:'a verificar',desconhecida:'situação não registrada'};
const SITKEY={vigente:'vigente',alterada:'alterada',revogada:'revogada','nao localizada':'nao_localizada',fantasma:'nao_localizada','em tramitacao':'tramitacao',tramitacao:'tramitacao',conflito:'conflito',verificar:'verificar'};
const LEVELS=['N1','N2','N3','N4','N5','N6','N7','N8','N9','N10','NT','MA','?'];
const LVLNAME={N1:'Constituição',N2:'Leis',N3:'Decretos',N4:'MEC e órgãos federais',N5:'Estatuto',N6:'Regimentos comuns',N7:'Conselhos superiores',N8:'Regimentos de unidades',N9:'Conselhos de centro e colegiados',N10:'Reitoria e pró-reitorias',NT:'Em tramitação',MA:'Material de apoio','?':'Nível não identificado'};
const raiz=document.querySelector('link[rel=stylesheet][href$="farol.css"]').getAttribute('href').replace('assets/farol.css','');
let IDX=[];const MS={};
function parseQuery(txt){const c={toks:[],org:'',niv:'',ano1:0,ano2:0,sit:'',tema:'',num:''};
  norm(txt.trim()).split(/\s+/).filter(Boolean).forEach(t=>{const m=t.match(/^(orgao|org|ano|nivel|n|tema|situacao|sit|num|numero):(.+)$/);
    if(!m){c.toks.push(t);return;}const k=m[1],v=m[2];
    if(k==='orgao'||k==='org')c.org=v;else if(k==='ano'){const r=v.match(/^(\d{4})(?:-(\d{4}))?$/);if(r){c.ano1=+r[1];c.ano2=+(r[2]||r[1]);}}
    else if(k==='nivel'||k==='n')c.niv=v.toUpperCase().replace(/^(\d)/,'N$1');else if(k==='tema')c.tema=v;else if(k==='situacao'||k==='sit')c.sit=SITKEY[v]||v;else c.num=v;});
  c.toks=c.toks.filter(t=>{if(/^(19|20)\d\d$/.test(t)&&!c.ano1){c.ano1=c.ano2=+t;return false;}return true;});
  return c;}
function criterios(){const c=parseQuery($('q').value);
  if(+$('fAno1').value)c.ano1=+$('fAno1').value;if(+$('fAno2').value)c.ano2=+$('fAno2').value;
  c.ord=$('fOrd').value;return c;}
function filtrosAtivos(){return Object.values(MS).some(m=>!m.todos());}
function run(c){let hits=IDX.filter(x=>{const n=x.n;
    if(c.toks.length&&!c.toks.every(k=>x.k.includes(k)))return false;
    if(c.org&&!norm(n.o).includes(c.org))return false;
    if(c.niv&&n.nv!==c.niv)return false;
    if(c.ano1&&(!x.yr||x.yr<c.ano1))return false;if(c.ano2&&(!x.yr||x.yr>c.ano2))return false;
    if(c.sit&&n.s!==c.sit)return false;
    if(c.tema&&!n.t.some(t=>norm(t).includes(norm(c.tema))))return false;
    if(c.num&&!norm(n.n).includes(c.num)&&!norm(n.l).includes(c.num))return false;
    if(!MS.org.aceita(n.o||'?'))return false;if(!MS.niv.aceita(n.nv))return false;if(!MS.sit.aceita(n.s))return false;
    if(!MS.tema.aceitaAlgum(n.t))return false;if(!MS.col.aceita(n.g?'fantasma':'texto'))return false;return true;});
  if(c.ord==='rel')hits.sort((a,b)=>(b.n.g?0:1)-(a.n.g?0:1)||(b.n.deg-a.n.deg));
  else if(c.ord==='datao')hits.sort((a,b)=>(a.n.d||'z').localeCompare(b.n.d||'z'));
  else if(c.ord==='nome')hits.sort((a,b)=>a.n.l.localeCompare(b.n.l,'pt'));
  else hits.sort((a,b)=>(b.n.d||'').localeCompare(a.n.d||'')||(b.n.g?0:1)-(a.n.g?0:1)||(b.n.deg-a.n.deg));  // mais novas primeiro
  return hits;}
function esc(s){return (s||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
function show(){if(!IDX.length)return;const c=criterios();const vazio=!c.toks.length&&!c.org&&!c.niv&&!c.ano1&&!c.sit&&!c.tema&&!c.num&&!filtrosAtivos();
  const hits=vazio?[]:run(c);
  $('cnt').textContent=vazio?`${IDX.length.toLocaleString('pt-BR')} normas no índice. Digite algo ou escolha um filtro.`:`${hits.length.toLocaleString('pt-BR')} norma${hits.length===1?'':'s'} encontrada${hits.length===1?'':'s'}${hits.length>60?' · mostrando 60':''}`;
  $('res').innerHTML=hits.slice(0,60).map(x=>{const n=x.n;return `<div class="r"><a href="${raiz}norma/${n.id.replace(/\?/g,'_')}/">${esc(n.l)}</a> <span class="hint">${n.nv} · ${esc(n.o||'?')} · ${n.dy||'s/ data'} · ${SIT[n.s]||n.s}${n.g?' · sem texto':''}</span><div class="e">${esc(n.e||'(sem ementa no acervo)')}</div></div>`;}).join('');}
fetch(raiz+'dados/fichas.json').then(r=>r.json()).then(D=>{
  IDX=D.nodes.map(n=>({n,k:norm(n.l+' '+n.id.replace(/-/g,' ')+' '+n.e+' '+n.o+' '+n.n+' '+n.t.join(' ')),yr:+n.dy||0}));
  const orgs=new Map(),temas=new Map(),niv=new Map(),sit=new Map();let comTexto=0,semTexto=0;
  D.nodes.forEach(n=>{orgs.set(n.o||'?',(orgs.get(n.o||'?')||0)+1);n.t.forEach(t=>temas.set(t,(temas.get(t)||0)+1));niv.set(n.nv,(niv.get(n.nv)||0)+1);sit.set(n.s,(sit.get(n.s)||0)+1);n.g?semTexto++:comTexto++;});
  MS.org=MultiSel('fOrg',{nome:'órgão',plural:'órgãos',opcoes:[...orgs].sort((a,b)=>b[1]-a[1]).map(([o,c])=>({v:o,l:o,n:c})),aoMudar:show});
  MS.niv=MultiSel('fNiv',{nome:'nível',plural:'níveis',opcoes:LEVELS.filter(l=>niv.get(l)).map(l=>({v:l,l:`${l} · ${LVLNAME[l]}`,n:niv.get(l)})),aoMudar:show});
  MS.sit=MultiSel('fSit',{nome:'situação',plural:'situações',rotuloTodos:'Todas as situações',opcoes:Object.keys(SIT).filter(k=>sit.get(k)).map(k=>({v:k,l:SIT[k],n:sit.get(k)})),aoMudar:show});
  MS.tema=MultiSel('fTema',{nome:'tema',plural:'temas',opcoes:[...temas].sort((a,b)=>b[1]-a[1]).map(([t,c])=>({v:t,l:t,n:c})),aoMudar:show});
  MS.col=MultiSel('fCol',{nome:'opção',plural:'opções',rotuloTodos:'Com e sem texto',opcoes:[{v:'texto',l:'com texto no acervo',n:comTexto},{v:'fantasma',l:'só citada (sem texto)',n:semTexto}],aoMudar:show});
  const q=new URLSearchParams(location.search).get('q');if(q)$('q').value=q;
  show();$('q').focus();
}).catch(e=>{$('cnt').textContent='Não foi possível carregar o índice: '+e;});
$('q').addEventListener('input',show);
$('fOrd').addEventListener('change',show);
['fAno1','fAno2'].forEach(id=>$(id).addEventListener('input',show));
$('fLimpar').addEventListener('click',()=>{Object.values(MS).forEach(m=>m.reset());$('fAno1').value='';$('fAno2').value='';$('fOrd').value='data';show();});
})();

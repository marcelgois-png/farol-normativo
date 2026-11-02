"""Rodada 5: páginas oficiais (planalto.gov.br e Câmara dos Deputados) -> fichas, textos e relações.

Entradas (W = pasta de trabalho):
  W/orig/FEDERAL/<ID>__planalto.html, <ID>__planalto-compilado.html   (planalto)
  W/orig/FEDERAL/<ID>__camara-norma.html, <ID>__camara-original.html  (Câmara, atos que o planalto não publica)
  W/manifestos/*.tsv  (nome, bytes, sha256, content-type, url, data)
Saída: W/saida/r5_nos.json, r5_rel.json, r5_txt.json, r5_alertas.json

Regras (mesmas das Rodadas 2–4):
- Texto: versão compilada do planalto quando existir; ~~tachado~~ marca redação revogada ou alterada.
  O extrator lê o texto SEM os trechos tachados (citações da redação vigente e as anotações
  "(Redação dada pela Lei…)", "(Revogado pela…)", que viram relações alteradora -> esta norma).
- Relações agregadas por (origem, destino, tipo), com os dispositivos listados e o número de
  ocorrências, como na Rodada 2.
- Bloqueio hierárquico: norma de nível inferior não altera nem revoga superior (vira REMETE A).
- A epígrafe tem de conferir com o ID (número e ano); se não conferir, o arquivo é descartado
  e a citação vai para conferência.
"""
import csv, glob, hashlib, json, os, re, sys, unicodedata, collections
from bs4 import BeautifulSoup, NavigableString

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))           # scripts/extrator.py
sys.path.insert(0, os.path.join(AQUI, "..", "r3"))     # scripts/r3/camara_r3.py
from extrator import extrai, prepara
import camara_r3

csv.field_size_limit(10**9)
REPO = os.path.abspath(os.path.join(AQUI, "..", ".."))
W = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/r5"
HOJE = "2026-11-02"
NFC = lambda s: unicodedata.normalize("NFC", s)
MESES = camara_r3.MESES

N = {r["id"]: r for r in csv.DictReader(open(f"{REPO}/base/nos.csv", encoding="utf-8"))}
inv = set(N)

def nivel(i):
    if i == "BR-CF-1988" or i.startswith("BR-EC-"): return "N1"
    if re.match(r"(BR|PB)-(LEI|LC|DL|MP|LDEL)-", i): return "N2"
    if re.match(r"BR-(DEC|DLG)-", i): return "N3" if i.startswith("BR-DEC") else "N2"
    if i.startswith(("BR-", "PB-")): return "N4"
    if re.match(r"UFPB-(CONSEPE|CONSUNI|CURADOR)-RES-", i): return "N7"
    if re.match(r"UFPB-[A-Z]+-PORT-", i): return "N10"
    return "N9"

TIPO = {"LEI": "Lei", "LC": "Lei Complementar", "DEC": "Decreto", "DL": "Decreto-Lei", "EC": "Emenda Constitucional",
        "MP": "Medida Provisória", "LDEL": "Lei Delegada", "DLG": "Decreto Legislativo"}
EPI_RE = re.compile(r"(?i)(LEI\s+COMPLEMENTAR|LEI\s+DELEGADA|DECRETO[\s-]*LEI|DECRETO\s+LEGISLATIVO|DECRETO|EMENDA\s+CONSTITUCIONAL|MEDIDA\s+PROVIS[ÓO]RIA|LEI)"
                    r"\s*N\s*[º°oO.]*\s*([\d.]+(?:-[A-Z])?)\s*,?\s*(?:DE\s+)?(\d{1,2})[º°o]?\s*(?:DE\s+)?([A-ZÇa-zç]+)\s+(?:DE\s+)?(\d{4})\.?")
PREAMB_RE = re.compile(r"(?:O\s+PRESIDENTE|A\s+PRESIDENTA|O\s+VICE[-\s]PRESIDENTE|AS\s+MESAS|As\s+Mesas|O\s+CONGRESSO|Fa[çc]o\s+saber|OS\s+MINISTROS|O\s+CHEFE\s+DO\s+GOVERNO|O\s+PRESIDENTE\s+DA\s+REP|Art\.?\s*1\s*[º°o.]?\s)")
ATO = r"(?:MPv|Lei\s+Complementar|Lei\s+Delegada|Lei|Decreto[\s-]*Lei|Decreto\s+Legislativo|Decreto|Medida\s+Provis[óo]ria|Emenda\s+Constitucional)"
NUM = r"n?\s*[º°o.]*\s*[\d.]+(?:-\d+)?(?:\s*,\s*(?:de\s+)?[\d.]+(?:\s+de\s+[A-Za-zç]+\s+de\s+\d{4})?)?"
EXC = r"(?:excetuand\w*|ressalv\w*|salvo|exceto)[^()]{0,60}?(?:art\.\s*\d+[º°]?(?:\s+e\s+seus?\s+§§?\s*[\dº°]+(?:\s*(?:,|e)\s*[\dº°]+)*)?|§§?\s*[\dº°]+(?:\s*(?:,|e)\s*[\dº°]+)*)"
NOTAS_RE = re.compile(r"(?i)\(?\s*(?:Texto\s+compilado|Texto\s+para\s+impress[ãa]o|Mensagem\s+de\s+veto|Mensagem\s+de\s+Veto\s+Total|\(?Vig[êe]ncia\)?(?:\s+encerrada)?|Regulamento|Produ[çc][ãa]o\s+de\s+efeitos?|"
                      r"Promulga[çc][ãa]o\s+partes?\s+vetadas?|Partes?\s+vetadas?|Exposi[çc][ãa]o\s+de\s+motivos|Convers[ãa]o\s+d[ao]\s+" + ATO + r"\s*" + NUM + r"|"
                      r"Convertid[oa]\s+n[ao]\s+" + ATO + r"\s*" + NUM + r"|Revogad[oa]s?\s+(?:parcialmente\s+)?pel[oa]s?\s+" + ATO + r"\s*" + NUM + r"(?:\s*,?\s*" + EXC + r")?|"
                      r"Revigorad[oa]s?\s+pel[oa]s?\s+" + ATO + r"\s*" + NUM + r"|Rejeitad[oa]\s+pel[oa]\s+Ato\s+Declarat[óo]rio[^()]{0,40}?\d{4}|"
                      r"(?<=\()\s*(?:Vide|Retificad[oa]|Republicad[oa]|Atualiza[çc][ãa]o|Em\s+vigor|Efic[áa]cia|Ref\.?)[^()]{0,200}"
                      r"|Vide\s+(?:" + ATO + r"|ADI|ADC|ADPF|art|Resolu[çc][ãa]o|Ato\s+Declarat[óo]rio|Portaria|Instru[çc][ãa]o\s+Normativa|Parecer)[^()]{0,40}?" + r"\d+(?:\s*(?:,|e)\s*\d+)*(?:\s*,?\s*de\s+\d{1,2}\s+de\s+[a-zç]+\s+de\s+\d{4})?(?:\s+do\s+Ato\s+das\s+Disposi[çc][õo]es\s+Constitucionais(?:\s+e)?\s+Transit[óo]rias)?(?=\s)"
                      r")\s*\)?")
def dec(b):
    for enc in ("utf-8", "cp1252", "latin-1"):
        try:
            return b.decode(enc)
        except Exception:
            pass
    return b.decode("utf-8", "replace")

def html_texto(html, tachado=True):
    """Texto do HTML do planalto. tachado=True marca ~~redação revogada~~; False a remove."""
    soup = BeautifulSoup(html, "lxml")
    for t in soup(["script", "style", "head"]):
        t.decompose()
    for t in soup.find_all(["strike", "s", "del"]):
        inner = t.get_text(" ", strip=True)
        t.replace_with(NavigableString((f" ~~{inner}~~ " if inner else " ") if tachado else " "))
    for t in soup.find_all(list(camara_r3.BLOCO)):
        t.insert_before(NavigableString("\n")); t.insert_after(NavigableString("\n"))
    tx = soup.get_text().replace("\xa0", " ")
    tx = re.sub(r"[ \t]+", " ", tx)
    tx = re.sub(r" *\n *", "\n", tx)
    tx = re.sub(r"\n{3,}", "\n\n", tx)
    return NFC(tx.strip())

def fracao_tachada(html):
    soup = BeautifulSoup(html, "lxml")
    tot = len(soup.get_text(" ", strip=True)) or 1
    st = sum(len(t.get_text(" ", strip=True)) for t in soup.find_all(["strike", "s", "del"]))
    return st / tot

def num_id(i):
    m = re.match(r"^BR-([A-Z]+)-(\d+)([A-Z]?)-(\d{4})$", i)
    return (m.group(1), int(m.group(2)), m.group(4)) if m else (None, None, None)

def ficha_planalto(i, txt):
    """Epígrafe, data, ementa e notas do topo. txt: texto da página com os trechos tachados mantidos (sem marcas)."""
    tp, n, ano = num_id(i)
    f = dict(epigrafe="", data="", ementa="", notas="", confere=False)
    t = re.sub(r"\s+", " ", txt[:12000])
    m = EPI_RE.search(t)
    if not m:
        return f
    nn = int(m.group(2).replace(".", "").split("-")[0])
    f["epigrafe"] = m.group(0).strip().rstrip(".")
    mes = m.group(4).lower().replace("ç", "c")
    mm = MESES.get(mes, 0) or MESES.get(m.group(4).lower(), 0)
    f["data"] = f"{m.group(5)}-{mm:02d}-{int(m.group(3)):02d}" if mm else m.group(5)
    f["confere"] = (nn == n and m.group(5) == ano)
    resto = t[m.end():]
    p = PREAMB_RE.search(resto)
    cab = resto[:p.start()] if p else resto[:1200]
    notas = [x.group(0).strip() for x in NOTAS_RE.finditer(cab)]
    em = NOTAS_RE.sub(" ", cab)
    em = re.sub(r"\(\s*\)", " ", em)
    em = re.sub(r"\s+", " ", em).strip(" .;,-()")
    em = re.sub(r"^(?:e|l)\s+(?=[A-ZÁÉÍÓÚ])", "", em)
    f["ementa"] = em[:700]
    f["notas"] = " ".join(notas)
    f["cab"] = cab
    f["antes"] = t[:m.start()]
    return f

def situacao_notas(i, notas, frac):
    s = notas
    if re.search(r"(?i)Revigorad[oa]", s):
        return "", "revogação seguida de revigoramento indicada na página do planalto (" + re.sub(r"\s+", " ", re.search(r"(?i)Revogad[^()]{0,120}Revigorad[^()]{0,80}|Revigorad[^()]{0,80}", s).group(0)).strip() + "); conferir"
    rj = re.search(r"(?i)Rejeitad[oa]\s+pel[oa]\s+Ato\s+Declarat[óo]rio[^()]{0,40}?\d{4}", s)
    if rj:
        return "", f"{re.sub(r'\s+', ' ', rj.group(0)).strip()} — decreto-lei rejeitado pelo Congresso Nacional (nota da página do planalto)"
    rp = re.search(r"(?i)Revogad[oa]\s+pel[oa]s?\s+(" + ATO + r"\s*" + NUM + r")\s*,?\s*(" + EXC + r")", s)
    if rp:
        return "revogada parcialmente", f"revogada por {re.sub(r'\s+', ' ', rp.group(1))}, {re.sub(r'\s+', ' ', rp.group(2)).strip()} (nota da página do planalto)"
    m = re.search(r"(?i)Revogad[oa]\s+pel[oa]s?\s+(" + ATO + r"\s*" + NUM + r")", s)
    if m and not re.search(r"(?i)Revogad[oa]s?\s+parcialmente", m.group(0)):
        return "revogada", f"revogada por {re.sub(r'\s+', ' ', m.group(1))} (nota da página do planalto)"
    c = re.search(r"(?i)Convertid[oa]\s+n[ao]\s+(" + ATO + r"\s*" + NUM + r")", s)
    if i.startswith("BR-MP-") and c:
        return "", f"medida provisória convertida na {re.sub(r'\s+', ' ', c.group(1))} (nota da página do planalto)"
    if frac > 0.85:
        if i.startswith("BR-MP-"):
            return "", f"texto integralmente tachado na página oficial ({frac:.0%}): medida provisória sem eficácia ou convertida em lei"
        return "revogada", f"texto integralmente tachado na página oficial ({frac:.0%} do texto)"
    return "", ""

# ------------------------------------------------------------------ manifestos
man = {}
for f in glob.glob(f"{W}/manifestos/*.tsv"):
    for ln in open(f, encoding="utf-8"):
        p = ln.rstrip("\n").split("\t")
        if len(p) >= 5:
            man[p[0]] = dict(bytes=p[1], sha256=p[2], ct=p[3], url=p[4])

pasta = f"{W}/orig/FEDERAL"
ids = sorted({x.split("__")[0] for x in os.listdir(pasta) if x.endswith(".html")})
NOS, TXT, ALERTA = {}, {}, collections.defaultdict(list)
REL = collections.OrderedDict()
CTRL_D86 = collections.Counter()

REVOG_ART_RE = re.compile(r"(?i)^\s*Art\.?\s*\d+[º°o.]*\s*[-–—.]?\s*(?:Revogam[-\s]se|Ficam?\s+revogad[oa]s?|Revoga[-\s]se|S[ãa]o\s+revogad[oa]s|Fica\s+revogad[oa])")
ART_RE = re.compile(r"(?m)^\s*Art\.?\s*\d+")

def efeito(cab):
    """Data de início de efeito da revogação ("Ficam revogados, a partir de 1º de janeiro de 2033:")."""
    m = re.search(r"(?i)a\s+partir\s+de\s+(\d{1,2})\s*[º°o]?\s+de\s+([a-zç]+)\s+de\s+(\d{4})", re.sub(r"\s+", " ", cab))
    if not m: return ""
    mm = MESES.get(m.group(2).lower(), 0)
    return f"{m.group(3)}-{mm:02d}-{int(m.group(1)):02d}" if mm else m.group(3)

def spans_revogacao(t):
    """D86/P2: trechos de artigos cuja cláusula é de revogação ("Revogam-se:", "Ficam revogados:")."""
    ps = [m.start() for m in ART_RE.finditer(t)] + [len(t)]
    out = []
    for a, b in zip(ps, ps[1:]):
        if REVOG_ART_RE.match(t[a:a + 200]):
            # o artigo termina no próximo artigo, no fecho ("Brasília, …") ou no primeiro anexo
            f = re.search(r"(?m)^\s*(?:Bras[íi]lia\s*,|Rio\s+de\s+Janeiro\s*,|ANEXO\b|Anexo\s+[IVXLC\d]+\b)", t[a:b])
            out.append((a, a + f.start() if f else b, efeito(t[a:a + 300])))
    return out

ITEM_SEP = re.compile(r"[;:]|\n\s*(?=(?:[IVXLC]+|\d+)\s*[-–—]|[a-z]\)|Art\.?\s*\d|§)|\.\s+(?=[A-ZÁÉÍÓÚ])")
DISP_ITEM = re.compile(r"(?i)§|\b(arts?\.?|artigos?|par[áa]grafos?|incisos?|al[íi]neas?|caput|dispositivos?|anexos?|itens?|tabelas?|cap[íi]tulos?|t[íi]tulos?|se[çc][ãa]o)\b")
NAO_ITEM = re.compile(r"(?i)\(\s*vide|\bvide\b|com\s+as\s+altera[çc][õo]es|\b(?:acrescentad|renumerad|introduzid|inclu[íi]d|transformad|convertid)[oa]s?\b|reda[çc][ãa]o\s+dada|\b(altera|alterad[oa]|disp[õo]e|institui|cria|regulament|nos\s+termos|de\s+que\s+trata|prevista?|conforme|com\s+a\s+reda[çc][ãa]o)\b")

def d86(T, x, ano_o):
    """Decide se a citação em artigo de revogação é REVOGA (total/parcial). Devolve (tipo, disp_destino) ou None."""
    m = re.search(r"-(\d{4})$", x["destino"])
    if m and int(m.group(1)) > ano_o:
        return None                      # norma anterior não revoga posterior
    pos = x["pos"]
    ini = max([mm.end() for mm in ITEM_SEP.finditer(T, max(0, pos - 400), pos)] + [max(0, pos - 400)])
    item = re.sub(r"\s+", " ", T[ini:pos]).strip()
    # o caput do próprio artigo de revogação não é dispositivo do destino
    item = re.sub(r"(?i)^Art\.?\s*\d+[º°o.]*\s*[-–—.]?\s*(?:Revogam[-\s]se|Ficam?\s+revogad[oa]s?|Revoga[-\s]se|S[ãa]o\s+revogad[oa]s|Fica\s+revogad[oa])\s*,?\s*", "", item)
    if NAO_ITEM.search(item) or len(item) > 220:
        return None
    if DISP_ITEM.search(item) or x["destino"] == "BR-CF-1988":
        dd = x.get("disp_destino") or "norma inteira"
        limpo = re.sub(r"(?i)^(?:[IVXLC]+\s*[-–—]\s*|[a-z]\)\s*)?(?:e\s+)?(?:o|a|os|as)\s+", "", item).strip(" ,;")
        limpo = re.sub(r"(?i)\s*(?:,?\s*tod[oa]s\s+)?(?:d[oa]s?|n[oa]s?)\s*$", "", limpo).strip(" ,;")
        _fim = re.search(r"\d{4}\s*[,:;]?", T[pos:pos + 160])
        if re.search(r"(?i)seguintes\s+dispositivos", limpo) and _fim:
            dep = T[pos + _fim.end():pos + _fim.end() + 600]
            fimlista = re.search(r"\n\s*[IVXLC]+\s*[-–—]|\n\s*Art\.", dep)
            dep = re.sub(r"\s+", " ", dep[:fimlista.start()] if fimlista else dep[:250]).strip(" :;")
            dd = ("seguintes dispositivos: " + dep)[:220]
        elif dd == "norma inteira" or len(DISP_ITEM.findall(limpo)) > 1:
            dd = limpo[:220] or "dispositivos listados"
        return ("REVOGA (parcial)", dd)
    return ("REVOGA (total)", "norma inteira")

def junta_rel(i, x, dominio):
    """Acumula relação agregada por (origem, destino, tipo)."""
    o, d, tp = x["origem"], x["destino"], x["tipo"]
    if o == d or d.endswith("-?") and False:
        return
    if tp in ("ALTERA", "REVOGA (total)", "REVOGA (parcial)") and nivel(d) < nivel(o):
        tp = "REMETE A"; x["obs"] = (x.get("obs", "") + " bloqueio hierárquico").strip()
    k = (o, d, tp)
    r = REL.get(k)
    do = x.get("disp_origem") or "norma inteira"; dd = x.get("disp_destino") or "norma inteira"
    if not r:
        REL[k] = dict(origem=o, destino=d, tipo=tp, disp_origem=[do], disp_destino=[dd], natureza=x.get("natureza", ""),
                      base=f"texto ({dominio})", confianca=x.get("confianca", ""), parte=x.get("parte", ""),
                      fonte_texto=dominio, citacao=x.get("citacao", ""), ressalva=x.get("ressalva", ""),
                      trecho=(x.get("trecho") or "")[:600], inicio_efeito=x.get("inicio_efeito", ""), obs_lst=[x.get("obs", "")] if x.get("obs") else [],
                      anot=x.get("parte") == "anotação de consolidação", texto_de=i, n=1)
    else:
        r["n"] += 1
        if do not in r["disp_origem"]: r["disp_origem"].append(do)
        if dd not in r["disp_destino"]: r["disp_destino"].append(dd)
        if x.get("obs") and x["obs"] not in r["obs_lst"]: r["obs_lst"].append(x["obs"])
        if r["confianca"] != "alta" and x.get("confianca") == "alta": r["confianca"] = "alta"

for i in ids:
    tp, n, ano = num_id(i)
    pp, pc = f"{pasta}/{i}__planalto.html", f"{pasta}/{i}__planalto-compilado.html"
    cn, co = f"{pasta}/{i}__camara-norma.html", f"{pasta}/{i}__camara-original.html"
    if os.path.exists(pp):
        h_main = dec(open(pp, "rb").read())
        src = pc if os.path.exists(pc) else pp
        if src == pc:
            fc = ficha_planalto(i, html_texto(dec(open(pc, "rb").read()), True).replace("~~", " "))
            if not fc["confere"]:
                ALERTA["compilado de outra norma (usada a página principal)"].append([i, fc["epigrafe"]]); src = pp
        h = dec(open(src, "rb").read()) if src != pp else h_main
        txt = html_texto(h, True); sem = html_texto(h, False)
        f = ficha_planalto(i, html_texto(h_main, True).replace("~~", " "))
        if not f["confere"]:
            ALERTA["epígrafe não confere com o ID (descartado)"].append([i, f["epigrafe"]]); continue
        frac = fracao_tachada(h)
        sit, sit_base = situacao_notas(i, f.get("cab", "") + " " + f.get("antes", ""), fracao_tachada(h_main))
        nome = os.path.basename(src); mf = man.get(nome, {}); mm = man.get(os.path.basename(pp), {})
        dominio = "planalto.gov.br"
        NOS[i] = dict(id=i, tipo=TIPO.get(tp, ""), orgao="Presidência da República" if tp in ("LEI", "LC", "DEC", "DL", "MP", "LDEL") else "Congresso Nacional",
                      numero=f"{n}/{ano}", data=f["data"], ementa=f["ementa"], nivel=nivel(i),
                      situacao=sit, situacao_base=sit_base,
                      status_coleta="texto integral (planalto.gov.br)",
                      metodo_texto="HTML oficial do planalto.gov.br convertido em texto; ~~tachado~~ = redação revogada ou alterada",
                      fonte=mm.get("url", ""), fonte_arquivo=mf.get("url", ""), arquivo_local=f"originais_r5/FEDERAL/{nome}",
                      texto_acervo=f"textos/FEDERAL/{i}.md", data_coleta=HOJE, sha256=mf.get("sha256", ""),
                      epigrafe=f["epigrafe"], notas_topo=f["notas"], fracao_tachada=round(frac, 3),
                      compilado=src == pc, url_compilado=mf.get("url", "") if src == pc else "",
                      versao="compilada (planalto)" if src == pc or "compil" in mm.get("url", "").lower() else "texto da página oficial (planalto)")
    elif os.path.exists(cn):
        r = camara_r3.ficha_norma(dec(open(cn, "rb").read()))
        src = co if os.path.exists(co) else None
        if not src:
            ALERTA["Câmara sem publicação original"].append([i]); continue
        txt = camara_r3.texto_original(dec(open(src, "rb").read())); sem = re.sub(r"~~[^~]*~~", " ", txt)
        epi_n = re.search(r"n[º°o]\s*([\d.]+)", r["epigrafe"], re.I)
        if not (epi_n and int(epi_n.group(1).replace(".", "")) == n and r["data"][:4] == ano):
            ALERTA["epígrafe não confere com o ID (descartado)"].append([i, r["epigrafe"]]); continue
        sit = "revogada" if re.search(r"(?i)revogad", r.get("situacao_fonte", "")) else ""
        dominio = "www2.camara.leg.br"
        NOS[i] = dict(id=i, tipo=TIPO.get(tp, ""), orgao="Presidência da República" if tp != "DLG" else "Congresso Nacional", numero=f"{n}/{ano}",
                      data=r["data"], ementa=r["ementa"], nivel=nivel(i), situacao=sit,
                      situacao_base=(f"situação na página da Câmara: {r['situacao_fonte']}" if r.get("situacao_fonte") else ""),
                      status_coleta="texto integral (www2.camara.leg.br)",
                      metodo_texto="página oficial do Portal da Legislação da Câmara dos Deputados (HTML) convertida em texto",
                      fonte=man.get(os.path.basename(cn), {}).get("url", ""), fonte_arquivo=man.get(os.path.basename(src), {}).get("url", ""),
                      arquivo_local=f"originais_r5/FEDERAL/{os.path.basename(src)}", texto_acervo=f"textos/FEDERAL/{i}.md",
                      data_coleta=HOJE, sha256=man.get(os.path.basename(src), {}).get("sha256", ""), epigrafe=r["epigrafe"],
                      notas_topo=r.get("vide", []), versao="publicação original (Câmara dos Deputados)")
    else:
        continue
    TXT[i] = txt
    if os.environ.get("SO_FICHAS"):
        continue
    rr, info = extrai(sem, i, "FED", inv | set(ids) | {i})
    T = prepara(sem)
    rv = spans_revogacao(T)
    _f = re.search(r"(?m)^\s*(?:Bras[íi]lia\s*,|Rio\s+de\s+Janeiro\s*,)", T)
    fecho = _f.start() if _f else len(T)
    ano_o = int(ano)
    for x in rr:
        parte = x.get("parte", "")
        if parte == "dispositivo" and x.get("tipo") == "REMETE A" and x.get("pos") is not None and any(a <= x["pos"] < b for a, b, _ in rv):
            alt = d86(T, x, ano_o)
            if alt:
                x["tipo"], dd = alt
                if dd: x["disp_destino"] = dd
                x["obs"] = (x.get("obs", "") + " D86/P2: citação em item de artigo de revogação (Revogam-se / Ficam revogados)").strip()
                CTRL_D86[x["tipo"]] += 1
            else:
                CTRL_D86["mantida REMETE A (nota, ementa transcrita ou cronologia)"] += 1
        if x.get("tipo", "").startswith("REVOGA") and x.get("pos") is not None:
            ef = [e for a, b, e in rv if a <= x["pos"] < b and e]
            if ef:
                x["inicio_efeito"] = ef[0]
                x["ressalva"] = (x.get("ressalva", "") + f" revogação com efeito a partir de {ef[0][8:10]}/{ef[0][5:7]}/{ef[0][:4]}").strip()
        # "revoga dispositivos da Lei X" é revogação parcial (o extrator das Rodadas 1–4 a registrava como total)
        if x.get("tipo") == "REVOGA (total)" and x.get("pos") is not None and (x.get("disp_destino") or "norma inteira") == "norma inteira":
            antes = re.sub(r"\s+", " ", T[max(0, x["pos"] - 90):x["pos"]])
            if re.search(r"(?i)(?:§|\b(?:dispositivos?|arts?\.|artigos?|incisos?|par[áa]grafos?)\b)[^;:]{0,60}$", antes):
                x["tipo"] = "REVOGA (parcial)"; x["disp_destino"] = "dispositivos (não especificados no trecho)"
                x["obs"] = (x.get("obs", "") + " Rodada 5: 'revoga dispositivos da…' = revogação parcial").strip()
                CTRL_D86["REVOGA (total) do extrator corrigida para parcial (revoga dispositivos)"] += 1
        if parte in ("citação indireta", "anotação junto a citação"):
            continue
        if parte != "anotação de consolidação":
            x["origem"] = i
            if x["destino"] == i: continue
            if x["destino"].startswith("UFPB-") and not re.search(r"UFPB|Universidade Federal da Para", x.get("trecho", "")):
                continue
        elif x.get("destino") != i:
            continue
        if x.get("pos") is not None and str(x.get("disp_origem", "")).startswith(("Anexo", "ANEXO")) and x["pos"] < fecho:
            x["disp_origem"] = re.sub(r"^(?:Anexo|ANEXO)\s+[IVXLC\d]+(?:,\s*)?", "", x["disp_origem"]) or "norma inteira"
        junta_rel(i, x, dominio)

os.makedirs(f"{W}/saida", exist_ok=True)
rels = []
for r in REL.values():
    r["disp_origem"] = "; ".join(r["disp_origem"][:12]) + (f" e outros {len(r['disp_origem'])-12}" if len(r["disp_origem"]) > 12 else "")
    r["disp_destino"] = "; ".join(r["disp_destino"][:12]) + (f" e outros {len(r['disp_destino'])-12}" if len(r["disp_destino"]) > 12 else "")
    obs = ("anotação no texto consolidado; " if r["anot"] else "") + f"{r['n']} ocorrência(s) no texto oficial"
    if r["obs_lst"]: obs += " | " + " | ".join(o for o in r["obs_lst"][:3] if o)
    r["obs"] = obs; r["evidencias"] = str(r["n"])
    if r["anot"] and r["tipo"] in ("ALTERA", "REVOGA (total)", "REVOGA (parcial)") and not r.get("inicio_efeito"):
        m = re.search(r"-(\d{4})$", r["origem"]); r["inicio_efeito"] = m.group(1) if m else ""
    for k in ("obs_lst", "anot", "n"): r.pop(k)
    rels.append(r)
json.dump(NOS, open(f"{W}/saida/r5_nos.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump({"relacoes": rels}, open(f"{W}/saida/r5_rel.json", "w", encoding="utf-8"), ensure_ascii=False)
json.dump(TXT, open(f"{W}/saida/r5_txt.json", "w", encoding="utf-8"), ensure_ascii=False)
json.dump(ALERTA, open(f"{W}/saida/r5_alertas.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
c = collections.Counter(r["tipo"] for r in rels)
print("normas:", len(NOS), "| relações:", len(rels), dict(c))
print("D86/P2 (REMETE A -> REVOGA em artigo de revogação):", dict(CTRL_D86))
json.dump(dict(CTRL_D86), open(f"{W}/saida/r5_d86.json", "w"))
print("alertas:", {k: len(v) for k, v in ALERTA.items()})
print("situação revogada:", sum(1 for x in NOS.values() if x["situacao"] == "revogada"), "| sem ementa:", [k for k, x in NOS.items() if not x["ementa"]][:20])

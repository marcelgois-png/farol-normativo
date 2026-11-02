"""Rodada 3: textos coletados (Câmara, CNE, unidades) -> nós, relações extraídas e Markdown por norma.
Entradas:
  saida/camara.json           (ficha + texto das leis e decretos da Câmara)
  txt/CNE/<ID>.txt            (texto dos PDFs do CNE) + _metodos_especiais.json
  txt/UNIDADES/<ID>.txt       (texto dos PDFs de unidades) + unidades.json (ficha mínima)
  manifestos *.tsv (sha256)
Saída: saida/r3_nos.json, saida/r3_rel.json, saida/textos/<GRUPO>/<ID>.md
"""
import csv, json, os, re, sys, unicodedata, collections, glob
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))  # scripts/extrator.py
from extrator import extrai, datas
csv.field_size_limit(10**9)

REPO = "/home/claude/marcelgois-png/farol-normativo"
W = "/home/claude/r3"
HOJE = "2026-11-02"
NFC = lambda s: unicodedata.normalize("NFC", s)
N = {r["id"]: r for r in csv.DictReader(open(f"{REPO}/base/nos.csv", encoding="utf-8"))}
inv = set(N)
NIV = lambda i: "N1" if i.startswith(("BR-CF", "BR-EC")) else "N2" if re.match(r"BR-(LEI|LC|DL|MP)-", i) else "N3" if i.startswith("BR-DEC") else "N4" if i.startswith("BR-") else "N10" if re.match(r"UFPB-[A-Z]+-PORT-", i) else "N9"

man = {}
for f in glob.glob(f"{W}/manifestos/*.tsv"):
    for ln in open(f, encoding="utf-8"):
        p = ln.rstrip("\n").split("\t")
        if len(p) >= 5: man[p[0]] = dict(bytes=p[1], sha256=p[2], ct=p[3], url=p[4])

nos, rels = {}, []
VERB = r"(Disp[õo]e|Aprova|Institui|Estabelece|Altera|Define|Regulamenta|Redefine|Atualiza|Orienta|Fixa|Torna|Inclui|Cria|Homologa|Reconhece|Autoriza|Renova|Regula|Proíbe|Normatiza|Concede|Declara|Transfere|Revoga|Consulta|Diretrizes|Reexame|Recurso|Solicita|Pedido|Credenciamento|Reconhecimento|Renovação)"

def relacoes(i, texto, cons, metodo, dominio):
    r, info = extrai(texto, i, cons, inv | set(nos) | {i})
    out = []
    for x in r:
        if x["destino"] == i: continue
        if x.get("parte") in ("citação indireta", "anotação de consolidação"): continue
        if x["tipo"] in ("ALTERA", "REVOGA (total)", "REVOGA (parcial)") and i.startswith("BR-") and NIV(x["destino"]) < NIV(i):
            x["tipo"] = "REMETE A"; x["obs"] = (x.get("obs", "") + " bloqueio hierárquico").strip()
        if x["tipo"] in ("ALTERA", "REVOGA (total)", "REVOGA (parcial)") and i.startswith("UFPB-") and not x["destino"].startswith("UFPB-"):
            x["tipo"] = "REMETE A"; x["obs"] = (x.get("obs", "") + " bloqueio hierárquico: ato de unidade não altera norma federal").strip()
        if x["destino"].startswith("UFPB-") and i.startswith("BR-") and not re.search(r"UFPB|Universidade Federal da Para", x.get("trecho", "")):
            continue
        out.append(dict(origem=i, destino=x["destino"], tipo=x["tipo"], disp_origem=x.get("disp_origem") or "norma inteira", disp_destino=x.get("disp_destino") or "norma inteira",
                        natureza=x.get("natureza", ""), base=f"texto ({dominio})", confianca=x.get("confianca", ""), evidencias="1", parte=x.get("parte", ""),
                        fonte_texto=metodo, citacao=x.get("citacao", ""), trecho=(x.get("trecho") or "")[:600], obs=x.get("obs", "")))
    return out, info

# ---------------------------------------------------------------- 1. Câmara (leis e decretos)
C = json.load(open(f"{W}/saida/camara.json", encoding="utf-8"))
TXT = {}
for i, r in C.items():
    if not r.get("texto"): continue
    tipo = "Decreto-Lei" if i.startswith("BR-DL") else "Lei" if i.startswith("BR-LEI") else "Decreto"
    m = re.match(r"BR-\w+-(\w+)-(\d{4})", i)
    sit = r.get("situacao_fonte", "")
    nos[i] = dict(id=i, tipo=tipo, orgao="União", numero=f"{m.group(1)}/{m.group(2)}", data=r.get("data", ""), ementa=r.get("ementa", ""), nivel=NIV(i),
                  situacao=("revogada" if sit.lower().startswith("revogad") else ""), situacao_base=(f"{sit} (indicação do Portal da Legislação da Câmara dos Deputados)" + ("; " + "; ".join(r.get("vide") or []) if r.get("vide") else "")) if sit else "",
                  status_coleta="texto integral (www2.camara.leg.br)", metodo_texto=r["metodo_texto"], fonte=r.get("fonte_ficha") or r.get("fonte_texto"), fonte_arquivo=r.get("fonte_texto"),
                  arquivo_local=r.get("arquivo_local"), texto_acervo=f"textos/FEDERAL/{i}.md", data_coleta=HOJE, sha256=r.get("sha256", ""), grupo="FEDERAL",
                  epigrafe=r.get("epigrafe", ""), publicacao=r.get("publicacao", ""), versao=r.get("versao", ""))
    TXT[i] = NFC(r["texto"])
for i in list(TXT):
    rr, info = relacoes(i, TXT[i], "FED", nos[i]["metodo_texto"], "www2.camara.leg.br")
    rels += rr
print("Câmara:", len(TXT), "normas,", len(rels), "relações")

# ---------------------------------------------------------------- 2. CNE
esp = json.load(open(f"{W}/txt/CNE/_metodos_especiais.json", encoding="utf-8")) if os.path.exists(f"{W}/txt/CNE/_metodos_especiais.json") else {}
n0 = len(rels)
for f in sorted(glob.glob(f"{W}/txt/CNE/*.txt")):
    i = os.path.basename(f)[:-4]
    t = NFC(open(f, encoding="utf-8", errors="replace").read())
    m = re.match(r"BR-CNE-(CES|CEB|CP)-(RES|PAR)-(\d+)-(\d{4})", i)
    cam, tp, num, ano = m.groups()
    t2 = re.sub(r"\s+", " ", t)
    em = ""
    if tp == "PAR":
        e = re.search(r"ASSUNTO:\s*(.{10,400}?)\s+(?:RELATOR|INTERESSAD|COMISS[ÃA]O|CONSELHEIRO|PROCESSO)", t2, re.I) or re.search(r"(?:Consulta|Diretrizes|Reexame|Recurso|Solicita|Pedido|Credenciamento|Reconhecimento|Renova)[^.]{10,300}\.", t2[:6000])
        em = (e.group(1) if e and e.lastindex else (e.group(0) if e else ""))[:400]
    else:
        e = re.search(VERB + r"[^.]{10,400}\.", t2[:6000]); em = e.group(0)[:400] if e else ""
    d = datas(t)
    data = ""
    if tp == "PAR":
        pa = t2.find("APROVADO EM")
        dm = re.search(r"(\d{1,2})\s*/\s*(\d{1,2})\s*/\s*(\d{4})", t2[pa:pa+300]) if pa >= 0 else None
        if dm: data = f"{dm.group(3)}-{int(dm.group(2)):02d}-{int(dm.group(1)):02d}"
    if not data:
        dm = re.search(r"(?:RESOLU[ÇC][ÃA]O|PARECER)[^\n]{0,60}?,?\s*DE\s+(\d{1,2})[º°o]?\s+DE\s+([A-ZÇ]+)\s+DE\s+(\d{4})", t[:3000], re.I)
        MES = {"janeiro":1,"fevereiro":2,"marco":3,"março":3,"abril":4,"maio":5,"junho":6,"julho":7,"agosto":8,"setembro":9,"outubro":10,"novembro":11,"dezembro":12}
        if dm and dm.group(2).lower() in MES: data = f"{dm.group(3)}-{MES[dm.group(2).lower()]:02d}-{int(dm.group(1)):02d}"
    if not data: data = ano
    mf = man.get(i + ".pdf", {})
    metodo = esp.get(i, "camada de texto do PDF oficial (pdftotext)")
    nos[i] = dict(id=i, tipo=("Parecer" if tp == "PAR" else "Resolução"), orgao=f"CNE/{cam}", numero=f"{num}/{ano}", data=data, ementa=em, nivel="N4",
                  situacao="", situacao_base="", status_coleta="texto integral (gov.br/mec — CNE)", metodo_texto=metodo, fonte=mf.get("url", ""), fonte_arquivo=mf.get("url", ""),
                  arquivo_local=f"originais_r3/CNE/{i}.pdf", texto_acervo=f"textos/CNE/{i}.md", data_coleta=HOJE, sha256=mf.get("sha256", ""), grupo="CNE",
                  epigrafe=f"{'Parecer' if tp=='PAR' else 'Resolução'} CNE/{cam} nº {num}/{ano}", versao="original publicado")
    rv = re.search(r"PARECER\s+REVOGADO\s+PEL[AO]\s+(.{5,120}?)(?:\s+MINIST[ÉE]RIO|\n\n|$)", t2[:400], re.I)
    if rv:
        nos[i]["situacao"] = "revogada"; nos[i]["situacao_base"] = "nota oficial no cabeçalho do PDF publicado pelo CNE: revogado pela " + rv.group(1).strip()
    hm = re.search(r"PARECER\s+HOMOLOGADO.{0,200}?(?:D\.?O\.?U\.?|Di[áa]rio\s+Oficial\s+da\s+Uni[ãa]o)\s*(?:de\s+)?(\d{1,2}/\d{1,2}/\d{4})", t2[:600], re.I)
    if tp == "PAR":
        nos[i]["obs"] = ("parecer homologado; despacho do Ministro publicado no DOU de " + hm.group(1)) if hm else ("parecer; homologação não indicada no cabeçalho do PDF" if not re.search(r"HOMOLOGADO", t2[:400], re.I) else "parecer homologado (data do despacho não identificada)")
    TXT[i] = t
for i in [k for k in TXT if k.startswith("BR-CNE")]:
    rr, info = relacoes(i, TXT[i], "CNE", nos[i]["metodo_texto"], "gov.br/mec — CNE")
    # citações a "UFPB-..." dentro de atos do CNE são, quase sempre, atos do próprio CNE/CFE
    for x in rr:
        dd = x["destino"]; tr = (x.get("trecho") or "") + " " + (x.get("citacao") or "")
        if dd.startswith(("UFPB-", "OUTRO-", "BR-?-")):
            mm = re.match(r"(?:UFPB|OUTRO|BR)-(?:[A-Z?]+-)*?(RES|PAR|PORT)-0*(\d+[A-Z]?)-(\d{4})$", dd)
            if mm:
                n_, a_ = int(re.sub(r"\D", "", mm.group(2))), mm.group(3)
                if mm.group(1) == "PORT": nd = f"BR-MEC-PORT-{n_}-{a_}" if re.search(r"MEC|Minist|Normativa", tr) else f"BR-?-PORT-{n_}-{a_}"
                elif re.search(r"Conselho\s+Federal\s+de\s+Educa|\bCFE\b", tr): nd = f"BR-CFE-{mm.group(1)}-{n_}-{a_}"
                elif re.search(r"\bCP\b|Conselho\s+Pleno", tr): nd = f"BR-CNE-CP-{mm.group(1)}-{n_}-{a_}"
                elif re.search(r"\bCES\b|Educa[çc][ãa]o\s+Superior", tr): nd = f"BR-CNE-CES-{mm.group(1)}-{n_}-{a_}"
                elif re.search(r"\bCEB\b|Educa[çc][ãa]o\s+B[áa]sica", tr): nd = f"BR-CNE-CEB-{mm.group(1)}-{n_}-{a_}"
                else: nd = f"BR-?-{mm.group(1)}-{n_}-{a_}"
                x["obs"] = (x.get("obs", "") + f" destino reidentificado ({dd} → {nd}): citação em ato do CNE não se refere a norma da UFPB").strip(); x["destino"] = nd
    rr = [x for x in rr if x["destino"] != i]
    if "-PAR-" in i:
        for x in rr:
            if x["tipo"] in ("ALTERA", "REVOGA (total)", "REVOGA (parcial)", "REGULAMENTA"):
                x["obs"] = (x.get("obs", "") + f" parecer não tem efeito normativo próprio: relação {x['tipo']} consta do projeto de resolução anexo; vale só pela resolução homologada").strip(); x["tipo"] = "REMETE A"
    rels += rr
print("CNE:", len([k for k in TXT if k.startswith('BR-CNE')]), "atos,", len(rels) - n0, "relações")

# ---------------------------------------------------------------- 3. unidades da UFPB
U = json.load(open(f"{W}/txt/UNIDADES/unidades.json", encoding="utf-8")) if os.path.exists(f"{W}/txt/UNIDADES/unidades.json") else {}
n0 = len(rels)
for i, v in U.items():
    f = f"{W}/txt/UNIDADES/{i}.txt"
    if not os.path.exists(f): continue
    t = NFC(open(f, encoding="utf-8", errors="replace").read())
    mf = man.get(i + ".pdf") or man.get(i + ".html") or {}
    ext = ".html" if man.get(i + ".html") else ".pdf"
    nos[i] = dict(id=i, tipo=v.get("tipo", "Portaria"), orgao=v.get("orgao", ""), numero=v.get("numero", ""), data=v.get("data", ""), ementa=v.get("ementa", ""), nivel=v.get("nivel", NIV(i)),
                  situacao="", situacao_base="", status_coleta=f"texto integral ({v.get('dominio','site da unidade')})", metodo_texto=v.get("metodo", "camada de texto do PDF oficial (pdftotext)"),
                  fonte=mf.get("url", v.get("url", "")), fonte_arquivo=mf.get("url", v.get("url", "")), arquivo_local=f"originais_r3/UNIDADES/{i}{ext}", texto_acervo=f"textos/UNIDADES/{i}.md",
                  data_coleta=HOJE, sha256=mf.get("sha256", ""), grupo="UNIDADES", epigrafe=v.get("epigrafe", ""), versao="original publicado no site da unidade")
    TXT[i] = t
    rr, info = relacoes(i, t, "UNID", nos[i]["metodo_texto"], v.get("dominio", "site da unidade"))
    rels += rr
print("Unidades:", len(U), "atos,", len(rels) - n0, "relações")

json.dump(nos, open(f"{W}/saida/r3_nos.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump({"relacoes": rels}, open(f"{W}/saida/r3_rel.json", "w", encoding="utf-8"), ensure_ascii=False)
json.dump({k: v for k, v in TXT.items()}, open(f"{W}/saida/r3_txt.json", "w", encoding="utf-8"), ensure_ascii=False)
print("total nós:", len(nos), "relações:", len(rels), collections.Counter(x["tipo"] for x in rels))
print("destinos novos (fora da base):", len({x["destino"] for x in rels} - inv - set(nos)))

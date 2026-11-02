"""Rodada 5: incorpora à base os atos coletados no planalto e na Câmara, as relações tiradas dos textos e as reidentificações.
Aplica diretamente em base/ do repositório (o git mostra a diferença).
Entradas: W/saida/r5_nos.json, r5_rel.json; scripts/r5/decisoes_r5.tsv; W/manifestos/*.tsv
Uso: python scripts/r5/merge_r5.py /home/claude/r5
"""
import csv, io, json, os, re, sys, collections
csv.field_size_limit(10**9)
AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(AQUI, "..", ".."))
W = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/r5"
HOJE = "2026-11-02"
STATUS_ALTERADORA = "alteradora anotada no texto consolidado do planalto — não citada; fora da fila por citação (Rodada 5)"

N = {r["id"]: r for r in csv.DictReader(open(f"{REPO}/base/nos.csv", encoding="utf-8"))}
COLS_N = list(next(iter(N.values())).keys())
A = list(csv.DictReader(io.StringIO(open(f"{REPO}/base/arestas.csv", encoding="utf-8").read().replace("\x00", ""))))
COLS_A = list(A[0].keys())
CTRL = collections.Counter(); REID = []

def novo_no(i, **kw):
    x = {c: "" for c in COLS_N}; x["id"] = i; x.update({k: v for k, v in kw.items() if k in COLS_N}); return x

def nivel_de(i):
    if i == "BR-CF-1988" or i.startswith("BR-EC-"): return "N1"
    if re.match(r"(BR|PB)-(LEI|LC|DL|MP|LDEL|DLG)-", i): return "N2"
    if i.startswith("BR-DEC-"): return "N3"
    if i.startswith(("BR-", "PB-")): return "N4"
    if re.match(r"UFPB-(CONSEPE|CONSUNI|CURADOR)-RES-", i): return "N7"
    if i.startswith("UFPB-REGIMENTO-"): return "N8"
    if re.match(r"UFPB-(GR|PR[A-Z]+)-PORT-", i): return "N10"
    if i.startswith("UFPB-"): return "N9"
    return "?"

def tipo_de(i):
    m = re.match(r"(?:BR|PB)-([A-Z]+)-", i)
    return {"LEI": "Lei", "LC": "Lei Complementar", "DEC": "Decreto", "DL": "Decreto-Lei", "EC": "Emenda Constitucional",
            "MP": "Medida Provisória", "LDEL": "Lei Delegada", "DLG": "Decreto Legislativo"}.get(m.group(1), "") if m else ""

def num_de(i):
    m = re.match(r"(?:BR|PB)-[A-Z]+-(\d+[A-Z]?)-(\d{4})$", i)
    return f"{m.group(1)}/{m.group(2)}" if m else ""

# ------------------------------------------------------------ 1. decisões de identificação
COR, FORA = {}, {}
for r in csv.DictReader(open(f"{AQUI}/decisoes_r5.tsv", encoding="utf-8"), delimiter="\t"):
    d = r["decisao"]
    if d.startswith("reidentificar"):
        COR[r["id_citado"]] = (r["id_correto"], ("provável; " if "provável" in d else "") + r["fundamento"])
    elif d.startswith("fora do escopo"):
        FORA[r["id_citado"]] = ("citada — norma estadual ou municipal, fora da fonte federal (Rodada 5)", r["fundamento"])
    else:
        FORA[r["id_citado"]] = ("citada — não localizada em fonte oficial acessível (Rodada 5)", r["fundamento"])

novas = []
for a in A:
    for lado in ("origem", "destino"):
        v = a[lado]
        if v in COR:
            nv, mot = COR[v]
            a = dict(a); a[lado] = nv
            a["obs"] = (a.get("obs", "") + f" | Rodada 5: {lado} reidentificado {v} → {nv} ({mot[:200]})").strip(" |")
            CTRL[f"arestas com {lado} reidentificado"] += 1; REID.append((a["origem"] if lado == "destino" else "base", v, nv, mot))
            if nv not in N:
                N[nv] = novo_no(nv, tipo=tipo_de(nv), numero=num_de(nv), nivel=nivel_de(nv), status_coleta="citada — a coletar",
                                obs="nó criado na Rodada 5 por reidentificação de citação")
    if a["origem"] == a["destino"]:
        CTRL["arestas descartadas (autocitação após correção)"] += 1; continue
    novas.append(a)
A = novas
usados = {a["origem"] for a in A} | {a["destino"] for a in A}
for old, (nv, mot) in COR.items():
    if old in N and old not in usados and not N[old]["status_coleta"].startswith("texto"):
        if N[nv].get("obs", "").find(old) < 0:
            N[nv]["obs"] = (N[nv].get("obs", "") + f" | Rodada 5: fundido com {old}").strip(" |")
        del N[old]; CTRL["nós removidos (citação reidentificada)"] += 1
for i, (st, mot) in FORA.items():
    if i in N:
        N[i]["status_coleta"] = st; N[i]["obs"] = (N[i]["obs"] + " | Rodada 5: " + mot).strip(" |")
        CTRL["nós marcados fora do escopo federal ou não localizados"] += 1

# ------------------------------------------------------------ 2. normas com texto da Rodada 5
R5N = json.load(open(f"{W}/saida/r5_nos.json", encoding="utf-8"))
for i, v in R5N.items():
    x = N.get(i) or novo_no(i)
    if i not in N: CTRL["nós novos com texto (não estavam na base)"] += 1
    keep = x.get("obs", "")
    for k in ("tipo", "orgao", "numero", "data", "ementa", "nivel", "status_coleta", "metodo_texto", "fonte", "fonte_arquivo", "arquivo_local", "texto_acervo", "data_coleta"):
        if v.get(k): x[k] = v[k]
    x["situacao"] = v.get("situacao", "") or ""
    x["situacao_base"] = v.get("situacao_base", "") or ""
    x["situacao_planalto"] = v.get("situacao_base", "") if "planalto" in v.get("situacao_base", "") or "Câmara" in v.get("situacao_base", "") else x.get("situacao_planalto", "")
    x["obs"] = " | ".join(s for s in [keep, "texto coletado na Rodada 5 (" + ("planalto.gov.br" if "planalto" in v["status_coleta"] else "Câmara dos Deputados") + ")"] if s)
    N[i] = x
CTRL["normas com texto integral incorporadas"] = len(R5N)

# ------------------------------------------------------------ 3. relações extraídas
def k_ar(a): return (a["origem"], a["destino"], a["tipo"])
exist = {k_ar(a) for a in A}; n_new = 0; n_dup = 0; NOVAS_IDS = set()
anot_orig = set(); cit_dest = set()
for x in json.load(open(f"{W}/saida/r5_rel.json", encoding="utf-8"))["relacoes"]:
    for lado in ("origem", "destino"):
        if x[lado] in COR: x["obs"] = (x.get("obs", "") + f" | {lado} reidentificado {x[lado]} → {COR[x[lado]][0]}").strip(" |"); x[lado] = COR[x[lado]][0]
    if x["origem"] == x["destino"]: continue
    a = {c: "" for c in COLS_A}
    a.update({k: x.get(k, "") for k in COLS_A if k in x})
    a["evidencias"] = x.get("evidencias", "1")
    if k_ar(a) in exist: n_dup += 1; continue
    exist.add(k_ar(a)); A.append(a); n_new += 1; NOVAS_IDS.add(id(a))
    CTRL[f"relações novas: {a['tipo']}"] += 1
    if a["parte"] == "anotação de consolidação": anot_orig.add(a["origem"])
    else: cit_dest.add(a["destino"])
CTRL["relações novas tiradas dos textos da Rodada 5"] = n_new
CTRL["relações já existentes na base (não duplicadas)"] = n_dup
destinos_citados = {a["destino"] for a in A if a.get("parte") != "anotação de consolidação"}
for e in sorted(anot_orig | cit_dest):
    if e in N: continue
    so_anot = e in anot_orig and e not in destinos_citados
    N[e] = novo_no(e, tipo=tipo_de(e), numero=num_de(e), nivel=nivel_de(e),
                   status_coleta=STATUS_ALTERADORA if so_anot else "citada — a coletar",
                   obs=("Rodada 5: só aparece como alteradora/revogadora anotada em texto consolidado do planalto (D90)" if so_anot else "citada em ato coletado na Rodada 5"))
    CTRL["nós novos: alteradoras anotadas (fora da fila, D90)" if so_anot else "nós novos: citados por atos da Rodada 5 (entram na fila)"] += 1
# alteradora que passou a ser citada volta para a fila
for i, x in N.items():
    if x["status_coleta"].startswith("alteradora anotada") and i in destinos_citados:
        x["status_coleta"] = "citada — a coletar"; x["obs"] = (x["obs"] + " | Rodada 5: passou a ser citada por norma coletada; volta à fila").strip(" |")
        CTRL["alteradoras anotadas que passaram a ser citadas (voltam à fila)"] += 1

# ------------------------------------------------------------ 4. situação a partir das relações lidas
for i in R5N:
    if not N[i].get("situacao"): N[i]["situacao"] = "sem alteração ou revogação registrada"
NIVEL_ORD = lambda i: {"N1": 1, "N2": 2, "N3": 3}.get(nivel_de(i), 4)
for a in A:
    if a.get("natureza", "") or a["destino"] not in N: continue
    if id(a) not in NOVAS_IDS: continue                      # só relações lidas nesta rodada
    if a.get("parte") in ("citação indireta", "anotação junto a citação"): continue
    if NIVEL_ORD(a["origem"]) > NIVEL_ORD(a["destino"]): continue   # norma inferior não revoga superior
    d = N[a["destino"]]
    ief = a.get("inicio_efeito", "")
    if a["tipo"].startswith("REVOGA") and len(ief) == 10 and ief > HOJE:
        nota = f"revogação {'total' if a['tipo'] == 'REVOGA (total)' else 'parcial'} programada por {a['origem']} ({a['disp_origem']}) com efeito a partir de {ief[8:10]}/{ief[5:7]}/{ief[:4]}"
        if nota not in d.get("situacao_base", ""):
            d["situacao_base"] = (d.get("situacao_base", "") + "; " + nota).strip("; ")
        CTRL["situações: revogação programada (efeito futuro), não aplicada"] += 1
        continue
    if a["tipo"] == "REVOGA (total)" and a["parte"] != "anotação de consolidação" and not d.get("situacao", "").startswith("revogada"):
        d["situacao"] = "revogada"; d["situacao_base"] = f"revogada por {a['origem']} ({a['disp_origem']}); texto lido na Rodada 5"; CTRL["situações: revogação lida na Rodada 5"] += 1
    elif a["tipo"] in ("ALTERA", "REVOGA (parcial)") and a["destino"] in R5N:
        rotulo = "alterada" if a["tipo"] == "ALTERA" else "revogada parcialmente"
        if d.get("situacao", "") in ("", "sem alteração ou revogação registrada"):
            d["situacao"] = rotulo; d["situacao_base"] = f"{rotulo} por {a['origem']} (anotações do texto compilado)"; CTRL["situações: alteração anotada no texto compilado"] += 1
        elif d["situacao"] in ("alterada", "revogada parcialmente") and rotulo not in d["situacao"]:
            d["situacao"] = "alterada e revogada parcialmente"

# ------------------------------------------------------------ 5. gravação
with open(f"{REPO}/base/nos.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, COLS_N, lineterminator="\r\n"); w.writeheader(); [w.writerow({c: x.get(c, "") for c in COLS_N}) for x in sorted(N.values(), key=lambda x: x["id"])]
with open(f"{REPO}/base/arestas.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, COLS_A, lineterminator="\r\n"); w.writeheader(); [w.writerow({c: a.get(c, "") for c in COLS_A}) for a in A]
p = f"{REPO}/base/divergencias/reidentificacoes_r5.csv"
antigos = list(csv.DictReader(open(p, encoding="utf-8"))) if os.path.exists(p) else []
with open(p, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, lineterminator="\r\n"); w.writerow(["origem", "id_antigo", "id_novo", "motivo"])
    w.writerows([[r["origem"], r["id_antigo"], r["id_novo"], r["motivo"]] for r in antigos] + sorted({(o, a, n, "Rodada 5 (coleta): " + m) for o, a, n, m in REID}))
man_rows = []
for f in sorted(os.listdir(f"{W}/manifestos")):
    for ln in open(f"{W}/manifestos/{f}", encoding="utf-8"):
        p_ = ln.rstrip("\n").split("\t")
        if len(p_) < 5: continue
        nome = p_[0]; i = nome.split("__")[0]
        if i not in R5N: continue
        man_rows.append([i, "", "", N.get(i, {}).get("numero", ""), p_[4], f"originais_r5/FEDERAL/{nome}", p_[1], p_[2], p_[3]])
with open(f"{REPO}/base/manifesto_originais.tsv", "a", encoding="utf-8", newline="") as f:
    for r in man_rows: f.write("\t".join(r) + "\n")
CTRL["linhas acrescentadas ao manifesto"] = len(man_rows)
json.dump(dict(CTRL), open(f"{REPO}/base/controles/controles_r5.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(dict(CTRL), ensure_ascii=False, indent=1))
print("nós:", len(N), "arestas:", len(A))

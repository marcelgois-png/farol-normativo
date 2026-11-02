"""Rodada 4: incorpora à base do repositório farol-normativo os atos coletados e as reidentificações.
Aplica diretamente em base/ e textos/ do clone (git mostra a diferença).
Entradas: saida/r4_nos.json, saida/r4_rel.json, saida/r4_txt.json, decisoes_r4.tsv (blocos A, B e C)
"""
import csv, io, json, os, re, collections, unicodedata, sys
csv.field_size_limit(10**9)
REPO = "/home/claude/farol-normativo"; W = "/home/claude/r4"; HOJE = "2026-11-02"
N = {r["id"]: r for r in csv.DictReader(open(f"{REPO}/base/nos.csv", encoding="utf-8"))}
COLS_N = list(next(iter(N.values())).keys())
A = list(csv.DictReader(io.StringIO(open(f"{REPO}/base/arestas.csv", encoding="utf-8").read().replace("\x00", ""))))
COLS_A = list(A[0].keys())
CTRL = collections.Counter(); REID = []; DIV = []
def novo_no(i, **kw):
    x = {c: "" for c in COLS_N}; x["id"] = i; x.update({k: v for k, v in kw.items() if k in COLS_N}); return x
def nivel_de(i):
    if i == "BR-CF-1988" or i.startswith("BR-EC-"): return "N1"
    if re.match(r"BR-(LEI|LC|DL|MP)-", i): return "N2"
    if i.startswith("BR-DEC-"): return "N3"
    if i.startswith("BR-") or i.startswith("PB-"): return "N4"
    if re.match(r"UFPB-(CONSEPE|CONSUNI|CURADOR)-RES-", i): return "N7"
    if i.startswith("UFPB-REGIMENTO-"): return "N8"
    if re.match(r"UFPB-(GR|PR[A-Z]+)-PORT-", i): return "N10"
    if i.startswith("UFPB-"): return "N9"
    return "?"

# ------------------------------------------------------------ 1. reidentificações e descartes
COR = {}; FORA = {}; NAONORMA = {}
for f in ("decisoes_r4.tsv",):
    for r in csv.DictReader(open(f"{W}/{f}", encoding="utf-8"), delimiter="\t"):
        d = r["decisao"]
        if d.startswith("reidentificar") and r["id_correto"] not in ("", "—"):
            COR[r["id_citado"]] = (r["id_correto"], ("provável; " if "provável" in d else "") + r["fundamento"])
        elif d.startswith("fora do escopo"): FORA[r["id_citado"]] = r["fundamento"]
        elif d.startswith("não é norma"): NAONORMA[r["id_citado"]] = r["fundamento"]
        elif d.startswith(("não localizada", "não resolvida", "fonte oficial")): FORA.setdefault(r["id_citado"], "__NL__" + r["fundamento"])
# cadeia de reidentificação
def alvo(i):
    seen = set()
    while i in COR and i not in seen:
        seen.add(i); i = COR[i][0]
    return i
novas = []
for a in A:
    d = a["destino"]
    if d in NAONORMA:
        CTRL["arestas descartadas (citação não é norma)"] += 1; REID.append((a["origem"], d, "(não é norma)", NAONORMA[d])); continue
    if d in COR:
        nd = alvo(d); mot = COR[d][1]
        if nd == a["origem"]: CTRL["arestas descartadas (autocitação após correção)"] += 1; continue
        a = dict(a); a["obs"] = (a.get("obs", "") + f" | Rodada 4: destino reidentificado {d} → {nd} ({mot[:220]})").strip(" |"); a["destino"] = nd
        CTRL["arestas com destino reidentificado"] += 1; REID.append((a["origem"], d, nd, mot))
        if nd not in N: N[nd] = novo_no(nd, nivel=nivel_de(nd), status_coleta="citada — a coletar", obs="nó criado na Rodada 4 por reidentificação de citação")
    novas.append(a)
A = novas
usados = {a["origem"] for a in A} | {a["destino"] for a in A}
for old in list(COR) + list(NAONORMA):
    if old in N and old not in usados and not N[old]["status_coleta"].startswith("texto"):
        del N[old]; CTRL["nós removidos (citação reidentificada ou descartada)"] += 1
for i, mot in FORA.items():
    if i not in N: continue
    if mot.startswith("__NL__"):
        N[i]["status_coleta"] = "citada — não localizada em fonte oficial acessível (Rodada 4)"; N[i]["obs"] = (N[i]["obs"] + " | Rodada 4: " + mot[6:]).strip(" |")
    else:
        N[i]["status_coleta"] = "citada — norma estadual ou municipal, fora da fonte federal (Rodada 4)"; N[i]["obs"] = (N[i]["obs"] + " | Rodada 4: " + mot).strip(" |")
    CTRL["nós marcados como fora do escopo federal ou não localizados"] += 1

# ------------------------------------------------------------ 2. nós com texto da Rodada 4
R3N = json.load(open(f"{W}/saida/r4_nos.json", encoding="utf-8"))
R3T = json.load(open(f"{W}/saida/r4_txt.json", encoding="utf-8"))
for i, v in R3N.items():
    x = N.get(i) or novo_no(i)
    if i not in N: CTRL["nós novos com texto (não estavam na base)"] += 1
    keep_obs = x.get("obs", "")
    for k in ("tipo", "orgao", "numero", "data", "ementa", "nivel", "status_coleta", "metodo_texto", "aviso_texto", "fonte", "fonte_arquivo", "arquivo_local", "texto_acervo", "data_coleta"):
        if v.get(k): x[k] = v[k]
    if x.get("situacao") == "não localizada": x["situacao"] = ""
    if v.get("situacao"): x["situacao"] = v["situacao"]; x["situacao_base"] = v.get("situacao_base", "")
    elif v.get("situacao_base"): x["situacao_base"] = v["situacao_base"]
    x["obs"] = " | ".join(s for s in [keep_obs, v.get("obs", ""), "texto coletado na Rodada 4"] if s)
    N[i] = x
CTRL["normas com texto integral incorporadas"] = len(R3N)

# ------------------------------------------------------------ 3. relações extraídas
def k_ar(a): return (a["origem"], a["destino"], a["tipo"], a.get("disp_origem", ""), a.get("disp_destino", ""))
exist = {k_ar(a) for a in A}; n_new = 0
# correções conferidas no texto das leis estaduais: "Lei nº" dentro de lei da Paraíba é lei estadual; "Revogam-se as disposições do art. 2º" é revogação parcial
CORR_U = {("PB-LEI-6308-1996", "BR-LEI-3936-1977"): ("PB-LEI-3936-1977", "ALTERA", "norma inteira"),
          ("PB-LEI-6308-1996", "BR-LEI-5404-1991"): ("PB-LEI-5404-1991", "ALTERA", "norma inteira"),
          ("PB-LEI-6308-1996", "BR-LEI-5583-1992"): ("PB-LEI-5583-1992", "ALTERA", "norma inteira"),
          ("PB-LEI-10601-2015", "PB-LEI-3489-1967"): ("PB-LEI-3489-1967", "REVOGA (parcial)", "art. 2º")}
for x in json.load(open(f"{W}/saida/r4_rel.json", encoding="utf-8"))["relacoes"]:
    if (x["origem"], x["destino"]) in CORR_U:
        nd, tp, dd = CORR_U[(x["origem"], x["destino"])]
        x["obs"] = (x.get("obs", "") + f" Rodada 4: citação conferida no texto — destino {x['destino']} → {nd}, relação {tp} ({dd})").strip(); x["destino"] = nd; x["tipo"] = tp; x["disp_destino"] = dd; x["confianca"] = "alta"
        CTRL["citações corrigidas à mão (leis estaduais)"] += 1
    d = alvo(x["destino"]) if x["destino"] in COR else x["destino"]
    if d in NAONORMA or d == x["origem"]: continue
    a = {c: "" for c in COLS_A}
    a.update(origem=x["origem"], destino=d, tipo=x["tipo"], disp_origem=x.get("disp_origem") or "norma inteira", disp_destino=x.get("disp_destino") or "norma inteira",
             natureza=x.get("natureza", ""), base=x.get("base", "texto"), confianca=x.get("confianca", ""), evidencias="1", parte=x.get("parte", ""), fonte_texto=x.get("fonte_texto", ""),
             citacao=x.get("citacao", ""), ressalva=x.get("ressalva", ""), trecho=(x.get("trecho") or "")[:600], obs=(x.get("obs", "") + (f" destino reidentificado {x['destino']} → {d}" if d != x["destino"] else "")).strip())
    if k_ar(a) in exist: continue
    exist.add(k_ar(a)); A.append(a); n_new += 1
    for e in (a["origem"], a["destino"]):
        if e not in N: N[e] = novo_no(e, nivel=nivel_de(e), status_coleta="citada — a coletar", obs="citada em ato coletado na Rodada 4")
CTRL["relações novas tiradas dos textos da Rodada 4"] = n_new

# ------------------------------------------------------------ 5. situação das novas normas federais e do CNE (notas da fonte / relações)
for i in R3N:
    x = N[i]
    if not x.get("situacao"): x["situacao"] = "sem alteração ou revogação registrada"
    if not x.get("situacao_base") and x["id"].startswith("BR-CNE"): x["situacao_base"] = "nenhuma revogação ou alteração registrada nos textos lidos (Rodada 4)"
# revogações extraídas na rodada aplicadas ao destino
for a in A:
    if a["tipo"] == "REVOGA (total)" and a.get("natureza", "") == "" and a["origem"] in R3N and a["destino"] in N and not N[a["destino"]].get("situacao", "").startswith("revogada"):
        d = N[a["destino"]]
        if d["status_coleta"].startswith("texto") or True:
            d["situacao"] = "revogada"; d["situacao_base"] = f"revogada por {a['origem']} ({a['disp_origem']}); texto lido na Rodada 4"; CTRL["situações atualizadas por revogação lida na Rodada 4"] += 1
    if a["tipo"] in ("ALTERA", "REVOGA (parcial)") and a.get("natureza", "") == "" and a["origem"] in R3N and a["destino"] in N:
        d = N[a["destino"]]
        if d.get("situacao", "") in ("", "sem alteração ou revogação registrada"):
            d["situacao"] = "alterada"; d["situacao_base"] = f"alterada por {a['origem']} ({a['disp_origem']}); texto lido na Rodada 4"; CTRL["situações atualizadas por alteração lida na Rodada 4"] += 1
        elif a["origem"] not in d.get("situacao_base", ""):
            d["situacao_base"] = (d["situacao_base"] + f"; também alterada por {a['origem']} ({a['disp_origem']}; texto lido na Rodada 4)").strip("; "); CTRL["situações complementadas por alteração lida na Rodada 4"] += 1

# ------------------------------------------------------------ 6. gravação
with open(f"{REPO}/base/nos.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, COLS_N); w.writeheader(); [w.writerow({c: x.get(c, "") for c in COLS_N}) for x in sorted(N.values(), key=lambda x: x["id"])]
with open(f"{REPO}/base/arestas.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, COLS_A); w.writeheader(); [w.writerow({c: a.get(c, "") for c in COLS_A}) for a in A]
with open(f"{REPO}/base/divergencias/reidentificacoes_r4.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f); w.writerow(["origem", "id_antigo", "id_novo", "motivo"]); w.writerows(sorted(set(REID)))
json.dump(dict(CTRL), open(f"{REPO}/base/controles/controles_r4.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
# manifesto
man_rows = []
for f in sorted(os.listdir(f"{W}/manifestos")):
    for ln in open(f"{W}/manifestos/{f}", encoding="utf-8"):
        p = ln.rstrip("\n").split("\t")
        if len(p) < 5: continue
        nome = p[0]; i = re.sub(r"\.(pdf|html)$", "", nome.split("__")[0])
        if i not in R3N: continue  # originais descartados (ato de outro órgão) ficam em _descartados e fora do manifesto
        grp = "MEC" if "dou" in f else "PB"
        man_rows.append([i, "", "", N.get(i, {}).get("numero", ""), p[4], f"originais_r4/{grp}/{nome}", p[1], p[2], p[3]])
with open(f"{REPO}/base/manifesto_originais.tsv", "a", encoding="utf-8", newline="") as f:
    for r in man_rows: f.write("\t".join(r) + "\n")
CTRL["linhas acrescentadas ao manifesto"] = len(man_rows)
print(json.dumps(dict(CTRL), ensure_ascii=False, indent=1))
print("nós:", len(N), "arestas:", len(A))

"""Rodada 3: incorpora à base do repositório farol-normativo os atos coletados e as reidentificações.
Aplica diretamente em base/ e textos/ do clone (git mostra a diferença).
Entradas: saida/r3_nos.json, saida/r3_rel.json, saida/r3_txt.json, decisoes_leis.tsv, decisoes_cne.tsv, regimentos.json
"""
import csv, io, json, os, re, collections, unicodedata, sys
csv.field_size_limit(10**9)
REPO = "/home/claude/marcelgois-png/farol-normativo"; W = "/home/claude/r3"; HOJE = "2026-11-02"
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
    if re.match(r"UFPB-[A-Z]+-PORT-", i): return "N10"
    if i.startswith("UFPB-"): return "N9"
    return "?"

# ------------------------------------------------------------ 1. reidentificações e descartes
COR = {}; FORA = {}; NAONORMA = {}
for f in ("decisoes_leis.tsv", "decisoes_cne.tsv"):
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
        a = dict(a); a["obs"] = (a.get("obs", "") + f" | Rodada 3: destino reidentificado {d} → {nd} ({mot[:220]})").strip(" |"); a["destino"] = nd
        CTRL["arestas com destino reidentificado"] += 1; REID.append((a["origem"], d, nd, mot))
        if nd not in N: N[nd] = novo_no(nd, nivel=nivel_de(nd), status_coleta="citada — a coletar", obs="nó criado na Rodada 3 por reidentificação de citação")
    novas.append(a)
A = novas
usados = {a["origem"] for a in A} | {a["destino"] for a in A}
for old in list(COR) + list(NAONORMA):
    if old in N and old not in usados and not N[old]["status_coleta"].startswith("texto"):
        del N[old]; CTRL["nós removidos (citação reidentificada ou descartada)"] += 1
for i, mot in FORA.items():
    if i not in N: continue
    if mot.startswith("__NL__"):
        N[i]["status_coleta"] = "citada — não localizada em fonte oficial acessível (Rodada 3)"; N[i]["obs"] = (N[i]["obs"] + " | Rodada 3: " + mot[6:]).strip(" |")
    else:
        N[i]["status_coleta"] = "citada — norma estadual ou municipal, fora da fonte federal (Rodada 3)"; N[i]["obs"] = (N[i]["obs"] + " | Rodada 3: " + mot).strip(" |")
    CTRL["nós marcados como fora do escopo federal ou não localizados"] += 1
# CFE: todos os atos do CFE sem texto
for i, x in N.items():
    if i.startswith("BR-CFE-") and not x["status_coleta"].startswith("texto") and "Rodada 3" not in x["obs"]:
        x["status_coleta"] = "citada — fonte oficial não acessível (atos do extinto CFE; Rodada 3)"
        x["obs"] = (x["obs"] + " | Rodada 3: atos do Conselho Federal de Educação (até 1994) não estão no gov.br/mec; fonte: Documenta/DOU — pedir à SODS ou à Biblioteca Central").strip(" |")
        CTRL["atos do CFE marcados como fonte não acessível"] += 1

# ------------------------------------------------------------ 2. nós com texto da Rodada 3
R3N = json.load(open(f"{W}/saida/r3_nos.json", encoding="utf-8"))
R3T = json.load(open(f"{W}/saida/r3_txt.json", encoding="utf-8"))
for i, v in R3N.items():
    x = N.get(i) or novo_no(i)
    if i not in N: CTRL["nós novos com texto (não estavam na base)"] += 1
    keep_obs = x.get("obs", "")
    for k in ("tipo", "orgao", "numero", "data", "ementa", "nivel", "status_coleta", "metodo_texto", "fonte", "fonte_arquivo", "arquivo_local", "texto_acervo", "data_coleta"):
        if v.get(k): x[k] = v[k]
    if x.get("situacao") == "não localizada": x["situacao"] = ""
    if v.get("situacao"): x["situacao"] = v["situacao"]; x["situacao_base"] = v.get("situacao_base", "")
    elif v.get("situacao_base"): x["situacao_base"] = v["situacao_base"]
    x["obs"] = " | ".join(s for s in [keep_obs, v.get("obs", ""), "texto coletado na Rodada 3"] if s)
    N[i] = x
CTRL["normas com texto integral incorporadas"] = len(R3N)

# ------------------------------------------------------------ 3. relações extraídas
def k_ar(a): return (a["origem"], a["destino"], a["tipo"], a.get("disp_origem", ""), a.get("disp_destino", ""))
exist = {k_ar(a) for a in A}; n_new = 0
CORR_U = {  # correções manuais de citações em atos de unidades (conferidas no texto)
    ("UFPB-PRPG-PORT-08-2021", "BR-CAPES-PORT-6-2021"): ("UFPB-PRPG-PORT-06-2021", "ALTERA", "art. 6-A (acrescentado)"),
    ("UFPB-PRPG-PORT-08-2021", "BR-?-PORT-6-2021"): ("UFPB-PRPG-PORT-06-2021", "ALTERA", "art. 11, § 2º"),
    ("UFPB-PRPG-PORT-08-2021", "UFPB-PRPG-PORT-06-2021"): ("UFPB-PRPG-PORT-06-2021", "ALTERA", "norma inteira"),
    ("UFPB-PRPG-PORT-09-2021", "UFPB-PRPG-PORT-08-2021"): ("UFPB-PRPG-PORT-08-2021", "ALTERA", "§ 4º do art. 6-A da Portaria 06/2021 (retificação)"),
}
for x in json.load(open(f"{W}/saida/r3_rel.json", encoding="utf-8"))["relacoes"]:
    if (x["origem"], x["destino"]) in CORR_U:
        nd, tp, dd = CORR_U[(x["origem"], x["destino"])]
        x["obs"] = (x.get("obs", "") + f" Rodada 3: citação conferida no texto — destino {x['destino']} → {nd}, relação {tp} ({dd})").strip(); x["destino"] = nd; x["tipo"] = tp; x["disp_destino"] = dd; x["confianca"] = "alta"
        CTRL["citações de atos de unidades corrigidas à mão"] += 1
    d = alvo(x["destino"]) if x["destino"] in COR else x["destino"]
    if d in NAONORMA or d == x["origem"]: continue
    a = {c: "" for c in COLS_A}
    a.update(origem=x["origem"], destino=d, tipo=x["tipo"], disp_origem=x.get("disp_origem") or "norma inteira", disp_destino=x.get("disp_destino") or "norma inteira",
             natureza=x.get("natureza", ""), base=x.get("base", "texto"), confianca=x.get("confianca", ""), evidencias="1", parte=x.get("parte", ""), fonte_texto=x.get("fonte_texto", ""),
             citacao=x.get("citacao", ""), ressalva=x.get("ressalva", ""), trecho=(x.get("trecho") or "")[:600], obs=(x.get("obs", "") + (f" destino reidentificado {x['destino']} → {d}" if d != x["destino"] else "")).strip())
    if k_ar(a) in exist: continue
    exist.add(k_ar(a)); A.append(a); n_new += 1
    for e in (a["origem"], a["destino"]):
        if e not in N: N[e] = novo_no(e, nivel=nivel_de(e), status_coleta="citada — a coletar", obs="citada em ato coletado na Rodada 3")
CTRL["relações novas tiradas dos textos da Rodada 3"] = n_new

# ------------------------------------------------------------ 4. regimentos de unidades
REG = json.load(open(f"{W}/regimentos.json", encoding="utf-8"))
for sigla, v in REG.items():
    i = f"UFPB-REGIMENTO-{sigla}"
    if i not in N: continue
    x = N[i]
    x["ementa"] = x["ementa"].replace("Pró-Reitoria Administrativa (PRA)", "Pró-Reitoria de Administração (PRA)")
    if v.get("res"):
        r = N.get(v["res"])
        x["numero"] = v["res"].split("-")[-2] + "/" + v["res"].split("-")[-1]; x["data"] = r["data"] if r else ""
        x["status_coleta"] = "texto integral (anexo da resolução do CONSUNI/CONSEPE que o aprova — SIGRH)"
        x["metodo_texto"] = (r["metodo_texto"] if r else "") ; x["fonte"] = r["fonte"] if r else x["fonte"]; x["fonte_arquivo"] = r["fonte_arquivo"] if r else ""
        x["arquivo_local"] = r["arquivo_local"] if r else ""; x["texto_acervo"] = f"textos/REGIMENTOS/{i}.md"; x["data_coleta"] = HOJE
        x["ementa"] = re.sub(r"\s*Ato de aprovação a localizar\.?", "", x["ementa"]) + f" Aprovado pela {v['rotulo']}." + (f" {v['nota']}" if v.get("nota") else "")
        x["situacao"] = r["situacao"] if r else ""; x["situacao_base"] = (f"situação herdada do ato de aprovação {v['res']}: " + (r["situacao_base"] or "")) if r else ""
        x["obs"] = (x["obs"] + f" | Rodada 3: texto localizado como anexo da {v['rotulo']} (já no acervo); o Markdown do regimento é gerado a partir do mesmo original.").strip(" |")
        a = {c: "" for c in COLS_A}
        a.update(origem=i, destino=v["res"], tipo="FUNDAMENTA-SE EM", disp_origem="norma inteira", disp_destino="art. 1º (ato de aprovação)", base="ato de aprovação (ementa e art. 1º da resolução)", confianca="alta", evidencias="1", parte="dispositivo", fonte_texto=x["metodo_texto"], citacao=v["rotulo"], trecho=(r["ementa"] if r else "")[:300], obs="Rodada 3: regimento de unidade aprovado por resolução de conselho superior")
        if k_ar(a) not in exist: exist.add(k_ar(a)); A.append(a)
        for alt in v.get("alteradoras", []):
            if alt in N:
                b_ = {c: "" for c in COLS_A}
                b_.update(origem=alt, destino=i, tipo="ALTERA", disp_origem="norma inteira", disp_destino="norma inteira", base="ementa da resolução alteradora", confianca="média", evidencias="1", parte="ementa", fonte_texto=N[alt]["metodo_texto"], citacao=N[alt]["ementa"][:120], trecho=N[alt]["ementa"][:300], obs="Rodada 3: alteração do regimento registrada pela ementa; conferir o dispositivo no texto")
                if k_ar(b_) not in exist: exist.add(k_ar(b_)); A.append(b_)
        CTRL["regimentos de unidades localizados no acervo (anexos de resoluções)"] += 1
    else:
        x["status_coleta"] = "na fila — regimento próprio não localizado (Rodada 3)"
        x["obs"] = (x["obs"] + " | Rodada 3: " + v["nota"]).strip(" |")
        if v.get("estrutura") and v["estrutura"] in N:
            a = {c: "" for c in COLS_A}
            a.update(origem=i, destino=v["estrutura"], tipo="REMETE A", natureza="sugestão: ato de criação ou estrutura da unidade, não é o regimento", disp_origem="norma inteira", disp_destino="norma inteira", base="inferência (Rodada 3)", confianca="média", evidencias="1", parte="", citacao="", trecho="", obs=f"Rodada 3: enquanto o regimento não for localizado, a estrutura da unidade é dada por este ato ({v['estrutura']})")
            if k_ar(a) not in exist: exist.add(k_ar(a)); A.append(a)
        CTRL["regimentos de unidades ainda não localizados"] += 1

# ------------------------------------------------------------ 5. situação das novas normas federais e do CNE (notas da fonte / relações)
for i in R3N:
    x = N[i]
    if not x.get("situacao"): x["situacao"] = "sem alteração ou revogação registrada"
    if not x.get("situacao_base") and x["id"].startswith("BR-CNE"): x["situacao_base"] = "nenhuma revogação ou alteração registrada nos textos lidos (Rodada 3)"
# revogações extraídas na rodada aplicadas ao destino
for a in A:
    if a["tipo"] == "REVOGA (total)" and a.get("natureza", "") == "" and a["origem"] in R3N and a["destino"] in N and not N[a["destino"]].get("situacao", "").startswith("revogada"):
        d = N[a["destino"]]
        if d["status_coleta"].startswith("texto") or True:
            d["situacao"] = "revogada"; d["situacao_base"] = f"revogada por {a['origem']} ({a['disp_origem']}); texto lido na Rodada 3"; CTRL["situações atualizadas por revogação lida na Rodada 3"] += 1
    if a["tipo"] in ("ALTERA", "REVOGA (parcial)") and a.get("natureza", "") == "" and a["origem"] in R3N and a["destino"] in N:
        d = N[a["destino"]]
        if d.get("situacao", "") in ("", "sem alteração ou revogação registrada"):
            d["situacao"] = "alterada"; d["situacao_base"] = f"alterada por {a['origem']} ({a['disp_origem']}); texto lido na Rodada 3"; CTRL["situações atualizadas por alteração lida na Rodada 3"] += 1
        elif a["origem"] not in d.get("situacao_base", ""):
            d["situacao_base"] = (d["situacao_base"] + f"; também alterada por {a['origem']} ({a['disp_origem']}; texto lido na Rodada 3)").strip("; "); CTRL["situações complementadas por alteração lida na Rodada 3"] += 1

# ------------------------------------------------------------ 6. gravação
with open(f"{REPO}/base/nos.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, COLS_N); w.writeheader(); [w.writerow({c: x.get(c, "") for c in COLS_N}) for x in sorted(N.values(), key=lambda x: x["id"])]
with open(f"{REPO}/base/arestas.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, COLS_A); w.writeheader(); [w.writerow({c: a.get(c, "") for c in COLS_A}) for a in A]
with open(f"{REPO}/base/divergencias/reidentificacoes_r3.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f); w.writerow(["origem", "id_antigo", "id_novo", "motivo"]); w.writerows(sorted(set(REID)))
json.dump(dict(CTRL), open(f"{REPO}/base/controles/controles_r3.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
# manifesto
man_rows = []
for f in sorted(os.listdir(f"{W}/manifestos")):
    for ln in open(f"{W}/manifestos/{f}", encoding="utf-8"):
        p = ln.rstrip("\n").split("\t")
        if len(p) < 5: continue
        nome = p[0]; i = re.sub(r"\.(pdf|html)$", "", nome.split("__")[0])
        grp = "FEDERAL" if "camara" in f else "CNE" if "cne" in f else "UNIDADES"
        man_rows.append([i, "", "", N.get(i, {}).get("numero", ""), p[4], f"originais_r3/{grp}/{nome}", p[1], p[2], p[3]])
with open(f"{REPO}/base/manifesto_originais.tsv", "a", encoding="utf-8", newline="") as f:
    for r in man_rows: f.write("\t".join(r) + "\n")
CTRL["linhas acrescentadas ao manifesto"] = len(man_rows)
print(json.dumps(dict(CTRL), ensure_ascii=False, indent=1))
print("nós:", len(N), "arestas:", len(A))

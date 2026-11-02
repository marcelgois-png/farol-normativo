"""Rodada 4: correções apontadas pela conferência independente (P1–P5, 4c, 5b e completude). Aplicadas uma vez sobre a base."""
import csv, re
csv.field_size_limit(10**9)
REPO = "/home/claude/farol-normativo"
N = {r["id"]: r for r in csv.DictReader(open(f"{REPO}/base/nos.csv", encoding="utf-8"))}; CN = list(next(iter(N.values())).keys())
A = list(csv.DictReader(open(f"{REPO}/base/arestas.csv", encoding="utf-8"))); CA = list(A[0].keys())
REID = []; CTRL = {}
def no(i, **kw):
    if i not in N:
        x = {c: "" for c in CN}; x.update(id=i, nivel="N4", status_coleta="citada — a coletar"); N[i] = x
    N[i].update({k: v for k, v in kw.items() if v}); return N[i]
def reid(old, new, mot):
    for a in A:
        for c in ("origem", "destino"):
            if a[c] == old:
                a[c] = new; a["obs"] = (a["obs"] + f" | Rodada 4 (conferência): {c} reidentificado {old} → {new} ({mot})").strip(" |"); REID.append((a["origem"] if c == "destino" else "—", old, new, mot))
    if old in N: no(new); del N[old]
# 4c / P2 / 5b: citações sem órgão dentro de portarias do MEC são atos do próprio MEC; duplicatas fundidas
reid("BR-MEC-PORT-40-2007", "BR-MEC-PORTNORM-40-2007", "mesmo ato: Portaria Normativa MEC 40, de 12/12/2007 (e-MEC), republicada em 29/12/2010; ID duplicado fundido")
for n, a_ in (("19", "2016"), ("23", "2016"), ("24", "2012"), ("10", "2017")):
    reid(f"BR-?-PORT-{n}-{a_}", f"BR-MEC-PORTNORM-{n}-{a_}", f"Portaria Normativa MEC {n}/{a_}, nomeada e revogada pelo art. 105 da Portaria Normativa MEC 23/2017")
    no(f"BR-MEC-PORTNORM-{n}-{a_}", tipo="Portaria normativa", orgao="MEC", numero=f"{n}/{a_}")
reid("BR-?-PORT-343-2020", "BR-MEC-PORT-343-2020", "Portaria MEC 343, de 17/3/2020, citada pela Portaria MEC 473/2020 que lhe prorroga o prazo; nó já existente")
reid("BR-?-PORT-18-2012", "BR-MEC-PORTNORM-18-2012", "Portaria Normativa MEC 18, de 11/10/2012 (Lei de Cotas), citada no preâmbulo da PN MEC 9/2017; nó já existente")
reid("BR-?-PORT-270-2021", "BR-MEC-PORT-270-2021", "nó antigo remanescente da reidentificação do bloco C, ainda usado como origem de sugestão")
no("BR-?-PORT-33-1978", obs="órgão não identificado com segurança: a Portaria MEC 554/2019, art. 13, cita a 'Portaria nº 33, de 2 de agosto de 1978, do Departamento de Assuntos Universitários' (DAU/MEC), órgão extinto; mantida sem órgão até localizar o ato")
no("BR-?-PORT-1243-2009", obs="órgão não identificado com segurança: citada pela Portaria CAPES 183/2016 como a portaria que reajusta os valores do art. 2º da Lei 11.273/2006 (bolsas), provavelmente conjunta MEC/CAPES; mantida sem órgão até localizar o ato")
# P1: PN 11/2017, art. 32 — revoga a PN 18/2016 por inteiro e dispositivos da PN 40/2007
for a in A:
    if a["origem"] == "BR-MEC-PORTNORM-11-2017" and a["destino"] == "BR-MEC-PORTNORM-18-2016" and a["tipo"] == "REVOGA (total)":
        a["disp_origem"] = "art. 32"; a["confianca"] = "alta"; a["inicio_efeito"] = N["BR-MEC-PORTNORM-11-2017"]["data"]; base_p1 = a
x = {c: "" for c in CA}; x.update(dict(base_p1)); x.update(destino="BR-MEC-PORTNORM-40-2007", tipo="REVOGA (parcial)", disp_destino="arts. 13, 44, 45, 47, 48, 50, 51, 53, 54, § 3º do art. 57, arts. 55 e 60, inciso V do art. 61, § 2º do art. 61-F e § 2º do art. 63",
         obs="Rodada 4 (conferência): revogação parcial da PN 40/2007 pelo art. 32 da PN 11/2017, registrada à mão a partir do texto (D86)"); A.append(x)
# P2: art. 105 da PN 23/2017 revoga expressamente as PN 40/2007, 19/2016, 23/2016, 24/2012 e 10/2017
d23 = N["BR-MEC-PORT-23-2017"]["data"]
for a in A:
    if a["origem"] == "BR-MEC-PORT-23-2017" and a["disp_origem"] == "art. 105" and a["destino"].startswith("BR-MEC-PORTNORM-") and a["destino"] != "BR-MEC-PORTNORM-40-2007" or (a["origem"] == "BR-MEC-PORT-23-2017" and a["destino"] == "BR-MEC-PORTNORM-40-2007" and a["tipo"] == "REVOGA (total)"):
        if a["tipo"] == "REMETE A" and "que " in a["trecho"]:  # cada alínea do art. 105 nomeia o ato revogado
            a["tipo"] = "REVOGA (total)"; a["disp_destino"] = "norma inteira"; a["obs"] = (a["obs"] + " | Rodada 4 (conferência): ato enumerado no art. 105 ('Revogam-se…')").strip(" |")
        if a["tipo"] == "REVOGA (total)":
            a["confianca"] = "alta"; a["inicio_efeito"] = d23
            d = N[a["destino"]]; d["situacao"] = "revogada"; d["situacao_base"] = f"revogada por BR-MEC-PORT-23-2017 (art. 105); texto lido na Rodada 4"
# remover REMETE A duplicados que viraram REVOGA (mesma chave)
seen = set(); A2 = []
for a in A:
    k = (a["origem"], a["destino"], a["tipo"], a["disp_origem"], a["disp_destino"])
    if a["origem"] == "BR-MEC-PORT-23-2017" and a["disp_origem"] == "art. 105":
        if k in seen: continue
        seen.add(k)
    A2.append(a)
A = A2
# P3: Portaria MEC 374/2020 revogada pela 383/2020
for a in A:
    if a["origem"] == "BR-MEC-PORT-383-2020" and a["destino"] == "BR-MEC-PORT-374-2020" and a["tipo"] == "REVOGA (total)":
        a["confianca"] = "alta"; a["inicio_efeito"] = N["BR-MEC-PORT-383-2020"]["data"]
        N["BR-MEC-PORT-374-2020"].update(situacao="revogada", situacao_base="revogada por BR-MEC-PORT-383-2020 (art. 3º); texto lido na Rodada 4", tipo="Portaria", orgao="MEC", numero="374/2020", data="2020-04-03")
# P4: Lei PB 10.601/2015, art. 2º, revoga o art. 2º da Lei PB 3.489/1967
for a in A:
    if a["origem"] == "PB-LEI-10601-2015" and a["destino"] == "PB-LEI-3489-1967" and a["tipo"] == "REVOGA (parcial)":
        a["disp_origem"] = "art. 2º"; a["confianca"] = "alta"; a["inicio_efeito"] = N["PB-LEI-10601-2015"]["data"]; a["obs"] = (a["obs"] + " | Rodada 4 (conferência): o OCR leu 'Art. r'; é o art. 2º (entre o art. 1º e o art. 3º)").strip(" |")
N["PB-LEI-3489-1967"].update(situacao="revogada parcialmente", situacao_base="art. 2º revogado por PB-LEI-10601-2015 (art. 2º); texto lido na Rodada 4")
# P5: Lei PB 1.366/1955, art. 24, revoga a Lei PB 1.070/1954 (conferido na imagem do PDF; o OCR leu 'Arte 2h2')
x = {c: "" for c in CA}; x.update(origem="PB-LEI-1366-1955", disp_origem="art. 24", destino="PB-LEI-1070-1954", disp_destino="norma inteira", tipo="REVOGA (total)", inicio_efeito="1955-12-02", base="texto (sapl.al.pb.leg.br)", confianca="alta", evidencias="1",
         fonte_texto="OCR conferido na imagem do PDF oficial", citacao="Lei nº 1.070, de 24 de setembro de 1954", trecho="Art. 24º - Ficam revogadas a Lei nº 1.070, de 24 de setembro de 1954, e as disposições em contrário.",
         obs="Rodada 4 (conferência): relação registrada à mão após leitura da página 7 do PDF; o OCR ('Arte 2h2 … 2h de setembro de 195lj') não permitiu a extração automática"); A.append(x)
N["PB-LEI-1070-1954"].update(situacao="revogada", situacao_base="revogada por PB-LEI-1366-1955 (art. 24); texto lido na Rodada 4")
# completude: inicio_efeito nas relações estruturais da rodada; confiança alta em revogação expressa; níveis das leis estaduais; sugestão redundante
import json
R4 = set(json.load(open("/home/claude/r4/saida/r4_nos.json", encoding="utf-8")))
for a in A:
    if a["origem"] in R4 and a["tipo"] in ("ALTERA", "REVOGA (total)", "REVOGA (parcial)", "REGULAMENTA") and not a["natureza"]:
        if not a["inicio_efeito"]: a["inicio_efeito"] = N[a["origem"]]["data"]
        if a["tipo"].startswith("REVOGA") and a["confianca"] == "baixa": a["confianca"] = "alta"
A = [a for a in A if not (a["origem"] == "BR-MEC-PORT-1038-2020" and a["destino"] == "BR-MEC-PORT-544-2020" and a["natureza"].startswith("sugest"))]
for i, x in N.items():
    if i.startswith("PB-LEI-"): x["nivel"] = "N2"; x["tipo"] = x["tipo"] or "Lei estadual"; x["orgao"] = x["orgao"] or "Paraíba"
    m = re.match(r"BR-([A-Z]+)-(PORTNORM|PORT|RES|IN|ON)-(\d+)-(\d{4})$", i)
    if m and not x["tipo"]:
        x["tipo"] = {"PORTNORM": "Portaria normativa", "PORT": "Portaria", "RES": "Resolução", "IN": "Instrução normativa", "ON": "Orientação normativa"}[m.group(2)]; x["orgao"] = x["orgao"] or m.group(1); x["numero"] = x["numero"] or f"{m.group(3)}/{m.group(4)}"
    if m and not x["numero"]: x["numero"] = f"{m.group(3)}/{m.group(4)}"
with open(f"{REPO}/base/nos.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, CN); w.writeheader(); [w.writerow(x) for x in sorted(N.values(), key=lambda x: x["id"])]
with open(f"{REPO}/base/arestas.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, CA); w.writeheader(); w.writerows(A)
rows = list(csv.reader(open(f"{REPO}/base/divergencias/reidentificacoes_r4.csv", encoding="utf-8")))
for r in rows[1:]:
    r[3] = r[3].replace("Lei estadual 1.366, de 3/12/1955", "Lei estadual 1.366, de 2/12/1955").replace("a busca no DOU mostra que a portaria foi editada por CNE/CES", "o ato citado é resolução do CNE/CES (DCN da extensão)")
rows += [[a, b, c, d] for a, b, c, d in sorted(set(REID))]
with open(f"{REPO}/base/divergencias/reidentificacoes_r4.csv", "w", encoding="utf-8", newline="") as f: csv.writer(f).writerows(rows)
# manifesto: linhas repetidas (textos da Rodada 3 acrescentados mais de uma vez)
lines = open(f"{REPO}/base/manifesto_originais.tsv", encoding="utf-8").read().split("\n"); seen = set(); out = []
for ln in lines:
    if ln in seen and ln.strip(): continue
    seen.add(ln); out.append(ln)
open(f"{REPO}/base/manifesto_originais.tsv", "w", encoding="utf-8", newline="").write("\n".join(out))
print("reidentificações:", len(set(REID)), "nós:", len(N), "arestas:", len(A), "manifesto:", len(lines), "→", len(out))

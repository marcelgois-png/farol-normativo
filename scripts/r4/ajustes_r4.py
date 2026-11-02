"""Rodada 4: ajustes conferidos no texto depois do merge (citações sem órgão dentro de portarias do MEC são atos do próprio MEC)."""
import csv, io
csv.field_size_limit(10**9)
REPO = "/home/claude/farol-normativo"
N = {r["id"]: r for r in csv.DictReader(open(f"{REPO}/base/nos.csv", encoding="utf-8"))}; CN = list(next(iter(N.values())).keys())
A = list(csv.DictReader(open(f"{REPO}/base/arestas.csv", encoding="utf-8"))); CA = list(A[0].keys())
COR = {"BR-?-PORT-40-2007": ("BR-MEC-PORT-40-2007", "Portaria Normativa MEC 40/2007 (e-MEC), citada e revogada pela Portaria Normativa MEC 23/2017, art. 105; nó já existente na base"),
       "BR-?-PORT-374-2020": ("BR-MEC-PORT-374-2020", "Portaria MEC 374, de 3/4/2020 (DOU 6/4/2020), revogada pela Portaria MEC 383/2020, art. 3º — ato do próprio MEC"),
       "BR-?-PORT-18-2016": ("BR-MEC-PORTNORM-18-2016", "Portaria Normativa MEC 18, de 15/8/2016, revogada pela Portaria Normativa MEC 11/2017, art. 32 — ato do próprio MEC")}
reid = []
for a in A:
    if a["destino"] in COR:
        nd, mot = COR[a["destino"]]; reid.append((a["origem"], a["destino"], nd, mot))
        a["obs"] = (a["obs"] + f" | Rodada 4: destino reidentificado {a['destino']} → {nd} ({mot})").strip(" |"); a["destino"] = nd
        if nd not in N:
            x = {c: "" for c in CN}; x.update(id=nd, tipo="Portaria normativa" if "PORTNORM" in nd else "Portaria", orgao="MEC", nivel="N4", status_coleta="citada — a coletar", obs="nó criado na Rodada 4 por reidentificação de citação (" + mot + ")"); N[nd] = x
        if a["origem"] == "BR-MEC-PORTNORM-11-2017" and nd == "BR-MEC-PORTNORM-18-2016" and a["tipo"] == "REVOGA (parcial)":
            a["tipo"] = "REVOGA (total)"; a["disp_destino"] = "norma inteira"; a["obs"] += " | art. 32 revoga a Portaria Normativa 18/2016 por inteiro (a revogação parcial refere-se à PN 40/2007)"
            N[nd]["situacao"] = "revogada"; N[nd]["situacao_base"] = "revogada por BR-MEC-PORTNORM-11-2017 (art. 32); texto lido na Rodada 4"
for old in COR:
    if old in N: del N[old]
for x in N.values():
    x["obs"] = x["obs"].replace("Rodada 4: Rodada 4:", "Rodada 4:")
with open(f"{REPO}/base/nos.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, CN); w.writeheader(); [w.writerow(x) for x in sorted(N.values(), key=lambda x: x["id"])]
with open(f"{REPO}/base/arestas.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, CA); w.writeheader(); w.writerows(A)
with open(f"{REPO}/base/divergencias/reidentificacoes_r4.csv", "a", encoding="utf-8", newline="") as f:
    csv.writer(f).writerows(sorted(set(reid)))
print("reidentificações acrescentadas:", len(set(reid)), "nós:", len(N))

"""Rodada 5 — correções aprovadas pela coordenação em 02/11/2026 (pendências 1 e 2 do relatório).

A. Reaplica as regras D92 e D93 aos textos federais das Rodadas 2–4 (textos/FEDERAL, CNE, OUTROS, PB que
   não são da Rodada 5), com o mesmo extrator e as mesmas regras (scripts/r5/regras_r5.py):
   - citação em item de artigo "Revogam-se:/Ficam revogados:" registrada como REMETE A vira REVOGA (parcial/total);
     a REMETE A antiga sai quando todas as ocorrências da citação estavam no artigo de revogação;
   - REVOGA (total) do extrator sobre "revoga dispositivos da Lei X" vira REVOGA (parcial).
   A situação do destino só muda se ele não tiver decisão fundamentada em decisoes_vigencia.json, se a origem
   não for de nível inferior, se a revogação não tiver efeito futuro e se a origem não for anterior ao destino.
B. Retira a relação REVOGA (total) BR-DEC-9191-2017 → BR-LC-95-1998 (D99) e reidentifica a
   "Lei nº 13.241, de 1941" da página do planalto (Lei 13.241/2015).
C. D102: relação ALTERA/REVOGA em que a origem é anterior ao destino (impossível) vira REMETE A, com a nota.
Uso: python scripts/r5/correcoes_r5.py   (na raiz do repositório)
"""
import csv, io, json, os, re, sys, collections
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..")); sys.path.insert(0, AQUI)
from extrator import extrai, prepara
from regras_r5 import spans_revogacao, d86
csv.field_size_limit(10**9)
REPO = os.path.abspath(os.path.join(AQUI, "..", ".."))
HOJE = "2026-11-02"
B = f"{REPO}/base"

def le(p):
    with open(p, encoding="utf-8", newline="") as f:
        r = csv.DictReader(io.StringIO(f.read().replace("\x00", "")))
        return r.fieldnames, list(r)

CN, nos = le(f"{B}/nos.csv"); CA, ar = le(f"{B}/arestas.csv")
N = {n["id"]: n for n in nos}
PROTEGIDAS = {d["norma"] for d in json.load(open(f"{B}/decisoes_vigencia.json", encoding="utf-8"))["situacao"]}
R5 = {n["id"] for n in nos if n.get("arquivo_local", "").startswith("originais_r5/")}
CTRL = collections.Counter(); LOG = []

def ano_id(i):
    if i == "UFPB-ESTATUTO-ANTERIOR-2002": return None
    m = re.search(r"-(\d{4})(?:-B)?$", i)
    return int(m.group(1)) if m else None

def nivel_ord(i):
    if i == "BR-CF-1988" or i.startswith("BR-EC-"): return 1
    if re.match(r"(BR|PB)-(LEI|LC|DL|MP|LDEL|DLG)-", i): return 2
    if i.startswith("BR-DEC-"): return 3
    return 4 if i.startswith(("BR-", "PB-")) else 5

# ---------------------------------------------------------------- B. relação errada e "Lei 13.241, de 1941"
antes = len(ar)
ar = [a for a in ar if not (a["origem"] == "BR-DEC-9191-2017" and a["destino"] == "BR-LC-95-1998" and a["tipo"] == "REVOGA (total)")]
CTRL["B: arestas retiradas (D99)"] = antes - len(ar)
for a in ar:
    for lado in ("origem", "destino"):
        if a[lado] == "BR-LEI-13241-1941":
            a[lado] = "BR-LEI-13241-2015"; a["obs"] = (a["obs"] + " | Rodada 5: 'Lei nº 13.241, de 1941' na página do planalto é a Lei 13.241/2015 (erro de digitação da fonte; D103)").strip(" |")
            if lado == "origem" and a.get("inicio_efeito") == "1941": a["inicio_efeito"] = "2015"
            CTRL["B: arestas reidentificadas (13.241/1941 → 2015)"] += 1
REID = [["base", "BR-LEI-13241-1941", "BR-LEI-13241-2015", "Rodada 5 (correções): a página do planalto anota 'Revogado pela Lei nº 13.241, de 1941'; a lei que altera a Lei 11.196/2005 é a 13.241, de 30/12/2015 (D103)"]]
if "BR-LEI-13241-1941" in N:
    del N["BR-LEI-13241-1941"]; CTRL["B: nós removidos"] += 1

# ---------------------------------------------------------------- A. reaplicação de D92/D93
def corpo(md):
    for marca in ("\n## Texto integral\n", "\n## Texto\n"):
        k = md.find(marca)
        if k >= 0: return md[k + len(marca):]
    return ""

idx = collections.defaultdict(list)
for a in ar: idx[(a["origem"], a["destino"])].append(a)
inv = set(N)
novas = []
for g in ("FEDERAL", "CNE", "OUTROS", "PB"):
    for f in sorted(os.listdir(f"{REPO}/textos/{g}")):
        i = f[:-3]
        if i in R5 or i not in N or not N[i]["status_coleta"].startswith("texto"): continue
        sem = re.sub(r"~~[^~]*~~", " ", corpo(open(f"{REPO}/textos/{g}/{f}", encoding="utf-8").read()))
        if len(sem) < 200: continue
        ano = ano_id(i) or 9999
        T = prepara(sem); rv = spans_revogacao(T)
        if not rv: continue
        CTRL["A: textos com artigo de revogação"] += 1
        rr, _ = extrai(sem, i, "FED", inv)
        conv = collections.defaultdict(list); resto = collections.Counter(); tot_conv = collections.Counter(); tot_keep = collections.Counter()
        for x in rr:
            if x.get("parte") in ("anotação de consolidação", "anotação junto a citação", "citação indireta") or x["destino"] == i: continue
            d = x["destino"]
            dentro = x.get("pos") is not None and any(a <= x["pos"] < b for a, b, _ in rv)
            if x["tipo"] == "REMETE A":
                alt = d86(T, x, ano) if dentro and x.get("parte") == "dispositivo" else None
                if alt:
                    ef = [e for a, b, e in rv if a <= x["pos"] < b and e]
                    conv[d].append((alt[0], alt[1], x.get("disp_origem") or "norma inteira", x.get("trecho", ""), ef[0] if ef else ""))
                else:
                    resto[d] += 1
            elif x["tipo"] == "REVOGA (total)" and x.get("pos") is not None:
                ant = re.sub(r"\s+", " ", T[max(0, x["pos"] - 90):x["pos"]])
                if (x.get("disp_destino") or "norma inteira") == "norma inteira" and re.search(r"(?i)(?:§|\b(?:dispositivos?|arts?\.|artigos?|incisos?|par[áa]grafos?)\b)[^;:]{0,60}$", ant):
                    tot_conv[d] += 1
                else:
                    tot_keep[d] += 1
        for d, occ in conv.items():
            if d not in N: continue
            if nivel_ord(i) > nivel_ord(d):
                CTRL["A: conversões barradas pela hierarquia"] += 1; continue
            for tp in ("REVOGA (total)", "REVOGA (parcial)"):
                oo = [o for o in occ if o[0] == tp]
                if not oo: continue
                if any(a["tipo"] == tp for a in idx[(i, d)]):
                    CTRL["A: revogação já registrada"] += 1; continue
                base_txt = next((a["base"] for a in idx[(i, d)] if a["base"].startswith("texto")), "texto")
                fonte = next((a["fonte_texto"] for a in idx[(i, d)] if a.get("fonte_texto")), "")
                a = {c: "" for c in CA}
                a.update(origem=i, destino=d, tipo=tp, disp_origem="; ".join(dict.fromkeys(o[2] for o in oo))[:200],
                         disp_destino="; ".join(dict.fromkeys(o[1] for o in oo))[:300], base=base_txt, confianca="alta", evidencias=str(len(oo)),
                         parte="dispositivo", fonte_texto=fonte, trecho=oo[0][3][:600], inicio_efeito=oo[0][4] or str(ano_id(i) or ""),
                         ressalva=(f"revogação com efeito a partir de {oo[0][4][8:10]}/{oo[0][4][5:7]}/{oo[0][4][:4]}" if oo[0][4] else ""),
                         obs=f"Rodada 5 (correções): D92 reaplicada ao texto já no acervo — citação em item de artigo de revogação; {len(oo)} ocorrência(s)")
                novas.append(a); idx[(i, d)].append(a); CTRL[f"A: relações novas {tp}"] += 1
                LOG.append([i, d, tp, a["disp_destino"][:120], a["trecho"][:200]])
            if resto[d] == 0:
                rem = [a for a in idx[(i, d)] if a["tipo"] == "REMETE A" and a["parte"] in ("dispositivo", "") and not a.get("natureza")]
                for a in rem:
                    a["_apagar"] = True; CTRL["A: REMETE A retiradas (a citação era a revogação)"] += 1
        for d, n in tot_conv.items():
            if tot_keep[d] or d not in N: continue
            for a in idx[(i, d)]:
                if a["tipo"] == "REVOGA (total)" and a["parte"] not in ("anotação de consolidação",) and not a.get("natureza") and "Rodada 5 (correções)" not in a["obs"]:
                    a["tipo"] = "REVOGA (parcial)"; a["disp_destino"] = a["disp_destino"] if a["disp_destino"] != "norma inteira" else "dispositivos (não especificados no trecho)"
                    a["obs"] = (a["obs"] + " | Rodada 5 (correções): D93 — 'revoga dispositivos da…' é revogação parcial").strip(" |")
                    CTRL["A: REVOGA (total) → parcial (D93)"] += 1; LOG.append([i, d, "D93 total→parcial", "", a["trecho"][:200]])
                    dn = N[d]
                    if dn["situacao"] == "revogada" and i in dn.get("situacao_base", "") and d not in PROTEGIDAS:
                        dn["situacao"] = "revogada parcialmente"; dn["situacao_base"] = dn["situacao_base"] + " | Rodada 5 (correções): a revogação por " + i + " é parcial (D93)"
                        CTRL["A: situações revogada → revogada parcialmente (D93)"] += 1
ar = [a for a in ar if not a.get("_apagar")] + novas

# situação dos destinos das revogações novas
CONFLITOS = []
for a in novas:
    d = N[a["destino"]]; i = a["origem"]
    ief = a.get("inicio_efeito", "")
    if len(ief) == 10 and ief > HOJE:
        d["situacao_base"] = (d.get("situacao_base", "") + f"; revogação programada por {i} com efeito a partir de {ief[8:10]}/{ief[5:7]}/{ief[:4]}").strip("; ")
        CTRL["A: revogações programadas (efeito futuro)"] += 1; continue
    if a["destino"] in PROTEGIDAS:
        CONFLITOS.append([a["destino"], i, a["tipo"], "destino com decisão fundamentada em decisoes_vigencia.json; situação mantida"]); continue
    s = d.get("situacao", "")
    if a["tipo"] == "REVOGA (total)":
        if not s.startswith("revogada") or s == "revogada parcialmente":
            d["situacao"] = "revogada"; d["situacao_base"] = f"revogada por {i} ({a['disp_origem']}); D92 reaplicada na Rodada 5" + (f" | antes: {s}" if s else "")
            CTRL["A: situações → revogada"] += 1
    else:
        if s in ("", "sem alteração ou revogação registrada", "vigente"):
            d["situacao"] = "revogada parcialmente"; d["situacao_base"] = f"revogada parcialmente por {i} ({a['disp_destino'][:80]}); D92 reaplicada na Rodada 5"
            CTRL["A: situações → revogada parcialmente"] += 1
        elif s == "alterada":
            d["situacao"] = "alterada e revogada parcialmente"; d["situacao_base"] = (d.get("situacao_base", "") + f"; revogada em parte por {i} (D92 reaplicada na Rodada 5)").strip("; ")
            CTRL["A: situações → alterada e revogada parcialmente"] += 1

# ---------------------------------------------------------------- C. D102: cronologia
for a in ar:
    if a["tipo"] in ("ALTERA", "REVOGA (total)", "REVOGA (parcial)") and not a.get("natureza"):
        o, d = ano_id(a["origem"]), ano_id(a["destino"])
        if o and d and o < d:
            LOG.append([a["origem"], a["destino"], f"D102 {a['tipo']}→REMETE A", a["parte"], a["trecho"][:200]])
            a["obs"] = (a["obs"] + f" | Rodada 5 (correções, D102): registrada como {a['tipo']}, mas a origem ({o}) é anterior ao destino ({d}); provável anotação de redação ligada no sentido inverso — rebaixada a REMETE A").strip(" |")
            a["tipo"] = "REMETE A"; CTRL["C: relações cronologicamente impossíveis rebaixadas (D102)"] += 1
            dn = N.get(a["destino"])
            if dn and a["origem"] in dn.get("situacao_base", "") and dn["situacao"].startswith(("revogada", "alterada")) and a["destino"] not in PROTEGIDAS:
                CONFLITOS.append([a["destino"], a["origem"], "D102", f"situação '{dn['situacao']}' citava a relação rebaixada; conferir"])

# ---------------------------------------------------------------- gravação
ids = set(N)
orf = [a for a in ar if a["origem"] not in ids or a["destino"] not in ids]
assert not orf, orf[:3]
def grava(p, campos, linhas):
    with open(p, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos, lineterminator="\r\n", extrasaction="ignore"); w.writeheader(); w.writerows(linhas)
grava(f"{B}/nos.csv", CN, sorted(N.values(), key=lambda x: x["id"]))
grava(f"{B}/arestas.csv", CA, ar)
p = f"{B}/divergencias/reidentificacoes_r5.csv"
_, old = le(p)
with open(p, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, lineterminator="\r\n"); w.writerow(["origem", "id_antigo", "id_novo", "motivo"])
    w.writerows([[r["origem"], r["id_antigo"], r["id_novo"], r["motivo"]] for r in old] + REID)
with open(f"{B}/controles/correcoes_r5.tsv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t", lineterminator="\n"); w.writerow(["origem", "destino", "mudanca", "dispositivo/parte", "trecho"]); w.writerows(LOG)
json.dump({"controles": dict(CTRL), "conflitos": CONFLITOS}, open(f"{B}/controles/controles_correcoes_r5.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(dict(CTRL), ensure_ascii=False, indent=1)); print("conflitos:", len(CONFLITOS), CONFLITOS[:8]); print("nós:", len(N), "arestas:", len(ar))

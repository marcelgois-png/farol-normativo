"""Rodada 4: textos coletados (DOU/MEC, leis da Paraíba) -> nós, relações extraídas e textos JSON para o merge.
Entradas: fichas_r4.json, txt/<GRUPO>/<ID>.txt, manifestos/*.tsv. Saída: saida/r4_nos.json, r4_rel.json, r4_txt.json"""
import csv, json, os, re, sys, unicodedata, collections, glob
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))  # scripts/extrator.py
from extrator import extrai
csv.field_size_limit(10**9)
REPO = "/home/claude/farol-normativo"; W = "/home/claude/r4"; HOJE = "2026-11-02"
NFC = lambda s: unicodedata.normalize("NFC", s)
N = {r["id"]: r for r in csv.DictReader(open(f"{REPO}/base/nos.csv", encoding="utf-8"))}
inv = set(N)
NIV = lambda i: "N1" if i.startswith(("BR-CF", "BR-EC")) else "N2" if re.match(r"(BR|PB)-(LEI|LC|DL|MP)-", i) else "N3" if i.startswith("BR-DEC") else "N4" if i.startswith("BR-") else "N10" if re.match(r"UFPB-[A-Z]+-PORT-", i) else "N9"
man = {}
for f in glob.glob(f"{W}/manifestos/*.tsv"):
    for ln in open(f, encoding="utf-8"):
        p = ln.rstrip("\n").split("\t")
        if len(p) >= 5: man[p[0]] = dict(bytes=p[1], sha256=p[2], ct=p[3], url=p[4])
U = json.load(open(f"{W}/fichas_r4.json", encoding="utf-8"))
nos, rels, TXT = {}, [], {}
os.makedirs(f"{W}/saida", exist_ok=True)
for i, v in U.items():
    f = f"{W}/txt/{v['grupo']}/{i}.txt"
    if not os.path.exists(f): print("sem texto", i); continue
    t = NFC(open(f, encoding="utf-8", errors="replace").read())
    mf = man.get(i + v["ext"], {})
    nos[i] = dict(id=i, tipo=v["tipo"], orgao=v["orgao"], numero=v["numero"], data=v["data"], ementa=v["ementa"], nivel=v["nivel"], situacao="", situacao_base="",
                  status_coleta=f"texto integral ({v['dominio']})", metodo_texto=v["metodo"], aviso_texto=v.get("aviso", ""), fonte=mf.get("url", ""), fonte_arquivo=mf.get("url", ""),
                  arquivo_local=f"originais_r4/{v['grupo']}/{i}{v['ext']}", texto_acervo=f"textos/{'FEDERAL' if v['grupo']=='MEC' else 'PB'}/{i}.md", data_coleta=HOJE, sha256=mf.get("sha256", ""),
                  grupo=("FEDERAL" if v["grupo"] == "MEC" else "PB"), epigrafe=v["epigrafe"], versao="original publicado (alterações posteriores não incorporadas)")
    TXT[i] = t
    r, info = extrai(t, i, "FED", inv | set(U) | {i})
    for x in r:
        if x["destino"] == i or x.get("parte") in ("citação indireta", "anotação de consolidação"): continue
        if x["tipo"] in ("ALTERA", "REVOGA (total)", "REVOGA (parcial)") and NIV(x["destino"]) < NIV(i):
            x["tipo"] = "REMETE A"; x["obs"] = (x.get("obs", "") + " bloqueio hierárquico").strip()
        if x["destino"].startswith("UFPB-") and not re.search(r"UFPB|Universidade Federal da Para", x.get("trecho", "")): continue
        rels.append(dict(origem=i, destino=x["destino"], tipo=x["tipo"], disp_origem=x.get("disp_origem") or "norma inteira", disp_destino=x.get("disp_destino") or "norma inteira",
                         natureza=x.get("natureza", ""), base=f"texto ({v['dominio']})", confianca=x.get("confianca", ""), evidencias="1", parte=x.get("parte", ""), fonte_texto=v["metodo"],
                         citacao=x.get("citacao", ""), ressalva=x.get("ressalva", ""), trecho=(x.get("trecho") or "")[:600], obs=x.get("obs", "")))
json.dump(nos, open(f"{W}/saida/r4_nos.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump({"relacoes": rels}, open(f"{W}/saida/r4_rel.json", "w", encoding="utf-8"), ensure_ascii=False)
json.dump(TXT, open(f"{W}/saida/r4_txt.json", "w", encoding="utf-8"), ensure_ascii=False)
print("nós:", len(nos), "relações:", len(rels), collections.Counter(x["tipo"] for x in rels))
print("destinos novos:", len({x["destino"] for x in rels} - inv - set(nos)))

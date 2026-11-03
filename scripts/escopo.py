"""Escopo da fila de coleta (decisão da coordenação, 02/11/2026; D104).

A fila de coleta contém só:
  (A) normas internas da UFPB (IDs UFPB-…) ainda sem texto;
  (B) normas externas citadas diretamente por uma norma da UFPB com texto no acervo.
Ficam fora da fila, com status próprio, e continuam no mapa como nós sem texto:
  (C) normas externas que só alteram ou revogam uma norma citada pela UFPB (cadeia de vigência): coleta por demanda;
  (D) normas citadas só por normas externas (expansão em cadeia das leis federais) e normas sem citação.
As alteradoras só anotadas em texto compilado (D90) continuam com o status delas.
O script é reexecutável: a cada rodada a classificação é recalculada e uma norma que passar a ser citada
por norma da UFPB volta à fila.
Uso: python scripts/escopo.py   (na raiz do repositório)
"""
import csv, io, json, os, collections
csv.field_size_limit(10**9)
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
B = f"{REPO}/base"
FORA_C = "fora do escopo da fila — altera ou revoga norma citada pela UFPB (cadeia de vigência); coleta por demanda (D104)"
FORA_D = "fora do escopo da fila — citada só por normas externas (D104)"
ESTR = ("ALTERA", "REVOGA (total)", "REVOGA (parcial)", "SUPERA", "REGULAMENTA")

def le(p):
    with open(p, encoding="utf-8", newline="") as f:
        r = csv.DictReader(io.StringIO(f.read().replace("\x00", "")))
        return r.fieldnames, list(r)

CN, nos = le(f"{B}/nos.csv"); _, ar = le(f"{B}/arestas.csv")
N = {n["id"]: n for n in nos}
tem_texto = lambda i: N.get(i, {}).get("status_coleta", "").startswith("texto")
interna = lambda i: i.startswith("UFPB-")
citada_ufpb = {a["destino"] for a in ar if interna(a["origem"]) and tem_texto(a["origem"]) and a.get("parte") != "anotação de consolidação"}
vigencia = {a["origem"] for a in ar if a["destino"] in citada_ufpb and a["tipo"] in ESTR and not a.get("natureza")}
CTRL = collections.Counter()
for i, n in N.items():
    st = n["status_coleta"]
    if st.startswith(("texto", "alteradora anotada")):
        continue
    if interna(i) or i in citada_ufpb:
        if st.startswith("fora do escopo"):
            ant = n.get("obs", "").rsplit("status anterior: ", 1)
            n["status_coleta"] = ant[1].split(" |")[0].strip() if len(ant) == 2 else "citada — a coletar"
            n["obs"] = (n["obs"] + " | D104: voltou à fila (passou a ser citada por norma da UFPB)").strip(" |")
            CTRL["voltaram à fila"] += 1
        CTRL["na fila: " + ("A interna da UFPB" if interna(i) else "B citada por norma da UFPB")] += 1
        continue
    novo = FORA_C if i in vigencia else FORA_D
    if st != novo:
        if not st.startswith("fora do escopo"):
            n["obs"] = (n.get("obs", "") + f" | status anterior: {st}").strip(" |")
        n["status_coleta"] = novo; CTRL["status mudado para fora do escopo"] += 1
    CTRL["fora da fila: " + ("C cadeia de vigência" if novo == FORA_C else "D citada só por normas externas ou sem citação")] += 1

with open(f"{B}/nos.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=CN, lineterminator="\r\n"); w.writeheader(); w.writerows(sorted(N.values(), key=lambda x: x["id"]))
json.dump(dict(CTRL), open(f"{B}/controles/escopo_fila.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(dict(CTRL), ensure_ascii=False, indent=1))

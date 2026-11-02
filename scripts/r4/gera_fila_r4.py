"""Regenera base/fila_coleta.md após a Rodada 4 (mesmo formato das rodadas anteriores)."""
import csv, re, collections
csv.field_size_limit(10**9)
REPO = "/home/claude/farol-normativo"
N = {r["id"]: r for r in csv.DictReader(open(f"{REPO}/base/nos.csv", encoding="utf-8"))}
A = list(csv.DictReader(open(f"{REPO}/base/arestas.csv", encoding="utf-8")))
cit = collections.Counter(a["destino"] for a in A if a["origem"].startswith("UFPB-") and a["destino"] in N)
sem = [n for n in N.values() if not n["status_coleta"].startswith("texto")]
def grupo(i):
    if re.match(r"UFPB-(CONSEPE|CONSUNI|CURADOR)-", i): return "Resoluções dos conselhos superiores da UFPB sem texto"
    if i.startswith("UFPB-REGIMENTO-"): return "Regimentos de unidades (pedido da coordenação em 02/11/2026)"
    if i.startswith("UFPB-"): return "Normas de unidades, pró-reitorias e reitoria da UFPB"
    if i.startswith(("BR-CNE", "BR-CFE", "BR-CONAES")): return "CNE/CFE/CONAES"
    if i.startswith(("BR-MEC", "BR-CAPES", "BR-INEP", "BR-SERES", "BR-CNPQ", "BR-FNDE")): return "MEC e autarquias"
    if re.match(r"BR-(LEI|DEC|DL|LC|EC|MP)-", i): return "Leis e decretos"
    if i.startswith(("?", "OUTRO", "BR-?")) or "-?-" in i: return "Órgão não identificado ou outra instituição"
    return "Outros órgãos federais, conselhos profissionais e estaduais"
G = collections.defaultdict(list)
for n in sem: G[grupo(n["id"])].append(n)
ordem = ["Resoluções dos conselhos superiores da UFPB sem texto", "MEC e autarquias", "CNE/CFE/CONAES", "Outros órgãos federais, conselhos profissionais e estaduais",
         "Órgão não identificado ou outra instituição", "Normas de unidades, pró-reitorias e reitoria da UFPB", "Leis e decretos", "Regimentos de unidades (pedido da coordenação em 02/11/2026)"]
out = ["# Farol Normativo · Fila de coleta (após a Rodada 4)", "",
       "Atualizada em 02/11/2026. Normas citadas no acervo e ainda sem texto, ordenadas pelo número de resoluções da UFPB que as citam. A lista completa está em `base/nos.csv` (status_coleta diferente de \"texto integral\"). "
       "Status \"fonte oficial não acessível\": o ato foi identificado, mas não há texto em fonte oficial alcançável. Status \"norma estadual ou municipal, fora da fonte federal (Rodada 4)\": a citação é a lei ou decreto de outro ente federativo (Paraíba, João Pessoa, Santa Rita, Rio Tinto, Mamanguape), cuja fonte oficial não foi coletada nesta rodada. "
       "Status \"citada — não localizada em fonte oficial acessível (Rodada 4)\": o ato foi procurado no portal oficial e não consta do índice (ex.: pareceres antigos do CNE; portarias do MEC e da CAPES anteriores a 2013, que o índice pesquisável do DOU não cobre; Lei estadual 875/1953 ausente do SAPL da ALPB).", ""]
for g in ordem:
    lst = G.get(g, [])
    if not lst: continue
    lst.sort(key=lambda n: (-cit[n["id"]], n["id"]))
    nc = sum(1 for n in lst if cit[n["id"]])
    out.append(f"## {g} ({len(lst)}; {nc} citadas por resoluções da UFPB)" if "Regimentos" not in g else f"## {g} ({len(lst)} sem texto próprio)")
    out.append("")
    if "Regimentos" in g:
        out.append("Regimentos ainda não localizados após a Rodada 4. Para cada unidade, a ficha indica o ato de criação ou estrutura que vale enquanto o regimento não é localizado. Os 17 regimentos localizados saíram da fila: o texto é o anexo da resolução do CONSUNI que os aprovou (textos/REGIMENTOS/).")
        out.append("")
        for n in lst: out.append(f"- {n['id']} — {n['ementa'].split(' — ')[0]} — {n['status_coleta']} — {n['fonte']}")
    else:
        for n in lst[:40]:
            st = n["status_coleta"]
            out.append(f"- {n['id']} — citada por {cit[n['id']]} resolução(ões) da UFPB" + (f"; {st}" if st != "citada — a coletar" else ""))
        if len(lst) > 40: out.append(f"- … e mais {len(lst)-40}")
    out.append("")
open(f"{REPO}/base/fila_coleta.md", "w", encoding="utf-8", newline="\n").write("\n".join(out))
print({g: len(v) for g, v in G.items()}, "total", len(sem))

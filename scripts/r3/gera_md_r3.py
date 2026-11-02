"""Rodada 3: gera textos/<GRUPO>/<ID>.md para os atos coletados e textos/REGIMENTOS/<ID>.md para os regimentos
de unidades localizados como anexo de resolução (texto copiado do Markdown da resolução, nunca editado à mão)."""
import csv, json, os, re, collections, unicodedata
csv.field_size_limit(10**9)
REPO = "/home/claude/marcelgois-png/farol-normativo"; W = "/home/claude/r3"
N = {r["id"]: r for r in csv.DictReader(open(f"{REPO}/base/nos.csv", encoding="utf-8"))}
A = list(csv.DictReader(open(f"{REPO}/base/arestas.csv", encoding="utf-8")))
entra, sai = collections.defaultdict(list), collections.defaultdict(list)
for a in A: entra[a["destino"]].append(a); sai[a["origem"]].append(a)
R3N = json.load(open(f"{W}/saida/r3_nos.json", encoding="utf-8"))
R3T = json.load(open(f"{W}/saida/r3_txt.json", encoding="utf-8"))
y = lambda v: '"' + (v or "").replace('"', "'").replace("\n", " ") + '"'
EST = ("ALTERA", "REVOGA (total)", "REVOGA (parcial)", "REGULAMENTA")
n = 0
for i, v in R3N.items():
    x = N[i]; grp = v["grupo"]; txt = unicodedata.normalize("NFC", R3T[i])
    pasta = f"{REPO}/textos/{grp}"; os.makedirs(pasta, exist_ok=True)
    h = ["---", f"id: {i}", f"tipo: {y(x['tipo'])}", f"orgao: {y(x['orgao'])}", f"numero: {y(x['numero'])}", f"data: {y(x['data'])}", f"nivel: {x['nivel']}",
         f"situacao: {y(x['situacao'])}", f"situacao_base: {y(x['situacao_base'])}", f"ementa: {y(x['ementa'])}", f"fonte_oficial: {x['fonte']}",
         f"arquivo_local: {y(x['arquivo_local'])}", f"sha256: {v.get('sha256','')}", f"metodo_texto: {y(x['metodo_texto'])}", f"versao: {v.get('versao','')}", f"data_coleta: {x['data_coleta']}", "---", ""]
    c = [f"# {v.get('epigrafe') or i}", ""]
    if x["ementa"]: c += [f"**Ementa:** {x['ementa']}", ""]
    c += [f"**Situação no acervo:** {x['situacao'] or 'sem alteração ou revogação registrada'}" + (f" — {x['situacao_base']}" if x["situacao_base"] else ""), ""]
    if v.get("publicacao"): c += [f"**Publicação:** {v['publicacao']}", ""]
    if "-PAR-" in i and x.get("obs"): c += [f"**Natureza:** parecer do CNE ({x['obs'].split(' | ')[0]}). Parecer não tem força normativa própria; o projeto de resolução que o acompanha só vale depois de homologado e publicado como resolução.", ""]
    c += [f"**Fonte oficial:** {x['fonte']}", ""]
    ufpb = sorted({a["origem"] for a in entra[i] if a["origem"].startswith("UFPB-")})
    if ufpb: c += [f"**Resoluções da UFPB que a citam ({len(ufpb)}):** " + ", ".join(ufpb[:80]) + (f" … (+{len(ufpb)-80})" if len(ufpb) > 80 else ""), ""]
    est = [a for a in sai[i] if a["tipo"] in EST and not a["natureza"]]
    if est: c += ["**Esta norma sobre outras:**", ""] + [f"- **{a['tipo']}** {a['destino']} ({a['disp_destino'][:120]}) — nesta norma: {a['disp_origem'][:60]}" for a in est[:60]] + [""]
    mud = [a for a in entra[i] if a["tipo"] in EST and not a["natureza"]]
    if mud: c += ["**Outras normas sobre esta:**", ""] + [f"- **{a['tipo']}** por {a['origem']}" + (f" ({a['base']})" if a.get("base") else "") for a in mud[:60]] + [""]
    fund = sorted({a["destino"] for a in sai[i] if a["tipo"] == "FUNDAMENTA-SE EM"})
    if fund: c += ["**Fundamenta-se em:** " + ", ".join(fund), ""]
    c += ["> Transcrição para consulta. Não substitui a publicação oficial (link acima).", "", "---", "", "## Texto integral", "", txt.strip(), ""]
    open(f"{pasta}/{i}.md", "w", encoding="utf-8", newline="\n").write("\n".join(h + c)); n += 1
print("textos .md da rodada:", n)

# regimentos: cópia do texto da resolução que os aprova
REG = json.load(open(f"{W}/regimentos.json", encoding="utf-8"))
os.makedirs(f"{REPO}/textos/REGIMENTOS", exist_ok=True); m = 0
idx = {p.stem if hasattr(p, 'stem') else None: p for p in []}
import pathlib
textos = {p.stem: p for p in pathlib.Path(f"{REPO}/textos").rglob("*.md")}
for sigla, v in REG.items():
    if not v.get("res"): continue
    i = f"UFPB-REGIMENTO-{sigla}"; x = N[i]; src = textos.get(v["res"])
    if not src: print("sem texto da resolução:", v["res"]); continue
    s = src.read_text(encoding="utf-8")
    corpo = s.split("## Texto integral", 1)[1] if "## Texto integral" in s else s.split("## Texto", 1)[1]
    h = ["---", f"id: {i}", "tipo: Regimento", f"orgao: {y(x['orgao'])}", f"numero: {y(x['numero'])}", f"data: {y(x['data'])}", "nivel: N8", f"situacao: {y(x['situacao'])}", f"situacao_base: {y(x['situacao_base'])}",
         f"ementa: {y(x['ementa'])}", f"ato_de_aprovacao: {v['res']}", f"fonte_oficial: {x['fonte']}", f"arquivo_local: {y(x['arquivo_local'])}", f"metodo_texto: {y(x['metodo_texto'])}",
         f"versao: texto do regimento conforme publicado como anexo da {v['rotulo']} (SIGRH); alterações posteriores não incorporadas", f"data_coleta: {x['data_coleta']}", "---", "",
         f"# Regimento — {x['orgao']}", "", f"**Ementa:** {x['ementa']}", "", f"**Ato de aprovação:** {v['rotulo']} ({v['res']}). O texto abaixo é o mesmo extraído do original dessa resolução; não foi editado à mão.", "",
         f"**Situação no acervo:** {x['situacao'] or 'sem alteração ou revogação registrada'}" + (f" — {x['situacao_base']}" if x["situacao_base"] else ""), "", f"**Fonte oficial:** {x['fonte']}", "",
         "> Transcrição para consulta. Não substitui a publicação oficial.", "", "---", "", "## Texto integral", corpo.strip(), ""]
    (pathlib.Path(f"{REPO}/textos/REGIMENTOS") / f"{i}.md").write_text("\n".join(h), encoding="utf-8", newline="\n"); m += 1
print("regimentos .md:", m)

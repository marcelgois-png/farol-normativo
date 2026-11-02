"""Rodada 5: gera textos/FEDERAL/<ID>.md (leis, decretos, MPs e emendas do planalto e da Câmara) a partir dos textos extraídos.
Uso: python scripts/r5/gera_md_r5.py /home/claude/r5"""
import csv, json, os, re, sys, collections, unicodedata
csv.field_size_limit(10**9)
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
W = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/r5"
N = {r["id"]: r for r in csv.DictReader(open(f"{REPO}/base/nos.csv", encoding="utf-8"))}
A = list(csv.DictReader(open(f"{REPO}/base/arestas.csv", encoding="utf-8")))
entra, sai = collections.defaultdict(list), collections.defaultdict(list)
for a in A: entra[a["destino"]].append(a); sai[a["origem"]].append(a)
R3N = json.load(open(f"{W}/saida/r5_nos.json", encoding="utf-8"))
R3T = json.load(open(f"{W}/saida/r5_txt.json", encoding="utf-8"))
y = lambda v: '"' + (v or "").replace('"', "'").replace("\n", " ") + '"'
EST = ("ALTERA", "REVOGA (total)", "REVOGA (parcial)", "REGULAMENTA")
n = 0
for i, v in R3N.items():
    x = N[i]; grp = "FEDERAL"; txt = unicodedata.normalize("NFC", R3T[i])
    pasta = f"{REPO}/textos/{grp}"; os.makedirs(pasta, exist_ok=True)
    h = ["---", f"id: {i}", f"tipo: {y(x['tipo'])}", f"orgao: {y(x['orgao'])}", f"numero: {y(x['numero'])}", f"data: {y(x['data'])}", f"nivel: {x['nivel']}",
         f"situacao: {y(x['situacao'])}", f"situacao_base: {y(x['situacao_base'])}", f"ementa: {y(x['ementa'])}", f"fonte_oficial: {x['fonte']}", f"texto_compilado: {v.get('url_compilado','')}", f"epigrafe: {y(v.get('epigrafe',''))}",
         f"arquivo_local: {y(x['arquivo_local'])}", f"sha256: {v.get('sha256','')}", f"metodo_texto: {y(x['metodo_texto'])}", f"aviso_texto: {y(x.get('aviso_texto',''))}", f"versao: {v.get('versao','')}", f"data_coleta: {x['data_coleta']}", "---", ""]
    c = [f"# {v.get('epigrafe') or i}", ""]
    if x["ementa"]: c += [f"**Ementa:** {x['ementa']}", ""]
    c += [f"**Situação no acervo:** {x['situacao'] or 'sem alteração ou revogação registrada'}" + (f" — {x['situacao_base']}" if x["situacao_base"] else ""), ""]
    if v.get("notas_topo"): c += [f"**Notas da página oficial:** " + (v["notas_topo"] if isinstance(v["notas_topo"], str) else "; ".join(v["notas_topo"])), ""]
    if x.get("aviso_texto"): c += [f"**Aviso sobre o texto:** {x['aviso_texto']}", ""]
    if "-PAR-" in i and x.get("obs"): c += [f"**Natureza:** parecer do CNE ({x['obs'].split(' | ')[0]}). Parecer não tem força normativa própria; o projeto de resolução que o acompanha só vale depois de homologado e publicado como resolução.", ""]
    c += [f"**Fonte oficial:** {x['fonte']}" + (f" · texto compilado: {v['url_compilado']}" if v.get("url_compilado") else ""), ""]
    ufpb = sorted({a["origem"] for a in entra[i] if a["origem"].startswith("UFPB-")})
    if ufpb: c += [f"**Resoluções da UFPB que a citam ({len(ufpb)}):** " + ", ".join(ufpb[:80]) + (f" … (+{len(ufpb)-80})" if len(ufpb) > 80 else ""), ""]
    est = [a for a in sai[i] if a["tipo"] in EST and not a["natureza"]]
    if est: c += ["**Esta norma sobre outras:**", ""] + [f"- **{a['tipo']}** {a['destino']} ({a['disp_destino'][:120]}) — nesta norma: {a['disp_origem'][:60]}" for a in est[:60]] + [""]
    mud = [a for a in entra[i] if a["tipo"] in EST and not a["natureza"]]
    if mud: c += ["**Outras normas sobre esta:**", ""] + [f"- **{a['tipo']}** por {a['origem']}" + (f" ({a['base']})" if a.get("base") else "") for a in mud[:60]] + [""]
    fund = sorted({a["destino"] for a in sai[i] if a["tipo"] == "FUNDAMENTA-SE EM"})
    if fund: c += ["**Fundamenta-se em:** " + ", ".join(fund), ""]
    c += ["> Transcrição para consulta. Não substitui a publicação oficial (link acima). ~~Tachado~~ = redação revogada ou alterada, como na página oficial.", "", "---", "", "## Texto integral", "", txt.strip(), ""]
    open(f"{pasta}/{i}.md", "w", encoding="utf-8", newline="\n").write("\n".join(h + c)); n += 1
print("textos .md da Rodada 5:", n)


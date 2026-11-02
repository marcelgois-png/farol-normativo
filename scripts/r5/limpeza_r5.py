"""Rodada 5 — limpeza da fila antes da coleta.

1. Remove 7 nós residuais de reidentificações da Rodada 2 (sem nenhuma aresta;
   as citações já foram transferidas ao nó identificado). Registrado em D89.
2. Marca as normas que só constam como alteradoras anotadas nos textos
   consolidados do planalto (origem de ALTERA/REVOGA, nunca citadas por norma
   alguma): status próprio, fora da fila de coleta por citação. D90.
3. Unifica IDs duplicados e o padrão das instruções normativas (D87/D91):
   BR-<ÓRGÃO>-IN-<n>-<ano>; Planejamento sempre BR-MPOG.

Uso: python scripts/r5/limpeza_r5.py  (na raiz do repositório)
"""
import csv, json, re, sys
from pathlib import Path

csv.field_size_limit(10**9)
RAIZ = Path(__file__).resolve().parents[2]
B = RAIZ / "base"

RESIDUAIS = ["BR-CNE-RES-3-2016", "BR-?-RES-4-2009", "BR-?-RES-3-2002", "BR-CNE-RES-1-2002",
             "BR-?-RES-5-2009", "BR-?-RES-3-2016", "BR-?-RES-8-2008"]

# id_antigo -> id_novo (fusão quando id_novo já existe)
RENOMEIA = {
    "BR-IN-SGP-90-2021": "BR-SGP-IN-90-2021",
    "BR-IN-ME-90-2021": "BR-SGP-IN-90-2021",
    "BR-IN-CGU-3-2017": "BR-CGU-IN-3-2017",
    "BR-IN-CGU-1-2001": "BR-CGU-IN-1-2001",
    "BR-IN-CGU-8-2017": "BR-CGU-IN-8-2017",
    "BR-IN-CGU-13-2020": "BR-CGU-IN-13-2020",
    "BR-IN-CGU-18-2018": "BR-CGU-IN-18-2018",
    "BR-IN-SEGEP-2-2018": "BR-SEGEP-IN-2-2018",
    "BR-IN-SGP-36-2022": "BR-SGP-IN-36-2022",
    "BR-IN-SLTI-4-2010": "BR-SLTI-IN-4-2010",
    "BR-IN-MPOG-4-2010": "BR-SLTI-IN-4-2010",
    "BR-IN-SLTI-5-2014": "BR-SLTI-IN-5-2014",
    "BR-IN-?-2-2002": "BR-?-IN-2-2002",
    "BR-IN-?-4-2010": "BR-?-IN-4-2010",
    "BR-IN-?-4-2014": "BR-?-IN-4-2014",
    "BR-IN-?-9-2011": "BR-?-IN-9-2011",
    "BR-MP-PORT-150-2016": "BR-MPOG-PORT-150-2016",
    "BR-MP-PORT-155-2002": "BR-MPOG-PORT-155-2002",
    "BR-MP-CGU-IN-1-2016": "BR-MPOG-CGU-IN-1-2016",
    "BR-MP-MF-CGU-PORTINTER-507-2011": "BR-MPOG-MF-CGU-PORTINTER-507-2011",
}
MOTIVO = {
    "BR-IN-ME-90-2021": "mesmo ato: IN SGP/SEDGG/ME 90/2021, editada pela Secretaria de Gestão e Desempenho de Pessoal do Ministério da Economia",
    "BR-IN-MPOG-4-2010": "mesmo ato: IN SLTI/MPOG 4/2010 (contratação de soluções de TI), editada pela SLTI",
    "BR-MP-PORT-150-2016": "Planejamento sempre como MPOG, para não confundir com medida provisória (BR-MP-<n>-<ano>)",
}
STATUS_ALTERADORA = "alteradora anotada no texto consolidado do planalto — não citada; fora da fila por citação (Rodada 5)"


def le(p):
    with open(p, encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)


def grava(p, campos, linhas):
    with open(p, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos, lineterminator="\r\n")
        w.writeheader(); w.writerows(linhas)


def main():
    cn, nos = le(B / "nos.csv")
    ca, ar = le(B / "arestas.csv")
    ids = {n["id"] for n in nos}
    for a in RESIDUAIS:
        assert a in ids, a
        assert not any(x["origem"] == a or x["destino"] == a for x in ar), a
    nos = [n for n in nos if n["id"] not in RESIDUAIS]

    # 2. alteradoras anotadas
    destinos = {x["destino"] for x in ar}
    origens = {}
    for x in ar:
        origens.setdefault(x["origem"], []).append(x)
    n_alt = 0
    for n in nos:
        i = n["id"]
        if n["status_coleta"].startswith("texto") or i in destinos or i not in origens:
            continue
        if not re.match(r"BR-(LEI|DEC|DL|LC|MP|EC)-", i):
            continue
        if all("anotação no texto consolidado" in x["obs"] and x["fonte_texto"] == "planalto.gov.br" for x in origens[i]):
            n["status_coleta"] = STATUS_ALTERADORA
            n["obs"] = (n["obs"] + " | " if n["obs"] else "") + "Rodada 5: só aparece como alteradora/revogadora anotada em texto consolidado do planalto; a vigência do destino já está refletida no texto consolidado, por isso a coleta do ato é de baixa prioridade."
            n_alt += 1

    # 3. renomeações e fusões
    por_id = {n["id"]: n for n in nos}
    reident = []
    for antigo, novo in RENOMEIA.items():
        assert antigo in por_id, antigo
        velho = por_id.pop(antigo)
        if novo in por_id:
            alvo = por_id[novo]
            for k, v in velho.items():
                if v and not alvo.get(k):
                    alvo[k] = v
            alvo["obs"] = (alvo["obs"] + " | " if alvo["obs"] else "") + f"Rodada 5: fundido com {antigo} (D87/D91)."
            acao = "fusão"
        else:
            velho["id"] = novo
            if velho["orgao"] in ("IN", "MP", ""):
                m = re.match(r"BR-([A-Z?]+)-IN-", novo) or re.match(r"BR-(MPOG)", novo)
                if m:
                    velho["orgao"] = m.group(1)
            if novo.startswith("BR-?-IN") and not velho["tipo"]:
                velho["tipo"] = "Instrução Normativa"
            velho["obs"] = (velho["obs"] + " | " if velho["obs"] else "") + f"Rodada 5: ID padronizado (era {antigo}; D87/D91)."
            por_id[novo] = velho
            acao = "renomeação"
        reident.append({"origem": "base", "id_antigo": antigo, "id_novo": novo,
                        "motivo": f"Rodada 5 ({acao}, D87/D91): " + MOTIVO.get(antigo, "padrão único BR-<ÓRGÃO>-IN-<n>-<ano>; Planejamento como MPOG")})
    nos = list(por_id.values())
    vistas = set(); ar2 = []
    for x in ar:
        x["origem"] = RENOMEIA.get(x["origem"], x["origem"])
        x["destino"] = RENOMEIA.get(x["destino"], x["destino"])
        ch = (x["origem"], x["disp_origem"], x["destino"], x["disp_destino"], x["tipo"], x["trecho"])
        if ch in vistas:
            continue
        vistas.add(ch); ar2.append(x)

    grava(B / "nos.csv", cn, nos)
    grava(B / "arestas.csv", ca, ar2)
    grava(B / "divergencias" / "reidentificacoes_r5.csv", ["origem", "id_antigo", "id_novo", "motivo"], reident)

    # substituição dos IDs nos textos gerados (seção de relações) e demais arquivos vivos
    for p in list((RAIZ / "textos").rglob("*.md")) + [B / "quadro_vigencia.csv", B / "quadro_vigencia.md", B / "decisoes_vigencia.json", RAIZ / "tests" / "test_rotulos.py"]:
        if not p.exists():
            continue
        s = p.read_text(encoding="utf-8"); s0 = s
        for antigo, novo in RENOMEIA.items():
            s = re.sub(re.escape(antigo) + r"(?![\w-])", novo, s)
        if s != s0:
            p.write_text(s, encoding="utf-8")
    print(f"nós: {len(nos)} (removidos {len(RESIDUAIS)}, renomeados/fundidos {len(RENOMEIA)}); alteradoras anotadas marcadas: {n_alt}; arestas: {len(ar2)} (eram {len(ar)})")


if __name__ == "__main__":
    main()

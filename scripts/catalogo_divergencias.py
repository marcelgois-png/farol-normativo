"""Catálogo único das divergências do acervo.

Reúne, numa só tabela, tudo o que o acervo registra como divergência:
- base/divergencias/registro_divergencias.md (casos D01–D104, Rodadas 0, 1 e 3);
- base/decisoes_vigencia.json (decisões de vigência fundamentadas e sugestões de alvo provável);
- base/divergencias/divergencias_r2.csv (atos do CNE, Rodada 2);
- base/divergencias/divergencias_automaticas.csv (conferências automáticas texto × SIGRH).

Cada divergência recebe categoria (letra), subtipo (letra + dígito), gravidade (1 a 5)
e um número estável no formato <subtipo>-<sequência> (ex.: A1-003). Os números já
atribuídos são preservados entre execuções (lidos do catálogo anterior); os casos D
originais ficam na coluna "registro". Categoria e gravidade seguem as regras deste
arquivo, aplicadas a todos os casos do mesmo tipo: são classificação do Farol para
orientar a leitura, não decisão sobre o mérito.

    python scripts/catalogo_divergencias.py   # escreve base/divergencias/catalogo.csv
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "base" / "divergencias"
SAIDA = PASTA / "catalogo.csv"

CATEGORIAS = {
    "A": "Vigência — a norma (ou parte dela) está ou não em vigor",
    "B": "Fundamento — a norma se apoia em ato que foi revogado ou não a sustenta",
    "C": "Identificação e citação — qual norma é citada ou como ela é identificada",
    "D": "Fonte e cadastro oficial — SIGRH, páginas e arquivos oficiais divergem do texto",
    "E": "Texto da norma — erros materiais, numeração e datas no próprio ato",
    "F": "Método do acervo — regras de leitura e de escopo adotadas pelo Farol",
}
SUBTIPOS = {
    "A1": "Revogação contradita por atos posteriores (conflito de vigência)",
    "A2": "Revogação cujo alvo é provavelmente parcial ou outra norma",
    "A3": "Alteração ou revogação de norma já revogada (redundância, repristinação)",
    "A4": "Efeito temporal declarado no texto (vigência diferida, ultratividade, transição)",
    "A5": "Decisão de vigência fundamentada pelo Farol (regra aplicada sobre o registro)",
    "B1": "Fundamento em ato federal ou do CNE já revogado quando a norma foi editada",
    "B2": "Fundamento em ato federal ou do CNE revogado depois da edição",
    "B3": "Fundamento aparentemente impróprio ou desatualizado",
    "C1": "Número, ano, câmara ou tipo de ato citado provavelmente errado",
    "C2": "Identificação e padrão de ID (reidentificação, apelido consagrado)",
    "C3": "Alvo provável de citação ambígua (sugestão, não aplicada à vigência)",
    "C4": "Norma citada e não localizada em fonte oficial",
    "D1": "Documento trocado ou defeituoso na fonte oficial (SIGRH)",
    "D2": "Cadastro do SIGRH diverge do texto (ementa, título, relação não registrada)",
    "D3": "Página ou consolidado oficial diverge da norma ou está desatualizado",
    "D4": "Fonte, anexo ou texto não disponível (lacuna de acervo)",
    "E1": "Erro material no texto (número, data, remissão)",
    "E2": "Numeração e estrutura do texto (artigos repetidos, incisos ausentes)",
    "E3": "Datas divergentes (deliberação, assinatura, publicação)",
    "F1": "Regra de extração ou de leitura adotada",
    "F2": "Escopo e organização do acervo",
}
# gravidade padrão por subtipo: 1 mínima · 2 baixa · 3 média · 4 grave · 5 muito grave
GRAVIDADE = {"A1": 5, "A2": 4, "A3": 3, "A4": 3, "A5": 4, "B1": 4, "B2": 3, "B3": 2, "C1": 3, "C2": 2, "C3": 2, "C4": 2,
             "D1": 5, "D2": 2, "D3": 4, "D4": 3, "E1": 2, "E2": 2, "E3": 1, "F1": 1, "F2": 1}
NOME_GRAVIDADE = {1: "mínima", 2: "baixa", 3: "média", 4: "grave", 5: "muito grave"}

# tipos das conferências automáticas e da Rodada 2 → subtipo
TIPO_AUTO = {
    "Texto x SIGRH: relação não registrada no SIGRH": "D2",
    "Título/cabeçalho do texto × cadastro do SIGRH": "D2",
    "Ementa do SIGRH × ementa do texto": "D2",
    "SIGRH x texto: relação diferente": "D2",
    "SIGRH x texto: não confirmada": "D2",
    "Documento trocado no SIGRH": "D1",
    "Norma citada não localizada": "C4",
    "Efeito temporal declarado no texto": "A4",
    "Revogação de ato de criação com ressalva curricular": "A4",
    "Revogação redundante (norma já revogada)": "A3",
    "Repristinação expressa": "A3",
    "Revogação de norma já revogada (possível alvo trocado)": "A2",
    "Revogação de norma de assunto aparentemente distinto": "A2",
    "Revogação contradita por atos posteriores": "A1",
    "Registro excluído por decisão fundamentada": "A5",
    "Relação suspensa por decisão fundamentada": "A5",
    "Ementa e artigo revogam normas diferentes": "E1",
    "Alerta de citação (número × assunto) — conferir": "C1",
    "Divergência de citação (câmara do CNE)": "C1",
}
# tipo livre do registro em Markdown → subtipo (primeira regra que casar, em ordem)
REGRAS_MD = [
    (r"contradit|conflito entre textos|regimes de transi|substitui[çc][ãa]o n[ãa]o declarada", "A1"),
    (r"remiss[ãa]o gen[ée]rica|erro material \(alvo\)|alvo", "A2"),
    (r"altera[çc][ãa]o de norma revogada|repristina", "A3"),
    (r"leitura de vig[êe]ncia|vig[êe]ncia", "A5"),
    (r"fundamento desatualizado|remiss[ãa]o a norma revogada", "B2"),
    (r"fundamento", "B3"),
    (r"cita[çc][ãa]o|remiss[ãa]o aparentemente|tipo de ato trocado|erro de n[úu]mero|erro material \(n[úu]mero|provável erro de n[úu]mero", "C1"),
    (r"identifica[çc][ãa]o|padr[ãa]o de id|r[óo]tulo consagrado", "C2"),
    (r"documento trocado|arquivo oficial|arquivo errado|falha no original|texto copiado|links quebrados", "D1"),
    (r"erro da fonte oficial", "D3"),
    (r"qualidade do texto", "E1"),
    (r"cadastro|registro inconsistente|registro do sigrh|cadastro incompleto", "D2"),
    (r"consolida|anota[çc][ãa]o|formata[çc][ãa]o da p[áa]gina|leitura da fonte", "D3"),
    (r"lacuna de acervo|anexo|pend[êe]ncia|compet[êe]ncia a verificar|n[ãa]o dispon", "D4"),
    (r"lacuna", "E2"),
    (r"t[ée]cnica legislativa|numera", "E2"),
    (r"data", "E3"),
    (r"erro material|erros materiais|erro", "E1"),
    (r"extra[çc][ãa]o|r[óo]tulo de rela[çc][ãa]o|natureza do ato|regra", "F1"),
    (r"organiza[çc][ãa]o|escopo|m[ée]todo", "F2"),
]
_RE_ID = re.compile(r"\b((?:UFPB|BR|PB|OUTRO)-[A-Z0-9?\-]+-[0-9A-Z]+-(?:\d{4}|\?)|UFPB-REGIMENTO-[A-Z\-]+|UFPB-ESTATUTO-ANTERIOR-2002)\b")


_FIXOS = [(r"estatuto anterior", "UFPB-ESTATUTO-ANTERIOR-2002"), (r"minuta", "UFPB-NT-MINUTA-ESTATUTO-2019"), (r"estatuto", "UFPB-CONSUNI-RES-07-2002"),
          (r"regimento geral", "UFPB-REGIMENTO-GERAL"), (r"regimento da reitoria", "UFPB-CONSUNI-RES-257-1979"),
          (r"regimento dos [óo]rg[ãa]os|regimento da sods|279/78", "UFPB-CONSUNI-RES-279-1978")]
_RE_RES = re.compile(r"\b(CONSUNI|CONSEPE|Curador|CONSEPE/CONSUNI)\s*(?:nº\s*)?(\d{1,3})(?:-[A-Z])?/(\d{2,4})", re.I)
_RE_FED = re.compile(r"\b(Lei(?: Complementar)?|Decreto(?:-Lei)?|Decreto)\s*(?:nº\s*)?([\d.]+)(?:/|, de [^,;)]*?)(\d{4})", re.I)


def normas_citadas(texto: str, nos: dict) -> list[str]:
    """IDs das normas que um texto livre do registro menciona (só os que existem na base)."""
    achados: list[str] = []
    def junta(i: str) -> None:
        if i in nos and i not in achados:
            achados.append(i)
    for i in _RE_ID.findall(texto):
        junta(i)
    for org, num, ano in _RE_RES.findall(texto):
        ano = int(ano); ano = ano if ano > 100 else (1900 + ano if ano > 30 else 2000 + ano)
        o = "CURADOR" if org.lower() == "curador" else org.upper().split("/")[0]
        junta(f"UFPB-{o}-RES-{int(num):02d}-{ano}")
    for tipo, num, ano in _RE_FED.findall(texto):
        t = "LC" if "complementar" in tipo.lower() else "DL" if "decreto-lei" in tipo.lower() else "DEC" if tipo.lower().startswith("decreto") else "LEI"
        junta(f"BR-{t}-{num.replace('.', '')}-{ano}")
    for padrao, i in _FIXOS:
        if re.search(padrao, texto, re.I):
            junta(i)
    return achados


def subtipo_md(tipo: str) -> str:
    t = tipo.lower()
    for padrao, sub in REGRAS_MD:
        if re.search(padrao, t):
            return sub
    return "F2"


def chave(fonte: str, norma: str, outra: str, texto: str) -> str:
    return hashlib.sha1("|".join([fonte, norma, outra, texto[:160]]).encode("utf-8")).hexdigest()[:12]


def ler_md(nos: dict) -> list[dict]:
    itens = []
    secao = ""
    for linha in (PASTA / "registro_divergencias.md").read_text(encoding="utf-8").split("\n"):
        if linha.startswith("#"):
            secao = linha.strip("# ").strip()
            continue
        if not re.match(r"\|\s*D\d", linha):
            continue
        cel = [c.strip() for c in linha.strip().strip("|").split("|")]
        if len(cel) > 5:  # barra vertical dentro de uma célula: junta o excedente na observação
            cel = cel[:2] + [" | ".join(cel[2:-2])] + cel[-2:]
        d, onde, obs, tipo, enc = cel
        ids = normas_citadas(onde, nos) or normas_citadas(obs + " " + enc, nos)
        rodada = "Rodada 3" if "Rodada 3" in secao else "Rodada 1" if "Rodada 1" in secao else "Rodada 0"
        itens.append({"fonte": "registro (" + rodada + ")", "registro": d, "subtipo": subtipo_md(tipo), "tipo_original": tipo,
                      "norma": ids[0] if ids else "", "outra": ids[1] if len(ids) > 1 else "", "onde": onde,
                      "observacao": obs, "encaminhamento": enc})
    return itens


def ler_decisoes() -> list[dict]:
    dec = json.loads((RAIZ / "base" / "decisoes_vigencia.json").read_text(encoding="utf-8"))
    itens = []
    for d in dec.get("situacao", []):
        itens.append({"fonte": "decisão de vigência", "registro": d.get("divergencia", ""), "subtipo": "A5", "tipo_original": "decisão fundamentada",
                      "norma": d["norma"], "outra": "", "onde": d["norma"],
                      "observacao": f"Situação decidida: {d.get('situacao', '')}. {d.get('situacao_base', '')}",
                      "encaminhamento": f"{d.get('fundamento', '')} · {d.get('fonte', '')}".strip(" ·")})
    for s in dec.get("sugestoes", []):
        reg = re.search(r"D\d{2,3}", s.get("obs", "") or "")
        itens.append({"fonte": "decisão de vigência", "registro": reg.group(0) if reg else "", "subtipo": "C3", "tipo_original": "sugestão de alvo provável",
                      "norma": s["origem"], "outra": s["destino"], "onde": s["origem"],
                      "observacao": f"{s.get('tipo', '')} → alvo provável {s['destino']}: {s.get('natureza', '')}",
                      "encaminhamento": s.get("obs", "")})
    return itens


def ler_csv(nome: str, fonte: str, nos: dict) -> list[dict]:
    itens = []
    with open(PASTA / nome, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            tipo = r["tipo"]
            sub = TIPO_AUTO.get(tipo)
            outra = r.get("outra") or r.get("relacionada") or ""
            desc = r["descricao"]
            if tipo in ("Fundamento em ato do CNE revogado", "Fundamento em norma federal revogada"):
                sub = "B1" if "já estava revogad" in desc else "B2"
                if sub == "B2" and tipo == "Fundamento em norma federal revogada":
                    # compara a data da norma com a da revogadora, quando a base as tem
                    m = re.search(r"revogada por ((?:BR|PB)-[A-Z0-9\-]+-\d{4})", desc)
                    n, rv = nos.get(r["norma"]), nos.get(m.group(1)) if m else None
                    if n and rv and rv.get("data", "") and n.get("data", "") and rv["data"] < n["data"]:
                        sub = "B1"
            if not sub:
                sub = subtipo_md(tipo)
            itens.append({"fonte": fonte, "registro": "", "subtipo": sub, "tipo_original": tipo, "norma": r["norma"], "outra": outra,
                          "onde": r["norma"], "observacao": desc, "encaminhamento": ""})
    return itens


def gerar() -> list[dict]:
    nos: dict[str, dict] = {}
    with open(RAIZ / "base" / "nos.csv", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            nos[r["id"]] = r
    itens = ler_md(nos) + ler_decisoes() + ler_csv("divergencias_r2.csv", "conferência CNE (Rodada 2)", nos) + ler_csv("divergencias_automaticas.csv", "conferência automática texto × SIGRH", nos)
    anteriores: dict[str, str] = {}
    if SAIDA.exists():
        with open(SAIDA, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                anteriores[r["chave"]] = r["numero"]
    usados: dict[str, int] = defaultdict(int)
    for num in anteriores.values():
        sub, seq = num.split("-")
        usados[sub] = max(usados[sub], int(seq))
    for it in itens:
        it["chave"] = chave(it["fonte"], it["norma"], it["outra"], it["observacao"])
        it["categoria"] = it["subtipo"][0]
        it["gravidade"] = GRAVIDADE[it["subtipo"]]
        if it["chave"] in anteriores:
            it["numero"] = anteriores[it["chave"]]
    for it in itens:
        if "numero" not in it:
            usados[it["subtipo"]] += 1
            it["numero"] = f"{it['subtipo']}-{usados[it['subtipo']]:03d}"
    itens.sort(key=lambda x: (x["numero"].split("-")[0], int(x["numero"].split("-")[1])))
    campos = ["numero", "categoria", "subtipo", "gravidade", "registro", "norma", "outra", "onde", "observacao", "encaminhamento", "tipo_original", "fonte", "chave"]
    with open(SAIDA, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos, lineterminator="\n")
        w.writeheader()
        for it in itens:
            w.writerow({k: it.get(k, "") for k in campos})
    return itens


if __name__ == "__main__":
    its = gerar()
    from collections import Counter
    print(len(its), "divergências →", SAIDA.relative_to(RAIZ))
    print(sorted(Counter(i["subtipo"] for i in its).items()))
    print(sorted(Counter(i["gravidade"] for i in its).items()))
    sys.exit(0)

"""Derivações do grafo: dados da Teia, sugestões (irmãs e paralelas), dispositivos."""

from __future__ import annotations

import re
from collections import Counter

from .base import Base, Norma, Relacao
from .rotulos import CHAVE_RELACAO


def dados_teia(b: Base) -> dict:
    """JSON compacto consumido pela Teia (mesmo formato do protótipo)."""
    nodes = []
    for n in b.normas.values():
        nodes.append({
            "id": n.id, "l": n.rotulo, "o": n.orgao, "n": n.numero, "d": n.data_norm,
            "dy": n.ano, "nv": n.nivel, "s": n.situacao_chave, "sr": n.situacao,
            "sb": n.situacao_base[:300], "st": n.status_coleta, "t": n.temas,
            "e": (n.ementa or n.ementa_sigrh)[:260], "u": n.fonte, "g": 1 if n.fantasma else 0,
        })
    edges = []
    cit: list[list] = []
    vistos: set[tuple] = set()
    pares_cit: Counter = Counter()
    for r in b.relacoes:
        if r.origem not in b.normas or r.destino not in b.normas:
            continue
        if r.citacao_simples:
            pares_cit[(r.origem, r.destino)] += 1
            continue
        chave = (r.origem, r.destino, r.tipo, r.disp_origem, r.disp_destino)
        if chave in vistos:
            continue
        vistos.add(chave)
        edges.append({
            "s": r.origem, "t": r.destino, "k": CHAVE_RELACAO[r.tipo],
            "do": r.disp_origem[:80], "dd": r.disp_destino[:80],
            "ef": _data_norm(r.inicio_efeito), "ff": _data_norm(r.fim_efeito),
            "rs": r.ressalva[:160], "b": r.base[:60], "c": r.confianca, "q": r.trecho[:200],
            "sg": 1 if r.sugestao else 0, "nt": r.natureza[:160] if r.sugestao else "",
        })
    estruturais = {(e["s"], e["t"]) for e in edges}
    for (s, t), c in pares_cit.items():
        if (s, t) not in estruturais:
            cit.append([s, t, c])
    res = b.resumo()
    meta = {
        "nos": res["normas"], "arestas": len(edges), "citacoes": len(cit),
        "com_texto": res["com_texto"], "fantasmas": res["fantasmas"],
        "por_nivel": res["por_nivel"], "por_situacao": res["por_situacao"],
        "por_tipo": Counter(e["k"] for e in edges), "data_base": "2026-10-20", "rodada": "Rodada 2",
    }
    return {"meta": meta, "nodes": nodes, "edges": edges, "cit": cit}


def dados_fichas(b: Base) -> dict:
    """Índice compacto da busca."""
    nodes = []
    for n in b.normas.values():
        nodes.append({
            "id": n.id, "l": n.rotulo, "o": n.orgao, "n": n.numero, "d": n.data_norm, "dy": n.ano,
            "nv": n.nivel, "s": n.situacao_chave, "t": n.temas, "e": (n.ementa or n.ementa_sigrh)[:220],
            "g": 1 if n.fantasma else 0, "deg": b.grau_entrada(n.id) + b.grau_saida(n.id),
        })
    return {"nodes": nodes}


def _data_norm(d: str) -> str:
    d = (d or "").strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", d):
        return d
    if re.fullmatch(r"\d{4}", d):
        return d + "-01-01"
    return ""


def sugestoes(b: Base, id_: str, k: int = 6) -> tuple[list[tuple[str, int]], list[tuple[str, int]]]:
    """Normas irmãs (co-citação) e paralelas (acoplamento), fora das ligações diretas."""
    entrada = b.entrada.get(id_, [])
    saida = b.saida.get(id_, [])
    diretas = {r.origem for r in entrada} | {r.destino for r in saida} | {id_}
    irmas: Counter = Counter()
    for r in entrada:
        for f in b.saida.get(r.origem, []):
            if f.destino not in diretas:
                irmas[f.destino] += 1
    paralelas: Counter = Counter()
    for r in saida:
        for f in b.entrada.get(r.destino, []):
            if f.origem not in diretas:
                paralelas[f.origem] += 1
    return irmas.most_common(k), paralelas.most_common(k)


def por_dispositivo(b: Base, id_: str) -> list[tuple[str, list[tuple[str, Relacao, str]]]]:
    """Relações estruturais agrupadas pelo dispositivo desta norma."""
    grupos: dict[str, list] = {}
    for r in b.saida.get(id_, []):
        if r.citacao_simples:
            continue
        grupos.setdefault(r.disp_origem or "norma inteira", []).append(("→", r, r.destino))
    for r in b.entrada.get(id_, []):
        if r.citacao_simples:
            continue
        grupos.setdefault(r.disp_destino or "norma inteira", []).append(("←", r, r.origem))
    return sorted(grupos.items(), key=lambda kv: _ordem_disp(kv[0]))


def _ordem_disp(d: str) -> tuple:
    m = re.match(r"^\s*art(?:igo|\.)?\s*\.?\s*(\d+)", d, re.I)
    if m:
        return (0, int(m.group(1)), d)
    if d == "norma inteira":
        return (2, 0, d)
    return (1, 0, d)


def citacoes_para_links(b: Base, n: Norma) -> dict[str, tuple[str, str]]:
    """Texto citado → (destino, dispositivo), só quando a citação é inequívoca."""
    cit: dict[str, tuple[str, str]] = {}
    ambiguas: set[str] = set()
    for r in b.saida.get(n.id, []):
        c = (r.citacao or "").strip()
        if not c:
            continue
        if c in cit and cit[c][0] != r.destino:
            ambiguas.add(c)
        cit.setdefault(c, (r.destino, r.disp_destino))
    for c in ambiguas:
        cit.pop(c, None)
    return cit


# ---- anotações de vigência por artigo ---------------------------------------
TIPOS_VIGENCIA = ("ALTERA", "REVOGA (total)", "REVOGA (parcial)", "SUPERA")
_RE_ART_LISTA = re.compile(r"\bart(?:igo)?s?\.?\s*", re.I)
_RE_NUM = re.compile(r"(\d+)\s*[ºo°]?(?:-([A-Za-z])\b)?")
_RE_SEP = re.compile(r"\s*(?:,|;|\be\b|\bou\b|\ba\b|\baté\b)\s*", re.I)


def artigos_do_dispositivo(disp: str) -> list[str]:
    """Artigos citados num dispositivo da base, na ordem, sem repetição.

    "art. 5º" → ["5"]; "arts. 139 e 172 (COPERT → CPPD)" → ["139", "172"];
    "artigos 27 e 39 do Anexo I" → ["27", "39"]; "art. 7º-A; art. 18" → ["7-A", "18"];
    "arts. 232 a 235" → ["232", "233", "234", "235"]; "§ 2º do art. 5º" → ["5"].
    Faixas ("a", "até") só são expandidas quando têm até 30 artigos.
    """
    disp = disp or ""
    vistos: list[str] = []

    def junta(a: str) -> None:
        if a not in vistos:
            vistos.append(a)

    for m in _RE_ART_LISTA.finditer(disp):
        pos = m.end()
        anterior: int | None = None
        faixa = False
        while True:
            mn = _RE_NUM.match(disp, pos)
            if not mn:
                break
            num = int(mn.group(1))
            chave = mn.group(1) + ("-" + mn.group(2).upper() if mn.group(2) else "")
            if faixa and anterior is not None and not mn.group(2) and 0 < num - anterior <= 30:
                for k in range(anterior + 1, num):
                    junta(str(k))
            junta(chave)
            anterior = None if mn.group(2) else num
            ms = _RE_SEP.match(disp, mn.end())
            if not ms:
                break
            faixa = ms.group(0).strip().lower() in ("a", "até")
            pos = ms.end()
    return vistos


def notas_por_artigo(b: Base, id_: str) -> dict[str, list[Relacao]]:
    """Para cada artigo desta norma, as relações de alteração, revogação ou
    superação registradas na base que o alcançam (sugestões ficam de fora),
    em ordem cronológica de efeito."""
    notas: dict[str, list[Relacao]] = {}
    for r in b.entrada.get(id_, []):
        if r.tipo not in TIPOS_VIGENCIA or r.sugestao:
            continue
        for a in artigos_do_dispositivo(r.disp_destino):
            notas.setdefault(a, []).append(r)
    for lst in notas.values():
        lst.sort(key=lambda r: (_data_norm(r.inicio_efeito) or "9999", r.origem))
    return notas

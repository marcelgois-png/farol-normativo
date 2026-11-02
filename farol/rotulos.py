"""Rótulos, níveis e identificadores.

Regras fixas do projeto (ver CLAUDE.md): o ID padronizado tem a forma
<JURISDIÇÃO>-<ÓRGÃO...>-<TIPO>-<NÚMERO>-<ANO>, por exemplo
UFPB-CONSUNI-RES-07-2002, BR-LEI-9394-1996, BR-CNE-CES-RES-2-2019.
"""

from __future__ import annotations

import re

NIVEIS = ["N1", "N2", "N3", "N4", "N5", "N6", "N7", "N8", "N9", "N10", "NT", "MA", "?"]

NOME_NIVEL = {
    "N1": "Constituição Federal",
    "N2": "Leis",
    "N3": "Decretos federais",
    "N4": "MEC e órgãos federais",
    "N5": "Estatuto da UFPB",
    "N6": "Regimentos comuns",
    "N7": "Conselhos superiores",
    "N8": "Regimentos de unidades",
    "N9": "Conselhos de centro e colegiados",
    "N10": "Reitoria e pró-reitorias",
    "NT": "Em tramitação",
    "MA": "Material de apoio",
    "?": "Nível não identificado",
}

TIPOS_RELACAO = [
    "FUNDAMENTA-SE EM",
    "REGULAMENTA",
    "ALTERA",
    "REVOGA (total)",
    "REVOGA (parcial)",
    "SUPERA",
    "REMETE A",
    "DELEGA COMPETÊNCIA",
    "PROPÕE SUBSTITUIR",
]

# chave curta usada nos dados do site (uma letra por tipo)
CHAVE_RELACAO = {
    "FUNDAMENTA-SE EM": "F",
    "REGULAMENTA": "G",
    "ALTERA": "A",
    "REVOGA (total)": "R",
    "REVOGA (parcial)": "P",
    "SUPERA": "S",
    "REMETE A": "M",
    "DELEGA COMPETÊNCIA": "D",
    "PROPÕE SUBSTITUIR": "X",
}

# situação registrada na base -> chave curta usada no site
SITUACAO_CHAVE = {
    "": "desconhecida",
    "sem alteração ou revogação registrada": "vigente",
    "alterada": "alterada",
    "alterada e revogada parcialmente": "alterada",
    "revogada parcialmente": "alterada",
    "revogada": "revogada",
    "não localizada": "nao_localizada",
    "em tramitação": "tramitacao",
    "conflito de vigência (ver divergências)": "conflito",
    "a verificar (arquivo do SIGRH com texto de outra norma)": "verificar",
}

NOME_SITUACAO = {
    "vigente": "vigente",
    "alterada": "alterada",
    "revogada": "revogada",
    "nao_localizada": "não localizada",
    "tramitacao": "em tramitação",
    "conflito": "conflito de vigência",
    "verificar": "a verificar",
    "desconhecida": "situação não registrada",
}

_TIPO_NOME = {
    "RES": "Res.",
    "PORT": "Portaria",
    "LEI": "Lei",
    "DEC": "Decreto",
    "DL": "Decreto-Lei",
    "LC": "Lei Compl.",
    "EC": "EC",
    "MP": "MP",
    "PAR": "Parecer",
    "IN": "IN",
    "ON": "ON",
    "RDC": "RDC",
    "PORTNORM": "Port. Normativa",
    "PORTINTER": "Port. Interministerial",
    "PORTNORMINTER": "Port. Norm. Intermin.",
    "DLG": "Decreto Legislativo",
    "CF": "Constituição",
}

_ROTULOS_FIXOS = {
    "UFPB-REGIMENTO-GERAL": "Regimento Geral da UFPB",
    "UFPB-ESTATUTO-ANTERIOR-2002": "Estatuto anterior a 2002",
    "UFPB-NT-MINUTA-ESTATUTO-2019": "Minuta do novo Estatuto (NT)",
    "UFPB-CONSUNI-RES-07-2002": "Estatuto da UFPB (Res. CONSUNI 07/2002)",
    "UFPB-CONSUNI-RES-279-1978": "Regimento dos Órgãos Deliberativos (Res. CONSUNI 279/78)",
    "UFPB-CONSUNI-RES-257-1979": "Regimento da Reitoria (Res. CONSUNI 257/79)",
    "BR-CF-1988": "Constituição Federal de 1988",
}


# Centros de ensino da UFPB (site oficial, página "Centros de Ensino", lida em 02/11/2026).
CENTROS = {"CCEN", "CCHLA", "CCM", "CE", "CCSA", "CT", "CCS", "CCJ", "CBIOTEC", "CCTA", "CEAR", "CI", "CTDR", "CPT-ETS", "CCA", "CCHSA", "CCAE"}


def _fmt_numero(num: str) -> str:
    if re.fullmatch(r"\d{4,}", num):
        return f"{int(num):,}".replace(",", ".")
    return num


def rotulo(id_: str, orgao: str = "") -> str:
    """Nome curto e legível de uma norma a partir do ID (e do órgão da ficha)."""
    if id_ in _ROTULOS_FIXOS:
        return _ROTULOS_FIXOS[id_]
    if id_.startswith("UFPB-REGIMENTO-"):  # regimento de unidade: UFPB-REGIMENTO-<SIGLA>
        sigla = id_[len("UFPB-REGIMENTO-"):]
        return f"Regimento {'do' if sigla in CENTROS else 'da'} {sigla}"
    partes = id_.split("-")
    if len(partes) >= 3 and re.fullmatch(r"[\d?]{4}", partes[-1]):
        num, ano = partes[-2], partes[-1]
        meio = partes[1:-2]
        tk = next((p for p in meio if p in _TIPO_NOME), None)
        if tk:
            org = [p for p in meio if p != tk and p != "?"]
            if partes[0] == "PB":
                org = ["PB"] + org
            num = _fmt_numero(num)
            if partes[0] == "BR" and not org and tk in ("LEI", "DEC", "DL", "LC", "EC", "MP"):
                return f"{_TIPO_NOME[tk]} {num}/{ano}"
            o = "/".join(org) if org else (orgao or "?")
            return f"{_TIPO_NOME[tk]} {o} {num}/{ano}"
    return id_


def federal(id_: str) -> bool:
    return id_.startswith("BR-") or id_.startswith("PB-")


def slug(id_: str) -> str:
    """ID como segmento de URL (os IDs já são ASCII, exceto '?')."""
    return id_.replace("?", "_")


def ano_do_id(id_: str) -> str:
    m = re.search(r"-(\d{4})$", id_)
    return m.group(1) if m else ""

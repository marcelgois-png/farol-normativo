"""Rodada 5: regras de revogação usadas na extração (D92, D93 e efeito futuro).
Importado por processa_r5.py (textos da Rodada 5) e correcoes_r5.py (reaplicação aos textos das Rodadas 2–4)."""
import re
MESES = {"janeiro": 1, "fevereiro": 2, "marco": 3, "março": 3, "abril": 4, "maio": 5, "junho": 6, "julho": 7,
         "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12}

REVOG_ART_RE = re.compile(r"(?i)^\s*Art\.?\s*\d+[º°o.]*\s*[-–—.]?\s*(?:Revogam[-\s]se|Ficam?\s+revogad[oa]s?|Revoga[-\s]se|S[ãa]o\s+revogad[oa]s|Fica\s+revogad[oa])")
ART_RE = re.compile(r"(?m)^\s*Art\.?\s*\d+")

def efeito(cab):
    """Data de início de efeito da revogação ("Ficam revogados, a partir de 1º de janeiro de 2033:")."""
    m = re.search(r"(?i)a\s+partir\s+de\s+(\d{1,2})\s*[º°o]?\s+de\s+([a-zç]+)\s+de\s+(\d{4})", re.sub(r"\s+", " ", cab))
    if not m: return ""
    mm = MESES.get(m.group(2).lower(), 0)
    return f"{m.group(3)}-{mm:02d}-{int(m.group(1)):02d}" if mm else m.group(3)

def spans_revogacao(t):
    """D86/P2: trechos de artigos cuja cláusula é de revogação ("Revogam-se:", "Ficam revogados:")."""
    ps = [m.start() for m in ART_RE.finditer(t)] + [len(t)]
    out = []
    for a, b in zip(ps, ps[1:]):
        if REVOG_ART_RE.match(t[a:a + 200]):
            # o artigo termina no próximo artigo, no fecho ("Brasília, …") ou no primeiro anexo
            f = re.search(r"(?m)^\s*(?:Bras[íi]lia\s*,|Rio\s+de\s+Janeiro\s*,|ANEXO\b|Anexo\s+[IVXLC\d]+\b)", t[a:b])
            out.append((a, a + f.start() if f else b, efeito(t[a:a + 300])))
    return out

ITEM_SEP = re.compile(r"[;:]|\n\s*(?=(?:[IVXLC]+|\d+)\s*[-–—]|[a-z]\)|Art\.?\s*\d|§)|\.\s+(?=[A-ZÁÉÍÓÚ])")
DISP_ITEM = re.compile(r"(?i)§|\b(arts?\.?|artigos?|par[áa]grafos?|incisos?|al[íi]neas?|caput|dispositivos?|disposi[çc][õo]es|anexos?|itens?|tabelas?|cap[íi]tulos?|t[íi]tulos?|se[çc][ãa]o)\b")
NAO_ITEM = re.compile(r"(?i)\(\s*vide|\bvide\b|com\s+as\s+altera[çc][õo]es|\b(?:acrescentad|renumerad|introduzid|inclu[íi]d|transformad|convertid|alterad|mantid|ressalvad)[oa]s?\b|\bacresc\w*|\bem\s+vigor\b|\bexcet\w*|\bsalvo\b|reda[çc][ãa]o\s+dada|\b(altera|disp[õo]e|institui|cria|regulament|nos\s+termos|de\s+que\s+trata|prevista?|conforme|com\s+a\s+reda[çc][ãa]o)\b")

def d86(T, x, ano_o):
    """Decide se a citação em artigo de revogação é REVOGA (total/parcial). Devolve (tipo, disp_destino) ou None."""
    m = re.search(r"-(\d{4})$", x["destino"])
    if m and int(m.group(1)) > ano_o:
        return None                      # norma anterior não revoga posterior
    pos = x["pos"]
    ini = max([mm.end() for mm in ITEM_SEP.finditer(T, max(0, pos - 400), pos)] + [max(0, pos - 400)])
    item = re.sub(r"\s+", " ", T[ini:pos]).strip()
    # o caput do próprio artigo de revogação não é dispositivo do destino
    item = re.sub(r"(?i)^(?:Art\.?\s*\d+[º°o.]*\s*[-–—.]?\s*)?(?:Revogam[-\s]se|Ficam?\s+revogad[oa]s?|Revoga[-\s]se|S[ãa]o\s+revogad[oa]s|Fica\s+revogad[oa])\s*,?\s*", "", item)
    if NAO_ITEM.search(item) or len(item) > 220:
        return None
    if DISP_ITEM.search(item) or x["destino"] == "BR-CF-1988":
        dd = x.get("disp_destino") or "norma inteira"
        limpo = re.sub(r"(?i)^(?:[IVXLC]+\s*[-–—]\s*|[a-z]\)\s*)?(?:e\s+)?(?:o|a|os|as)\s+", "", item).strip(" ,;")
        limpo = re.sub(r"(?i)\s*(?:,?\s*tod[oa]s\s+)?(?:d[oa]s?|n[oa]s?)\s*$", "", limpo).strip(" ,;")
        _fim = re.search(r"\d{4}\s*[,:;]?", T[pos:pos + 160])
        if re.search(r"(?i)seguintes\s+dispositivos", limpo) and _fim:
            dep = T[pos + _fim.end():pos + _fim.end() + 600]
            fimlista = re.search(r"\n\s*[IVXLC]+\s*[-–—]|\n\s*Art\.", dep)
            dep = re.sub(r"\s+", " ", dep[:fimlista.start()] if fimlista else dep[:250]).strip(" :;")
            dd = ("seguintes dispositivos: " + dep)[:220]
        elif dd == "norma inteira" or len(DISP_ITEM.findall(limpo)) > 1:
            dd = limpo[:220] or "dispositivos listados"
        return ("REVOGA (parcial)", dd)
    # total só quando o item nomeia apenas normas ("I - o Decreto nº …"; "a Lei nº X, a Lei nº Y")
    resto = re.sub(r"(?i)^(?:[IVXLC]+\s*[-–—]\s*|[a-z]\)\s*|\d+\.\s*)", "", item)
    resto = re.sub(r"(?i)(?:Lei(?:s)?\s+Complementar(?:es)?|Leis?(?:\s+Delegadas?)?|Decretos?(?:[\s-]*Leis?|\s+Legislativos?)?|Medidas?\s+Provis[óo]rias?|Emendas?\s+Constitucionais?|Resolu[çc][õo]es?|Portarias?|Instru[çc][õo]es\s+Normativas?)"
                   r"[^,;]*?\d{4}", " ", resto)
    resto = re.sub(r"(?i)\b(?:e|o|a|os|as|n[ºo°.]*s?|n\s*os)\b|[,;:.\-–—]", " ", resto)
    if resto.strip():
        return None
    return ("REVOGA (total)", "norma inteira")


"""Farol Normativo — extrator de citações e relações normativas.

Lê o texto integral de uma norma e devolve:
  - as normas citadas (internas da UFPB e externas), normalizadas para o ID do acervo;
  - a relação de cada citação com a norma que cita (FUNDAMENTA-SE EM, REGULAMENTA,
    ALTERA, REVOGA total/parcial, REMETE A), com o dispositivo de origem (artigo da
    norma que cita), o dispositivo de destino (artigo citado), o trecho do texto e o
    grau de confiança da identificação.
  - anotações de consolidação do tipo "(Redação dada pela Resolução nº X)", que geram a
    relação inversa X → esta norma, no artigo em que aparecem.

Princípio: precisão antes de cobertura. Toda relação guarda o trecho literal que a
justifica; o que é inferência é marcado como tal.
"""
import re, unicodedata

MESES = {"janeiro": 1, "fevereiro": 2, "marco": 3, "março": 3, "abril": 4, "maio": 5, "junho": 6, "julho": 7,
         "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12}

def sem_acento(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()

def ano4(a):
    a = int(a)
    if a < 100:
        return 2000 + a if a <= 30 else 1900 + a
    return a

def numint(n):
    n = n.replace(".", "").replace(" ", "")
    m = re.match(r"(\d+)(-?[A-Za-z])?$", n)
    if not m:
        return None, ""
    return int(m.group(1)), (m.group(2) or "").replace("-", "").upper()

def id_ufpb(cons, n, suf, ano):
    s = str(n).zfill(2) + (suf or "")
    return f"UFPB-{cons}-RES-{s}-{ano}"

# ---------------------------------------------------------------------------
# Normalização do texto
# ---------------------------------------------------------------------------
CORTE_RE = re.compile(r"(?:SISTEMA\s+INTEGRADO\s+DE\s+PATRIM[ÔO]NIO,?\s+ADMINISTRA[ÇC][ÃA]O\s+E\s+CONTRATOS|FOLHA\s+DE\s+ASSINATURAS)", re.I)

def prepara(t):
    c = CORTE_RE.search(t)
    if c and c.start() > len(t) * 0.4:
        t = t[:c.start()]
    t = t.replace(" ", " ").replace("Ɵ", "ti").replace("ﬁ", "fi").replace("ﬂ", "fl").replace("\x02", "")
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\b([Ss])ubs tu", r"\1ubstitu", t); t = re.sub(r"\b([Ii])ns tu", r"\1nstitu", t); t = re.sub(r"\b([Cc])ons tu", r"\1onstitu", t)
    # junta hifenização de fim de linha (OCR/PDF)
    t = re.sub(r"(\w)-\n(\w)", r"\1\2", t)
    # marcadores inseridos na montagem do texto (OCR por página) e notas de redação
    t = re.sub(r"\[(?:fim da )?página \d+[^\]\n]*\]", "\n", t)
    t = re.sub(r"\(\s*NR\s*\)", "\n", t)
    # erros de OCR recorrentes em citações e dispositivos
    t = re.sub(r"(N\s*[º°o]\.?)\s*\(\s*(?=\d)", r"\1 ", t)
    t = re.sub(r"(?<=\d)\s*//\s*(?=\d)", "/", t)
    t = re.sub(r"\b(Anexo|ANEXO|inciso|Inciso|TABELA|Tabela|tabela|T[íi]tulo|Cap[íi]tulo)\s+\|", r"\1 I", t)
    t = re.sub(r"(?<=\s)Il(?=[\s,.;)]|$)", "II", t)
    t = re.sub(r"(?m)^\s*\|\s*[-–—]", "I -", t)
    t = re.sub(r"[\u200b-\u200f\u202a-\u202e\u2066-\u2069\u061f\u060c\u00ad]", "", t)
    t = re.sub(r"\b(Alterar|Revogar|Acrescentar|Suprimir|Incluir|Excluir|Modificar)(o|a|os|as)\b(?=\s)", r"\1 \2", t)
    t = re.sub(r"\be(o|a|os|as)\s+(Art|art|§|inciso|par[áa]grafo)", r"e \1 \2", t)
    return t

# ---------------------------------------------------------------------------
# Padrões
# ---------------------------------------------------------------------------
NUMTOK = r"(?:n\s*[º°o]\s*s?\.?|n\.\s*[º°o]s?|nº\.?|n°|nos?\.(?=\s*\d)|no(?=\s*\d)|número|num\.)"
NUMERO = r"\d{1,3}(?:\.\d{3})*(?:-?[A-Za-z](?![a-z]))?"
DATA_EXT = r"de\s+\d{1,2}\s*(?:º|°|o)?\s+de\s+[A-Za-zçÇ]+\s+de\s+\d{4}"
NUM_ANO = rf"{NUMERO}\s*/\s*\d{{2,4}}(?!\d)(?!\s*/\s*\d)"
NUM_DATA = rf"{NUMERO}\s*,?\s*{DATA_EXT}"
NUM_DE_ANO = rf"{NUMERO}\s*,\s*de\s+\d{{4}}(?!\d)"
ITEM = rf"(?:{NUM_ANO}|{NUM_DATA}|{NUM_DE_ANO})"
LISTA = rf"{ITEM}(?:\s*(?:,|;|\be\b|\bou\b)\s*(?:{NUMTOK}\s*)?{ITEM})*"

ORG_RES = (r"CONSEPE|Consepe|CONSUNI|Consuni|CONSUN|Conselho\s+Universit[áa]rio|"
           r"Conselho\s+Superior\s+de\s+Ensino,?\s+Pesquisa\s+e\s+Extens[ãa]o|Conselho\s+de\s+Ensino,?\s+Pesquisa\s+e\s+Extens[ãa]o|"
           r"Conselho\s+Curador|CURADOR|C[âa]mara\s+de\s+Educa[çc][ãa]o\s+(?:Superior|B[áa]sica)|CNE\s*/\s*CES|CNE\s*/\s*CP|CNE\s*/\s*CEB|CES\s*/\s*CNE|CP\s*/\s*CNE|CEB\s*/\s*CNE|CNE|CFE|CEPE|CONAES|CONSAD|CONTRAN|CNS|CONFEA|CFM|COFEN|CAPES|FNDE|CD/FNDE|ANVISA")

TIPOS = [
    ("RES", r"Resolu[çc](?:[ãa]o|[õo]es)|Res\.(?=\s)|Res(?=\.?\s*(?:n|\d))"),
    ("LC", r"Leis?\s+Complementar(?:es)?"),
    ("DL", r"Decretos?[-\s]+Leis?"),
    ("LEI", r"Leis?(?:\s+(?:Federal|Estadual|Ordin[áa]ria))?"),
    ("DEC", r"Decretos?(?:\s+(?:Federal|Presidencial|Estadual))?"),
    ("MP", r"Medidas?\s+Provis[óo]rias?"),
    ("EC", r"Emendas?\s+Constitucion(?:al|ais)"),
    ("PORT", r"Portarias?(?:\s+(?:Normativa|Ministerial|Interministerial|Conjunta))?"),
    ("PAR", r"Pareceres?"),
    ("IN", r"Instru[çc](?:[ãa]o|[õo]es)\s+Normativas?"),
    ("ON", r"Orienta[çc](?:[ãa]o|[õo]es)\s+Normativas?"),
]
TIPO_RE = "|".join(f"(?P<{k}>{v})" for k, v in TIPOS)
# órgão entre o tipo e o número (ex.: "Resolução CONSEPE nº", "Portaria MEC nº", "Parecer CNE/CES nº")
PRE_ORG = r"(?:\s*(?:do|da)?\s*(?P<preorg>[A-Z][A-Za-zÀ-ú]*(?:\s*/\s*[A-Z][A-Za-z]*)*(?:\s+(?:do|da)\s+[A-Z][A-Za-zÀ-ú]+)?|Conselho\s+(?:Universit[áa]rio|Curador|Superior\s+de\s+Ensino,?\s+Pesquisa\s+e\s+Extens[ãa]o))[\s/-]*(?:UFPB)?)?"
CIT_RE = re.compile(rf"(?P<tipo>{TIPO_RE}){PRE_ORG}\s*,?\s*(?:de\s+(?={NUMTOK}))?(?:{NUMTOK}\s*)?(?P<lista>{LISTA})", re.I)

NOMEADAS = [
    ("BR-CF-1988", r"Constitui[çc][ãa]o\s+(?:Federal|da\s+Rep[úu]blica(?:\s+Federativa\s+do\s+Brasil)?)|\bCF/88\b|\bCF\b(?=\s*,?\s*(?:art|de\s+1988))|Carta\s+Magna"),
    ("UFPB-CONSUNI-RES-07-2002", r"Estatuto\s+(?:da\s+(?:UFPB|Universidade(?:\s+Federal\s+da\s+Para[íi]ba)?)|desta\s+Universidade|vigente)|(?<=do\s)Estatuto\b(?!\s+d[aoe]s?\s+(?!UFPB\b|Universidade))(?!\s+(?:da\s+Crian|do\s+Idoso|da\s+Pessoa|dos?\s+Servidor|da\s+Juventude|da\s+Igualdade|do\s+Magist|da\s+Cidade|da\s+Metr))"),
    ("UFPB-REGIMENTO-GERAL", r"Regimento\s+Geral(?!\s+d[oa]s?\s+(?!UFPB\b|Universidade\s+Federal\s+da\s+Para))(?:\s+da\s+(?:UFPB|Universidade(?:\s+Federal\s+da\s+Para[íi]ba)?))?"),
    ("UFPB-CONSUNI-RES-279-1978", r"Regimento\s+dos\s+[ÓO]rg[ãa]os\s+Deliberativos(?:\s+(?:Superiores|da\s+Administra[çc][ãa]o\s+Superior))?|Regimento\s+da\s+SODS"),
    ("UFPB-CONSUNI-RES-257-1979", r"Regimento\s+(?:Geral\s+)?da\s+Reitoria"),
    ("BR-LEI-9394-1996", r"Lei\s+de\s+Diretrizes\s+e\s+Bases(?:\s+da\s+Educa[çc][ãa]o(?:\s+Nacional)?)?|\bLDB\b"),
    ("BR-LEI-8112-1990", r"Regime\s+Jur[íi]dico\s+[ÚU]nico|\bRJU\b"),
    ("BR-LEI-13709-2018", r"Lei\s+Geral\s+de\s+Prote[çc][ãa]o\s+de\s+Dados(?:\s+Pessoais)?|\bLGPD\b"),
    ("BR-LEI-12527-2011", r"Lei\s+de\s+Acesso\s+[àa]\s+Informa[çc][ãa]o"),
    ("BR-LEI-10861-2004", r"\bSINAES\b"),
    ("BR-LEI-11788-2008", r"Lei\s+do\s+Est[áa]gio"),
    ("BR-LEI-12711-2012", r"Lei\s+de\s+Cotas"),
]
NOMEADAS_RE = [(i, re.compile(p, re.I)) for i, p in NOMEADAS]

DISP_TOK = (r"(?:caput|par[áa]grafo\s+[úu]nico|§§\s*\d+\s*[º°o]?(?:\s*(?:,|e|a)\s*\d+\s*[º°o]?)*|§+\s*\d+\s*[º°o]?|tabelas?\s+(?:[IVX]+|\d+)(?:\s*(?:,|e)\s*(?:[IVX]+|\d+))*|anexos\s+[IVX]+(?:\s*(?:,|e)\s*[IVX]+)+|par[áa]grafos?\s+\d+[º°o]?|incisos?\s+[IVXLC]+(?:\s*(?:,|e|a)\s*[IVXLC]+)*|"
            r"al[íi]neas?\s+[\"“']?[a-z][\"”']?(?:\s*(?:,|e)\s*[\"“']?[a-z][\"”']?)*|itens?\s+\d+|"
            r"art(?:igo)?s?\.?\s*\d+\s*[º°o]?(?:-[A-Z](?![a-z]))?(?:\s*,\s*§\s*\d+\s*[º°o]?)?(?:\s*,\s*[IVXLC]+\b\.?)?(?:\s*(?:,|e|a|ao|à|até)\s*(?:o\s+)?\d+\s*[º°o]?(?:-[A-Z])?)*|Anexos?(?:\s+[IVX]+|\s+[ÚU]nico)?|Cap[íi]tulo\s+[IVXL]+|T[íi]tulo\s+[IVXL]+|Se[çc][ãa]o\s+[IVXL]+)")
DISP_FIM_RE = re.compile(rf"((?:{DISP_TOK})(?:\s*(?:,|;|\be\b|\bou\b)?\s*(?:(?:constantes?|previst[oa]s?|contid[oa]s?)\s+)?(?:d[oa]s?\b|n[oa]s?\b|o\b|a\b|os\b|as\b)?\s*(?:{DISP_TOK}))*)\s*[.,]?\s*(?:(?:ambos|ambas|todos|todas)\s+)?(?:(?:constantes?|previst[oa]s?|contid[oa]s?)\s+)?(?:d[oa]s?|n[oa]s?|pel[oa]s?|à|ao|aos|às|referid[oa]s?\s+n[oa])\s*(?:referid[oa]|citad[oa]|mencionad[oa])?\s*$", re.I)

VERBO_REVOGA = re.compile(r"\b(revog(?:a|am|ar|o|ou|aram|ando)|revogu(?:e|em)-se|revoca|revoga[çc][ãa]o|anula[çc][ãa]o|exclu(?:i|ir)\s+(?:o|a|os|as)\s+(?:art|§|inc|par[áa]g|al[íi]n)|ficam?\s+revogad[oa]s?|tornam?\s+sem\s+efeito|torna-se\s+sem\s+efeito|sem\s+efeito|anula|anular)\b", re.I)
VERBO_ALTERA = re.compile(r"\b(alter(?:a|am|ar)|altera[çc](?:[ãa]o|[õo]es)|modifica[çc](?:[ãa]o|[õo]es)|nova\s+reda[çc][ãa]o|d[áa]\s+nova\s+reda[çc][ãa]o|dar\s+nova\s+reda[çc][ãa]o|acrescent(?:a|ar|am)|acresc(?:e|er|enta)|inclu(?:i|ir)|inser(?:e|ir)|suprim(?:e|ir)|modific(?:a|ar)|passa(?:m)?\s+a\s+vigorar|retific(?:a|ar)|complement(?:a|ar)|substitu(?:i|ir)|renumer(?:a|ar))\b", re.I)
VERBO_NEUTRO = re.compile(r"\b(aprov(?:a|ar)|estabelec(?:e|er)|institu(?:i|ir)|disp[õo]e|cri(?:a|ar)|autoriz(?:a|ar)|fix(?:a|ar)|defin(?:e|ir)|homolog(?:a|ar)|norm(?:atiza|aliza)|concede|outorga|designa|reconhece|referenda|ratifica)\b", re.I)
VERBO_REGULA = re.compile(r"\b(regulament(?:a|ar|am)|disciplin(?:a|ar)\s+(?:o|a)\s+(?:disposto|aplica))\b", re.I)
PASSIVO_RE = re.compile(r"\b(alterad[oa]s?|revogad[oa]s?|modificad[oa]s?|reda[çc][ãa]o\s+dada|inclu[íi]d[oa]s?|acrescentad[oa]s?|acrescid[oa]s?|inserid[oa]s?|suprimid[oa]s?|renumerad[oa]s?|anulad[oa]s?)\s*(?:pel[oa]s?|por)\s*$", re.I)
_VERBO_ANOT = r"(?:alterad[oa]s?|revogad[oa]s?|modificad[oa]s?|reda[çc][ãa]o\s+dada|inclu[íi]d[oa]s?|acrescentad[oa]s?|acrescid[oa]s?|inserid[oa]s?|suprimid[oa]s?|renumerad[oa]s?|anulad[oa]s?)\s*(?:pel[oa]s?|por)"
# nota de alteração no próprio dispositivo: exige marcador explícito antes do verbo (artigo/§/inciso/alínea, "(*)" ou parêntese)
ANOT_INICIO_RE = re.compile(r"\s*(?:(?:(?:Art(?:igo)?\.?\s*\d+\s*[º°o]?(?:-[A-Z])?|§\s*\d+\s*[º°o]?|Par[áa]grafo\s+[úu]nico|[IVXLC]+|[a-z]\))\s*[.\-–—:)]*\s*(?:\(\*+\)\s*)?[-–—]?\s*\(?)|\(\*+\)\s*[-–—]?\s*\(?|\()\s*" + _VERBO_ANOT + r"\s*", re.I)
OBJETO_RE = re.compile(r"\b(Regulamento|Regimento|Estrutura(?:\s+(?:Acad[êe]mica|Curricular))?|Projeto\s+(?:Pol[íi]tico[- ])?Pedag[óo]gico|PPC|Anexos?(?:\s+[IVX]+)?|Composi[çc][ãa]o\s+Curricular|Ement[áa]rio|Matriz\s+Curricular|Fluxograma|Normas?\s+(?:Gerais|Complementares|Internas?)|Calend[áa]rio)\b", re.I)
OBJ_REF_RE = re.compile(r"(?:aprovad[oa]s?|regulamentad[oa]s?|regid[oa]s?|institu[íi]d[oa]s?|criad[oa]s?|homologad[oa]s?|estabelecid[oa]s?|definid[oa]s?)\s+(?:pel[oa]s?|por)\s*$|constantes?\s+(?:d[aoe]s?|n[oa]s?)\s*$|de\s+que\s+trata[m]?\s*$|(?:previst[oa]s?|dispost[oa]s?)\s+n[oa]s?\s*$|integrantes?\s+d[aoe]s?\s*$|(?:anexos?|Anexo\s+[IVX]+)\s+(?:à|ao|a|d[ao])\s*$|\(\s*$", re.I)
GENERICA_RE = re.compile(r"revogam-se\s+as\s+disposi[çc][õo]es\s+em\s+contr[áa]rio|revogadas\s+as\s+disposi[çc][õo]es\s+em\s+contr[áa]rio", re.I)
ANOTACAO_RE = re.compile(r"\((?P<verb>[^()]{0,40}?(?:Reda[çc][ãa]o\s+dada|Nova\s+reda[çc][ãa]o|Inclu[íi]d[oa]|Acrescentad[oa]|Acrescid[oa]|Inserid[oa]|Revogad[oa]|Alterad[oa]|Modificad[oa]|Suprimid[oa]|Renumerad[oa]|NR)[^()]{0,40}?)(?P<ref>(?:pel[oa]|por)\s[^()]{3,160})\)", re.I)
PREAMBULO_FUND = re.compile(r"\b(atribui[çc][õo]es|compet[êe]ncia|considerando|tendo\s+em\s+vista|com\s+base|com\s+fundamento|nos\s+termos|de\s+acordo|em\s+conformidade|conforme|disposto|consoante|amparad|fundamentad|à\s+luz)", re.I)

INICIO_CLAUSULA_RE = re.compile(r"^\s*(?:(?:Art(?:igo)?\.?\s*\d+\s*[º°o]?(?:-[A-Z](?![a-zà-ú]))?\s*[.\-–—:)]*|§\s*\d+\s*[º°o]?\s*[.\-–—:)]*|Par[áa]grafo\s+[úu]nico\s*[.\-–—:)]*|[IVXLC]+\s*[.\-–—:)]+|[a-z]\))\s*)+")
INICIO_REVOGA_RE = re.compile(r"^(?:(?:É|E|São|Sao)\s+revogad|Exclu(?:i|ir|i-se|em-se)\b|Fica[m]?\s+exclu[íi]d|Revoc(?:a|ar)\b|Revogu(?:e|em)-se\b|Fica[m]?\s+revogad|Revog(?:a|am|ar|a-se|am-se|ou|aram|ando)\b|Torna(?:m|r)?(?:-se)?\s+sem\s+efeito|Fica[m]?\s+sem\s+efeito|Anul|Ficam?\s+anulad|Declara[m]?(?:-se)?\s+(?:nul|revogad))", re.I)
# particípio absoluto: "..., revogada(s) a(s) Resolução(ões) ...", "ficando revogado o art. ... da", "tornando sem efeito a"
PARTICIPIO_REVOGA_RE = re.compile(r"(?:^|[,;:]\s*|\be\s+|\bficando\s+|\bsendo\s+|\bficam?\s+|\bdeclarad[oa]s?\s+)(?:tamb[ée]m\s+|ainda\s+|expressamente\s+|integralmente\s+)?(?:revogad[oaã]s?|anulad[oa]s?|tornando\s+sem\s+efeito|tornad[oa]s?\s+sem\s+efeito|sem\s+efeito)\s*,?\s*(?:(?:os|as)\s+(?:artigos|dispositivos|incisos|par[áa]grafos|itens|anexos)\s+d[aoe]s?\s*$|(?:a\s+partir|a\s+contar)\s+(?:d[aeo]s?|dest[ae]|dess[ae]|daquel[ae])\s+(?:\S+\s+){0,6}?\S+\s*,?\s*|nesta\s+data\s*,?\s*|na\s+data\s+de\s+sua\s+publica[çc][ãa]o\s*,?\s*)?(?:tamb[ée]m\s+|ainda\s+|expressamente\s+|integralmente\s+|especialmente\s+|em\s+especial\s+)?(?:a|o|as|os)?\s*$", re.I)
CONECTOR_LISTA_RE = re.compile(r"\s*(?:,|;)?\s*(?:e|bem\s+como|al[ée]m\s+d[ao]s?)?\s*(?:a|o|as|os)?\s*", re.I)
INICIO_ALTERA_RE = re.compile(r"^(?:Autoriza(?:r)?\s+a\s+inclus|(?:Fica|É)\s+restabelecid|Restabelec\w*\s+a\s+vig|(?:É|E|São|Sao|Fica[m]?)\s+(?:acrescid|inclu[íi]d|inserid|alterad|modificad|renumerad|desdobrad|substitu[íi]d)|Ser[áa]\s+desdobrad|Aprova(?:r)?\s+o\s+aditamento|Adita(?:r|-se)?\b|(?:Esta|Essa|Tal|A)\s+altera[çc][ãa]o\b|Alter(?:a|am|ar|a-se|am-se|ou)\b|D[áa](?:-se)?\s+(?:nova\s+reda|ao|à|aos|às|a)\b|Dar\s+nova\s+reda|Acrescent|Acresc|Inclu(?:i\b|ir|a-se|em-se|ído|ída|ídos|ídas)|Insir|Inser|Suprim|Modific|Retific|Substitu|Renumer|Complement|Fica[m]?\s+(?:acrescid|alterad|inclu|inserid|suprimid|modificad|retificad|substitu|renumerad|acrescentad))", re.I)
INICIO_REGULA_RE = re.compile(r"^(?:Regulament(?:a|ar|am|a-se)\b|Fica[m]?\s+regulamentad|Disciplin(?:a|ar|am)\b)", re.I)
ESTA_RES_RE = re.compile(r"^(?:Esta|Essa|A\s+presente)\s+(?:Resolu[çc][ãa]o|norma|Portaria)", re.I)
SUJEITO_DISP_RE = re.compile(r"^(?:O|A|Os|As)\s+(?:disposto|previsto|art|§|par[áa]grafo|inciso|al[íi]nea|caput|Anexo|item|Cap[íi]tulo|T[íi]tulo|Se[çc][ãa]o|reda[çc][ãa]o|ementa|quadro|tabela|estrutura)|^(?:O|A|Os|As)?\s*$", re.I)
PASSA_VIGORAR_RE = re.compile(r"\b(passa(?:m)?\s+a\s+(?:vigorar|ter)|fica(?:m)?\s+(?:acrescid|alterad|com\s+a\s+seguinte)|vigorar[áa]\s+com|(?:é|são|e|sao)\s+(?:acrescid|renumerad|alterad|modificad|inclu[íi]d|suprimid)\w*)", re.I)
SUJ_REVOGADA_RE = re.compile(r"^[\s,]*(?:(?:d[oa]|deste|desse)\s+[\wÀ-ú/]+[\s,]*){0,2}(?:é|são|fica(?:m)?)\s+(?:expressamente\s+|integralmente\s+)?revogad", re.I)
RESGUARDO_RE = re.compile(r"(?i)\b(?:resguard\w*|ressalvad\w*|preservad\w*|garantind\w*|assegurand\w*)\b[^.;]{0,160}$")
REFERENCIAL_RE = re.compile(r"\b(nos\s+termos\s+d[oae]s?|conforme(?:\s+(?:o\s+)?disposto)?|de\s+acordo\s+com|consoante|previst[oa]s?\s+n[oa]s?|dispost[oa]s?\s+n[oa]s?|na\s+forma\s+d[oae]s?|em\s+conformidade\s+com|observad[oa]s?|segundo|com\s+base\s+n[oa]s?|aprovad[oa]s?\s+pel[oa]s?|regulamentad[oa]s?\s+pel[oa]s?|regid[oa]s?\s+pel[oa]s?|homologad[oa]s?\s+pel[oa]s?|institu[íi]d[oa]s?\s+pel[oa]s?|criad[oa]s?\s+pel[oa]s?|de\s+que\s+trata[m]?|a\s+que\s+se\s+refere[m]?)\s*(?:o|a|os|as|art\S*\s*\S+\s*(?:d[oa]s?)?)?\s*$", re.I)
RELATIVA_RE = re.compile(r"\bque\s+(?:se\s+)?(aprov|disp[õo]|trat|estabelec|instit|regulament|cri|fix|homolog|norm|defin|disciplin|versa|cuid|organiz)", re.I)
ART_LINHA = re.compile(r"(?m)^\s*(?:\(\*+\)\s*)?(?:\d{1,2}[.)]\s+(?=Art))?(?:Art(?:igo)?\.?\s*(\d+)\s*[º°o]?(?:-([A-Z])(?![a-zà-ú]))?)")

EMENTA_RE = re.compile(r"(?s)(?i:RESOLU[ÇC][ÃÂA]O\s*(?:N[º°o.]*)?)\s*\(?\s*\d[^\n]{0,80}\n(.{10,900}?)\n\s*(?i:(?:O|A)\s*(?:\(A\)\s*)?(?:(?:Senhora|Senhor|Sra\.?|Sr\.?|Magn[íi]fic[oa])\s+)?(?:CONSELHO|PRESIDENTE|REITOR|REITORA|VICE|C[ÂA]MARA)\b)")

def secoes(t):
    """Retorna (fim_ementa, inicio_dispositivo). Dispositivo começa após 'RESOLVE' (ou equivalente)."""
    m = re.search(r"\bR\s*E\s*S\s*O\s*L\s*V\s*E\s*[:.]?|\bRESOLVEM\b|\bDECIDE\b|\bAPROVA\s*:|\bresolve\s*:", t)
    ini = m.end() if m else 0
    # ementa: entre o título "RESOLUÇÃO Nº ..." (qualquer formato de número/data na linha) e o início do preâmbulo
    e = EMENTA_RE.search(t[:ini] if ini else t[:4000])
    if e and re.search(r"(?im)\bRESOLVE\b|^\s*considerando", e.group(1)):
        e = None
    ementa = (e.start(1), e.end(1)) if e else None
    return ementa, ini

def artigos(t):
    return [(m.start(), m.group(1) + ("º" if int(m.group(1)) < 10 else "") + (("-" + m.group(2)) if m.group(2) else "")) for m in ART_LINHA.finditer(t)]

ANEXO_RE = re.compile(r"(?m)^\s*(?:ANEXO\s*((?:[IVX]+|[ÚU]NICO|\d+)\b)?|Anexo\s+((?:[IVX]+|[ÚU]nico|\d+)\b)(?=\s*(?:[-–—:]|[àa]o?\s+Resolu|d[ao]\s+Resolu|\n|$)))")
def anexos(t, ini):
    return [(m.start(), ("Anexo " + (m.group(1) or m.group(2)).upper().replace("UNICO", "Único").replace("ÚNICO", "Único")) if (m.group(1) or m.group(2)) else "Anexo") for m in ANEXO_RE.finditer(t) if m.start() > ini]
def art_em(arts, pos, ini):
    a = None
    for p, n in arts:
        if p <= pos:
            a = n
        else:
            break
    if a is None or (ini and pos < ini and not any(p <= pos for p, _ in arts)):
        return None
    return a

def org_res(txt):
    s = sem_acento(txt or "").upper().replace(" ", "")
    if "CAMARADEEDUCACAOSUPERIOR" in s: return "CNE-CES"
    if "CAMARADEEDUCACAOBASICA" in s: return "CNE-CEB"
    if "CNE" in s or "CONSELHONACIONALDEEDUCACAO" in s:
        if "CES" in s.replace("CNE", "") or "EDUCACAOSUPERIOR" in s: return "CNE-CES"
        if re.search(r"CP\b|CONSELHOPLENO", s.replace("CNE", "")): return "CNE-CP"
        if "CEB" in s.replace("CNE", "") or "EDUCACAOBASICA" in s: return "CNE-CEB"
        return "CNE"
    if re.search(r"\bCNE\b", sem_acento(txt or "").upper()): return "CNE"
    if "CFE" in s: return "CFE"
    if "CONSEPE" in s or "ENSINO,PESQUISAEEXTENSAO" in s or "ENSINOPESQUISAEEXTENSAO" in s or "CEPE" == s: return "CONSEPE"
    if "CONSUNI" in s or "CONSUN" in s or "UNIVERSITARIO" in s: return "CONSUNI"
    if "CURADOR" in s: return "CURADOR"
    for k in ("CONAES", "CONSAD", "CONTRAN", "CNS", "CONFEA", "CFM", "COFEN", "CAPES", "FNDE", "ANVISA"):
        if k in s: return k
    return None

ORG_POS_RE = re.compile(rf"^\s*(?:,\s*)?(?:[-–—/]\s*|\s*(?:do|da|deste|desse|dest[ae]|dess[ae]|pel[oa]|ambas|ambos|todas|todos|tamb[ée]m|,)\s*)*(?P<org>{ORG_RES}|Conselho(?!\s+(?:de\s+Centro|Departamental|do\s+Centro))|C[âa]mara\s+(?:de\s+Gradua[çc][ãa]o|de\s+P[óo]s))", re.I)

def classifica_org_pos(post):
    post = re.sub(r"^\s*,?\s*de\s+(?:\d{1,2}[./]\d{1,2}[./]\d{2,4}|\d{1,2}\s*(?:º|°|o)?\s+de\s+[A-Za-zçÇ]+\s+de\s+\d{4})\s*", "", post)
    m = ORG_POS_RE.match(post[:90])
    if not m:
        return None, None
    o = m.group("org")
    if re.match(r"(?i)conselho$", o.strip()):
        pref = post[:m.start("org")].lower()
        if "deste" in pref or "desse" in pref or "deste" in post[:40].lower():
            return "SELF", o
        return None, o
    if re.match(r"(?i)c[âa]mara", o):
        return "CONSEPE", o
    return org_res(o), o

LEI_SEM_ANO = re.compile(rf"\b(?P<t>Lei|Decreto)(?:\s+Federal)?\s*(?:{NUMTOK}\s*)?(?P<n>\d{{1,3}}\.\d{{3}}|\d{{3,5}})(?P<s>-?[A-Z](?![a-z]))?(?!\s*/\s*\d)(?!\s*,?\s*de\s+\d)(?![\d.])", re.I)

def _considerando_objeto(frase_antes):
    """O considerando trata a norma citada como objeto de atualização/correção/substituição (não como fundamento)."""
    fa = frase_antes[-220:]
    if re.search(r"(?i)\bsob\s+a\s+vig[êe]ncia\s+d[aoe]s?\s*$|\begress\w*[^;]{0,80}\bd[aoe]s?\s*$", fa):
        return True
    kws = list(re.finditer(r"(?i)\b(?:atualiz\w*|corrig\w*|corre[çc][ãa]o|alterar|altera[çc][ãa]o|revisar|revis[ãa]o|reformul\w*|substituir|substitui[çc][ãa]o|adapta[çc][ãa]o|adaptar)\b", fa))
    if not kws:
        return False
    seg = fa[kws[-1].end():]
    if len(seg) > 130 or re.search(r"(?i)\b(?:aos?\s+termos|nos\s+termos|conforme|segundo|de\s+acordo|em\s+conformidade|frente|com\s+(?:a|o|as|os)\b|à|às|ao|aos)\b", seg):
        return False
    return bool(re.search(r"(?i)(?:\bd[aeo]s?\b|\bn[oa]s?\b|aprovad[oa]s?\s+pel[oa]s?|fixad[oa]s?\s+pel[oa]s?)\s*$", seg))

# ---------------------------------------------------------------------------
def extrai(texto, meu_id, meu_cons, inventario, ano_lei=None):
    """inventario: set de IDs existentes (para resolver resoluções sem órgão)."""
    t = prepara(texto)
    ementa, ini = secoes(t)
    arts = artigos(t)
    out = []
    fecho_meu = datas(texto)[1]
    # ---- artigos próprios da norma x artigos de texto transcrito (nova redação de outra norma)
    ANEX0 = anexos(t, ini)
    lim_corpo = min([p_ for p_, _ in ANEX0] + [len(t)])
    _fc = [m_.start() for m_ in re.finditer(r"(?i)(?:Jo[ãa]o\s+Pessoa|Pessoa)\s*(?:\(PB\))?,?\s*(?:em\s+)?(?:de\s+)?\d{1,2}\s*(?:º|°|o)?\s*(?:de\s+)?[A-Za-zçÇ]+\s+(?:de\s+)?\d{4}", t) if m_.start() > ini]
    if _fc:
        lim_corpo = _fc[0]  # o corpo da norma termina no fecho ("João Pessoa, dd de mês de aaaa"); títulos de anexo citados antes dele não encerram o corpo
    TRIG_RE = re.compile(r"(?i)(?:seguinte|nova)\s+reda[çc][ãa]o\s*:|(?:passa(?:m)?|passar[áa]o?)\s+a\s+vigorar\s+(?:acrescid[oa]s?\s+d[oa]s?\s+seguintes?\s+\w+|com\s+(?:a|as)\s+seguintes?\s+\w+)\s*:"
                         r"|\ba\s+seguir\s*:|\bseguintes?\s+(?:artigos?|dispositivos?|par[áa]grafos?|incisos?|al[íi]neas?|itens?)\s*:|\bcomo\s+segue\s*:|\breda[çc][ãa]o\s+abaixo\s*:")
    def _nums_alterados(cl):
        ns = set()
        for g in re.finditer(r"(?i)\bart(?:igo)?s?\.?\s*((?:\d+\s*[º°o]?(?:-[A-Z])?\s*(?:,|;|\be\b|\ba\b)?\s*)+)", cl):
            ns.update(int(x) for x in re.findall(r"\d+", g.group(1)))
        for g in re.finditer(r"(?i)\bpara\s+(?:os\s+)?art(?:igo)?s?\.?\s*((?:\d+\s*[º°o]?\s*(?:,|\be\b)?\s*)+)", cl):
            ns.update(int(x) for x in re.findall(r"\d+", g.group(1)))
        return ns
    TRIGS = []
    for m_ in TRIG_RE.finditer(t):
        generico = not re.match(r"(?i)(?:seguinte|nova)\s+reda|passa|passar", m_.group(0))
        ls_ = max(t.rfind("\nArt", 0, m_.start()), t.rfind("\nArt", 0, m_.start()), 0)
        clausula_tr = t[ls_:m_.end()]
        if generico and (m_.start() < ini or m_.start() >= lim_corpo or not re.search(r"(?i)alter|acresc|renumer|inclu|suprim|reda[çc]|vigorar|passa", clausula_tr)):
            continue
        TRIGS.append((m_.start(), m_.end(), _nums_alterados(clausula_tr)))
    def _linha_transcrita(p_):
        ls_ = t.rfind("\n", 0, p_) + 1
        return bool(re.match(r"\s*[“\"]", t[ls_:p_ + 1])) or bool(re.match(r"Art(?:igo)?\.?\s*\d+\s*[º°o]?(?:-[A-Z])?\s*[.\-–—]?\s*\.{5,}", t[p_:p_ + 40]))
    cand_ = [(p_, n_, int(re.match(r"\d+", n_).group(0))) for p_, n_ in arts if ini <= p_ < lim_corpo and re.match(r"\d+", n_)]
    OWN, TRANS_ARTS = [], set()
    esperado = 1
    for k_, (p_, n_, num_) in enumerate(cand_):
        ini_atual = OWN[-1][0] if OWN else ini
        trig_atual = [tr for tr in TRIGS if ini_atual <= tr[0] < p_]
        s_atual = set().union(*[tr[2] for tr in trig_atual]) if trig_atual else set()
        if _linha_transcrita(p_) or (trig_atual and num_ in s_atual and num_ != esperado):
            TRANS_ARTS.add(p_); continue
        if trig_atual and num_ in s_atual and num_ == esperado:
            # mesmo número do artigo esperado e do artigo alterado: é próprio só se não houver outro com esse número adiante antes do seguinte
            depois_ = [c for c in cand_[k_ + 1:] if c[2] == esperado and not _linha_transcrita(c[0])]
            if depois_:
                TRANS_ARTS.add(p_); continue
        if num_ == esperado or (num_ == esperado + 1 and not any(c[2] == esperado for c in cand_[k_ + 1:])):
            OWN.append((p_, n_)); esperado = num_ + 1
        elif trig_atual:
            TRANS_ARTS.add(p_)
    if len(OWN) < 1:
        OWN = []
    TRANSCR = []
    for a_, b_, s_ in TRIGS:
        if ini <= a_ < lim_corpo and OWN:
            prox = [p_ for p_, _ in OWN if p_ > b_]
            fim_q = prox[0] if prox else lim_corpo
        else:
            atual = art_em(arts, a_, 0)
            fim_q = None
            if atual and re.match(r"\d+", atual):
                prox_n = int(re.match(r"\d+", atual).group(0)) + 1
                for p_, n_ in arts:
                    if p_ > b_ and re.match(r"\d+", n_) and int(re.match(r"\d+", n_).group(0)) == prox_n and not _linha_transcrita(p_):
                        fim_q = p_; break
            if fim_q is None:
                fq = t.find("”", b_, b_ + 6000)
                fim_q = fq if fq > 0 else b_ + 1500
        TRANSCR.append((b_, fim_q))
    # blocos entre aspas abertos após dois-pontos (ou em sequência de blocos) no corpo da norma
    for m_ in re.finditer("“", t):
        a_ = m_.start()
        if not (ini <= a_ < lim_corpo):
            continue
        antes_q = t[max(0, a_ - 40):a_]
        if not re.search(r"[:”]\s*$", antes_q):
            continue
        fq = t.find("”", a_ + 1, a_ + 8000)
        if fq > 0 and not any(x <= a_ < y for x, y in TRANSCR):
            TRANSCR.append((a_, fq))
    TRANSCR.sort()
    ARTS_DISP = OWN if OWN else arts
    ANEXOS = [a_ for a_ in ANEX0 if not any(s_ <= a_[0] < e_ for s_, e_ in TRANSCR)]
    _ma = re.search(r"-(\d{4})(?:-B)?$", meu_id)
    meu_ano = int(_ma.group(1)) if _ma else None

    # máscara para achar limites de frase: pontos de abreviaturas e de números não encerram frase
    mask = re.sub(r"(?<=\d)\.(?=\d)", "·", t)
    mask = re.sub(r"(?i)\b(arts?|n|nº|n°|res|inc|incs|al|fls?|p[áa]g|prof|profa|dr|dra|sr|sra|ltda|etc|ex|cf|pp?|vol|ed|no|nos|parág|par|cap|tít|sec|item|obs|tel|av|inc|ref|art)\.", lambda m: m.group(0)[:-1] + "·", mask)
    mask = re.sub(r"(?i)((?:\bArt(?:igo)?[.·]?\s*\d+\s*[º°o]?(?:-[A-Z])?)|(?:§\s*\d+\s*[º°o]?)|(?:Par[áa]grafo\s+[úu]nico))\s*\.", lambda m: m.group(1) + "·", mask)

    def ult_pv(pos):
        k = mask.rfind(";", 0, pos)
        while k >= 0 and re.match(r"\s*(?:e\s+)?(?:(?:o|a|os|as)\s+)?(?:\d|(?:art(?:igo)?s?\b|arts?\.|§|caput\b|incisos?\b|al[íi]neas?\b|par[áa]grafos?\b|anexos?\b))", mask[k + 1:k + 40], re.I):
            k = mask.rfind(";", 0, k)
        return k
    def limites(pos_ini, pos_fim):
        cands = [mask.rfind(". ", 0, pos_ini), mask.rfind(".\n", 0, pos_ini), ult_pv(pos_ini), mask.rfind(":\n", 0, pos_ini), mask.rfind("\n\n", 0, pos_ini),
                 mask.rfind("\nArt", 0, pos_ini), mask.rfind("\n§", 0, pos_ini), mask.rfind("\nParágrafo único", 0, pos_ini),
                 mask.rfind(".”", 0, pos_ini) + 1 if mask.rfind(".”", 0, pos_ini) >= 0 else -1, mask.rfind('."', 0, pos_ini) + 1 if mask.rfind('."', 0, pos_ini) >= 0 else -1]
        a0 = max(cands)
        if a0 < pos_ini - 320:
            # cláusula longa: só se estende além de 320 caracteres se o trecho for uma lista de dispositivos ("Os artigos 2º; 3º, Parágrafo único; 4º, caput; ...")
            seg_ = mask[max(a0, pos_ini - 1200):pos_ini - 60]
            toks_ = re.findall(r"\S+", seg_)
            listy_ = sum(1 for w in toks_ if re.fullmatch(r"(?i)[\d$&§]+\S*|[IVXLC]+[,;]?|e|ou|caput[,;]?|par[áa]grafos?|[úu]nico[,;]?|incisos?|al[íi]neas?\S*|[a-e][,;]?|arts?[.·]?|artigos?|anexos?|d[oa]s?|§+|\S*\d\S*", w)) / max(1, len(toks_))
            if not (a0 >= pos_ini - 1200 and listy_ >= 0.6):
                a0 = pos_ini - 320
        fins = [x for x in (mask.find(". ", pos_fim), mask.find(".\n", pos_fim), mask.find(";", pos_fim), mask.find("\n\n", pos_fim)) if x != -1]
        a1 = min(fins + [pos_fim + 260])
        return a0, a1

    def add(tipo_norma, alvo, n_cit, pos_ini, pos_fim, conf, nota=""):
        a0, a1 = limites(pos_ini, pos_fim)
        trecho = re.sub(r"\s+", " ", t[a0 + 1:a1 + 1]).strip()[:420]
        if pos_ini - a0 > 330:
            trecho = (re.sub(r"\s+", " ", t[a0 + 1:a0 + 120]).strip() + " (…) " + re.sub(r"\s+", " ", t[pos_ini - 160:a1 + 1]).strip())[:460]
        antes_l = INICIO_CLAUSULA_RE.sub("", re.sub(r"\s+", " ", t[a0 + 1:pos_ini]), count=1)[-240:]
        dm = DISP_FIM_RE.search(antes_l)
        disp_dest = re.sub(r"\s+", " ", dm.group(1)).strip(" ,") if dm else "norma inteira"
        antes_sem_disp = (antes_l[:dm.start()] if dm else antes_l).rstrip()
        # particípio absoluto de revogação imediatamente antes da citação (ou continuação de lista revogada)
        part_revoga = bool(PARTICIPIO_REVOGA_RE.search(antes_sem_disp[-120:] + " ")) and not PASSIVO_RE.search(antes_sem_disp[-70:] + " ")
        if not part_revoga:
            prev_rv = [q for q in out if q["origem"] == meu_id and q.get("_part_revoga") and q["fim"] <= pos_ini and pos_ini - q["fim"] < 160]
            if prev_rv:
                entre_l = re.sub(r"\s+", " ", t[prev_rv[-1]["fim"]:pos_ini])
                dm2 = DISP_FIM_RE.search(entre_l)
                entre_sd = entre_l[:dm2.start()] if dm2 else entre_l
                if CONECTOR_LISTA_RE.fullmatch(entre_sd) or re.fullmatch(r"\s*(?:,|;)?\s*(?:e|bem\s+como)?\s*(?:a|o|as|os)?\s*(?:d[oa]s?|n[oa]s?)?\s*", entre_sd, re.I):
                    part_revoga = True
        if ementa and ementa[0] - 5 <= pos_ini <= ementa[1] + 5:
            parte = "ementa"
        elif ini and pos_ini < ini:
            parte = "preâmbulo"
        else:
            parte = "dispositivo"
        art = art_em(ARTS_DISP if pos_ini < lim_corpo else arts, pos_ini, ini) if parte == "dispositivo" else None
        disp_orig = (("art. " + art) if art else ("ementa" if parte == "ementa" else "preâmbulo" if parte == "preâmbulo" else "norma inteira"))
        if parte == "dispositivo":
            anx = [a_ for a_ in ANEXOS if a_[0] <= pos_ini]
            if anx:
                p_anx, nome_anx = anx[-1]
                arts_anx = [a_ for a_ in arts if p_anx < a_[0] <= pos_ini]
                disp_orig = nome_anx + (f", art. {arts_anx[-1][1]}" if arts_anx else "")
        frase_antes = re.sub(r"\s+", " ", t[a0 + 1:pos_ini])
        depois = re.sub(r"\s+", " ", t[pos_fim:a1 + 1])
        clausula = INICIO_CLAUSULA_RE.sub("", frase_antes.lstrip(" ,;:.-–—)”\"'"), count=1).lstrip(" ,;:.-–—)”\"'")
        # citação descritiva: precedida de "nos termos de", "conforme", "aprovada pela"... ou ligada a citação anterior por "que"
        descritiva = bool(REFERENCIAL_RE.search(frase_antes[-60:]))
        anteriores = [q for q in out if q["origem"] == meu_id and a0 < q["pos"] < pos_ini and pos_ini - q["fim"] < 200]
        obj_relativa = False
        if anteriores:
            entre = re.sub(r"\s+", " ", t[anteriores[-1]["fim"]:pos_ini])
            if RELATIVA_RE.search(entre) or re.search(r"\bque\s+(?:\w+\s+){0,2}(?:alter|revog|regulament|d[áa]\s+nova|acrescent|inclu|suprim|modific)", entre, re.I):
                descritiva = True
            if re.fullmatch(r"\s*,?\s*(?:\([^()]{0,60}\)\s*,?\s*)?(?:(?:d[oa]|dest[ea]|dess[ea])\s+[\wÀ-ú]+(?:\s+[\wÀ-ú/]+){0,4}\s*,?\s*)?que\s+(?:\w+\s+){0,2}(?:alter|revog|regulament|d[áa]\s+nova|acrescent|inclu|suprim|modific|substitu)\w*\s+(?:(?:parcialmente|integralmente|expressamente)\s+)?(?:a|o|as|os)?\s*(?:(?:art|§|inc|par[áa]g|al[íi]n|anexo|caput)[^,;]{0,60}?\s+d[aoe]s?\s*)?", entre, re.I):
                obj_relativa = True
        superior = alvo.startswith(("BR-", "PB-")) and meu_id.startswith("UFPB-")
        _li = t.rfind("\n", 0, pos_ini) + 1
        linha = t[_li:pos_ini]
        titulo_anexo = re.match(r"[\s\x0c]*(?:ANEXO|Anexo)\b.{0,60}(?:à|a|À|A|da|do|DA|DO)\s+$", linha) and (
            re.match(r"[\s\x0c]*ANEXO\b", linha) or "\x0c" in linha[:2] or _li == 0 or t[max(0, _li - 2):_li] == "\n\n" or t[max(0, _li - 2):_li - 1] in (".", ":", ";", "”"))
        if titulo_anexo and parte != "preâmbulo":
            return  # título do anexo da própria resolução (autorreferência; número pode estar errado)
        transcr_reg = next(((a_, b_) for a_, b_ in TRANSCR if a_ <= pos_ini < b_), None) if parte == "dispositivo" else None
        transcrito = transcr_reg is not None
        disp_transcrito = ""
        if transcrito:
            arts_t = [(p_, n_) for p_, n_ in arts if transcr_reg[0] <= p_ <= pos_ini]
            disp_transcrito = ("art. " + arts_t[-1][1]) if arts_t else ""
            art_c = art_em(ARTS_DISP if transcr_reg[0] < lim_corpo else arts, transcr_reg[0], ini)
            if art_c:
                disp_orig = "art. " + art_c
        # ementa de outra norma numa lista de legislação ou bibliografia ("Resolução nº X, de ... . Altera a Resolução nº Y")
        ref_lista = None
        if parte != "ementa" and re.match(r"[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-zá-úç]+\b", clausula):
            antes_q = [q for q in out if q["origem"] == meu_id and q.get("fim") is not None and q["fim"] <= a0 + 1 and a0 + 1 - q["fim"] <= 90]
            if antes_q:
                q_ = max(antes_q, key=lambda q: q["fim"])
                cauda = re.sub(r"\s+", " ", t[q_["fim"]:a0 + 1])
                if re.fullmatch(r"\s*(?:,?\s*(?:de\s+)?\d{1,2}\s*(?:º|°|o)?\s+de\s+[A-Za-zçÇ]+\s+de\s+\d{4}|,?\s*de\s+\d{1,2}[./]\d{1,2}[./]\d{2,4}|,?\s*de\s+\d{4})?\s*(?:\([^()\n]{0,40}\)\s*)?(?:[-–—,]\s*[^.\n]{0,60})?\s*[.]?\s*", cauda):
                    s0 = limites(q_["pos"], q_["fim"])[0]
                    pref = re.sub(r"\s+", " ", t[s0 + 1:q_["pos"]])
                    if len(pref) < 160 and re.fullmatch(r"\s*(?:[-–—•·*▪]\s*|\(?\d{1,3}[.)]\s*|\(?[IVXLC]+\s*[-–—.)]\s*|[a-z]\)\s*)?(?:BRASIL\b[^\n]{0,140}?)?\s*", pref):
                        ref_lista = q_
        bibliog = parte == "dispositivo" and bool(re.search(r"(?i)Dispon[íi]vel\s+(?:em|no|na)|Acesso\s+em\s*:?\s*\d", re.split(r"\n\s*Art(?:igo)?\.?\s*\d", t[t.rfind("\n", 0, pos_ini) + 1:a1 + 250])[0]))
        if descritiva and parte == "dispositivo":
            outras0 = [q for q in out if q["origem"] == meu_id and a0 < q["pos"] < pos_ini and q["destino"] != alvo]
            if not outras0 and (re.match(r"(?i)^(?:Alter\w*|Revog\w*(?:-se)?|Modific\w*|Suprim\w*|Exclu\w*|D[áa]r?\s+nova\s+reda\w*\s+a)\s+(?:o|a|os|as)\s+(?:disposto|previsto|estabelecido)s?\s+n", clausula)
                               or (SUJEITO_DISP_RE.match(clausula) and PASSA_VIGORAR_RE.search(depois))):
                descritiva = False
        # "Altera o Regulamento ..., aprovado pela Resolução X": alterar o regulamento/estrutura/anexo aprovado por X é alterar X
        # verbo finito dentro de oração relativa de citação anterior ("Resolução X, que estabelece ... e revoga a Resolução Y"): descreve X
        _prev_cits = [q for q in out if q["origem"] == meu_id and q.get("fim") is not None and a0 < q["pos"] < pos_ini and q["parte"] in ("ementa", "dispositivo")]
        if _prev_cits and parte in ("ementa", "dispositivo"):
            seg_rel = t[_prev_cits[0]["fim"]:pos_ini]
            vm_ = list(re.finditer(r"(?i)(?<![,;]\s)(?<![,;])\b(?:e\s+)?(revoga|revogou|altera|alterou|modifica|modificou|d[áa]\s+nova\s+reda[çc][ãa]o|deu\s+nova\s+reda[çc][ãa]o|regulamenta|acrescenta|suprime)\b(?!-se)", seg_rel))
            if vm_ and re.search(r"(?i)\bque\b", seg_rel[:vm_[-1].start()]) and not re.search(r"(?i)Resolu[çc]|\bLei\b|Decreto|Portaria", seg_rel[vm_[-1].end():]) \
                    and not re.search(r"[,;]\s*(?:e\s+)?$", seg_rel[:vm_[-1].start()]):
                descritiva = True
                nota = (nota + "; " if nota else "") + "verbo dentro de oração relativa que descreve outra norma citada"
        objeto_aprov = False
        rel_forcado = None
        _vcs = list(re.finditer(r"(?i)(?:^|,|;|\be\b|\bbem\s+como\b)\s*(revogar|revoga-se|revogam-se|alterar|altera-se|alteram-se|dar\s+nova\s+reda[çc][ãa]o|d[áa]-se\s+nova\s+reda[çc][ãa]o|acrescentar|suprimir|modificar|excluir|inserir|incluir)\b", clausula)) if parte == "dispositivo" else []
        _vc = _vcs[-1] if _vcs else None
        _ev = clausula[_vc.end():] if _vc else ""
        _cit_entre = bool(re.search(r"(?i)Resolu[çc]|\bLei\b|Decreto|Portaria", _ev))
        _cit_antes = bool(_vc) and bool(re.search(r"(?i)Resolu[çc]|\bLei\b|Decreto|Portaria", clausula[:_vc.start()]))
        if _vc and not _cit_entre and len(_ev) < 420:
            _tp_vc = "REVOGA" if re.match(r"(?i)revog|exclu", _vc.group(1)) else "ALTERA"
            if _cit_antes or _vc.start() > 0:
                rel_forcado = _tp_vc
        if descritiva and OBJ_REF_RE.search(frase_antes[-80:]) and OBJETO_RE.search(clausula):
            outras = [q for q in out if q["origem"] == meu_id and a0 < q["pos"] < pos_ini and q["destino"] != alvo]
            if outras and rel_forcado and OBJETO_RE.search(_ev):
                objeto_aprov = True
            elif not outras:
                if parte == "ementa":
                    objeto_aprov = bool(VERBO_ALTERA.search(frase_antes) or VERBO_REVOGA.search(frase_antes))
                elif parte == "dispositivo":
                    objeto_aprov = bool(INICIO_ALTERA_RE.match(clausula) or INICIO_REVOGA_RE.match(clausula) or
                                        (ESTA_RES_RE.match(clausula) and (VERBO_ALTERA.search(clausula) or VERBO_REVOGA.search(clausula))))
            if objeto_aprov:
                descritiva = False
                if disp_dest == "norma inteira":
                    om_ = OBJETO_RE.search(clausula)
                    dmo_ = DISP_FIM_RE.search(clausula[:om_.start()])
                    disp_dest = om_.group(0) + " (aprovado pela norma)" + ((": " + re.sub(r"\s+", " ", dmo_.group(1)).strip(" ,")) if dmo_ else "")
                nota = (nota + "; " if nota else "") + "alteração/revogação do regulamento, estrutura ou anexo aprovado pela norma citada"
        if (PASSIVO_RE.search(frase_antes[-70:]) or PASSIVO_RE.search(antes_sem_disp[-70:] + " ")) and not transcrito:
            rel = "CITA RELAÇÃO"
        elif parte == "preâmbulo":
            rel = "FUNDAMENTA-SE EM" if PREAMBULO_FUND.search(t[max(0, pos_ini - 400):pos_ini]) else "REMETE A"
            if rel == "FUNDAMENTA-SE EM" and obj_relativa:
                rel, nota = "REMETE A", (nota + "; " if nota else "") + "norma mencionada como objeto do ato de outra norma citada no preâmbulo (descrição, não fundamento)"
                q_ = anteriores[-1]
                vrel = re.search(r"(?i)\bque\s+(?:\w+\s+){0,2}(revog|alter|d[áa]\s+nova|acrescent|inclu|suprim|modific|substitu|regulament)", entre)
                if vrel and q_["destino"] != alvo:
                    tp_i = "REVOGA (total)" if vrel.group(1).lower().startswith("revog") else "REGULAMENTA" if vrel.group(1).lower().startswith("regulament") else "ALTERA"
                    out.append(dict(origem=q_["destino"], disp_origem="norma inteira", destino=alvo, disp_destino=disp_dest, tipo=tp_i, tipo_transcrito="",
                                    parte="citação indireta", tipo_norma=tipo_norma, citacao=re.sub(r"\s+", " ", n_cit)[:120], trecho=trecho,
                                    confianca="média", nota=f"relação mencionada no preâmbulo de {meu_id} (relação indireta, a confirmar na norma de origem)", pos=pos_ini))
            elif rel == "FUNDAMENTA-SE EM" and _considerando_objeto(frase_antes):
                rel, nota = "REMETE A", (nota + "; " if nota else "") + "considerando que descreve a norma a atualizar ou substituir (não é fundamento)"
        elif descritiva:
            rel = "REMETE A"
        else:
            rel = "REMETE A"
            if parte == "ementa":
                verbos = [(m.start(), "REVOGA") for m in VERBO_REVOGA.finditer(frase_antes)] + \
                         [(m.start(), "ALTERA") for m in VERBO_ALTERA.finditer(frase_antes)] + \
                         [(m.start(), "REGULAMENTA") for m in VERBO_REGULA.finditer(frase_antes)] + \
                         [(m.start(), "NEUTRO") for m in VERBO_NEUTRO.finditer(frase_antes)]
                verbos = [v for v in verbos if not re.search(r"\bque\s+(?:\w+\s+){0,2}$", frase_antes[:v[0]])
                          or re.search(r"(?i)\bque\s+(?:especifica|menciona|indica|discrimina|define|estabelece|disciplina)\s+e\s+$", frase_antes[:v[0]])]
                if verbos and not GENERICA_RE.search(frase_antes):
                    vs = sorted(verbos)
                    ult = vs[-1][1]
                    PRI = {"REVOGA": 3, "ALTERA": 2, "REGULAMENTA": 1, "NEUTRO": 0}
                    k2 = len(vs) - 1
                    while k2 > 0 and re.fullmatch(r"\W*(?:\w+\W+)?e\s+", frase_antes[vs[k2 - 1][0]:vs[k2][0]].split(None, 1)[-1] if " " in frase_antes[vs[k2 - 1][0]:vs[k2][0]] else ""):
                        if PRI[vs[k2 - 1][1]] > PRI[ult]:
                            ult = vs[k2 - 1][1]
                        k2 -= 1
                    rel = ult if ult != "NEUTRO" else "REMETE A"
                if part_revoga:
                    rel = "REVOGA"
            else:
                dep_cl = re.split(r"\n\s*(?:Art(?:igo)?\.?\s*\d|§|Par[áa]grafo)", t[pos_fim:a1 + 1])[0]
                dep_cl = re.sub(r"\s+", " ", dep_cl)
                esta_rev = ESTA_RES_RE.match(clausula) and VERBO_REVOGA.search(clausula + " " + dep_cl[:80]) and not GENERICA_RE.search(clausula + " " + dep_cl[:80]) and not RESGUARDO_RE.search(frase_antes)
                if objeto_aprov and rel_forcado:
                    rel = rel_forcado
                elif INICIO_REVOGA_RE.match(clausula) or part_revoga or esta_rev or (SUJEITO_DISP_RE.match(clausula) and SUJ_REVOGADA_RE.match(dep_cl)):
                    rel = "REVOGA"
                elif INICIO_ALTERA_RE.match(clausula) or (SUJEITO_DISP_RE.match(clausula) and PASSA_VIGORAR_RE.search(depois)) or \
                        (ESTA_RES_RE.match(clausula) and VERBO_ALTERA.search(clausula) and not GENERICA_RE.search(clausula)):
                    rel = "ALTERA"
                elif INICIO_REGULA_RE.match(clausula) or (ESTA_RES_RE.match(clausula) and VERBO_REGULA.search(clausula)):
                    rel = "REGULAMENTA"
                if rel_forcado and not descritiva and parte == "dispositivo" and (rel == "REMETE A" or (_cit_antes and rel != rel_forcado)):
                    rel = rel_forcado
                    nota = (nota + "; " if nota else "") + "verbo de ato coordenado na mesma cláusula"
                    if rel == "ALTERA" and disp_dest == "norma inteira" and OBJETO_RE.search(_ev):
                        om2 = OBJETO_RE.search(_ev); dmo2 = DISP_FIM_RE.search(_ev[:om2.start()])
                        disp_dest = om2.group(0) + " (aprovado pela norma)" + ((": " + re.sub(r"\s+", " ", dmo2.group(1)).strip(" ,")) if dmo2 else "")
            if rel == "REGULAMENTA" and superior and parte != "ementa" and not re.search(r"no\s+[âa]mbito\s+d[ae]|nesta\s+Universidade|da\s+UFPB", frase_antes + " " + depois[:100], re.I):
                rel, nota = "REMETE A", (nota + "; " if nota else "") + "ementa de norma federal transcrita no texto (não é ato desta norma)"
            if rel in ("REVOGA", "ALTERA") and superior:
                rel, nota = "REMETE A", (nota + "; " if nota else "") + "verbo de alteração/revogação referido a norma superior (descrição, não ato desta norma)"
            if rel == "ALTERA" and re.search(r"\bsubstitu", frase_antes, re.I) and disp_dest == "norma inteira":
                rel, nota = "REVOGA", (nota + "; " if nota else "") + "substituição integral"
            if rel == "REVOGA" and disp_dest == "norma inteira" and re.search(r"(?i)(?:os|as)\s+(?:artigos|dispositivos|incisos|par[áa]grafos|itens|anexos)\s+d[aoe]s?\s*$", antes_sem_disp):
                disp_dest = "dispositivos indicados no trecho"
            if rel == "REVOGA" and disp_dest == "norma inteira":
                alvo_txt = clausula if parte == "dispositivo" else frase_antes[max([m_.end() for m_ in VERBO_REVOGA.finditer(frase_antes)] or [0]):]
                if re.search(r"(?i)^(?:(?:Fica[m]?|(?:É|São))\s+revogad[oa]s?|Revog\w*(?:-se)?|Exclu\w*(?:-se)?|Suprim\w*)?\s*,?\s*(?:o|a|os|as)?\s*(?:art(?:igo)?s?\b|art\.|§|par[áa]grafos?|incisos?|al[íi]neas?|itens?|caput|cap[íi]tulos?|se[çc](?:[ãa]o|[õo]es)|t[íi]tulos?)", alvo_txt.strip()):
                    disp_dest = "dispositivos indicados no trecho"
            if rel == "REVOGA":
                rel = "REVOGA (parcial)" if disp_dest != "norma inteira" else "REVOGA (total)"
                if re.search(r"(?i)garantind|resguardad|ressalvad|assegurad[oa]s?\s+(?:aos|os|as)|alunos\s+(?:que\s+)?(?:ingressa|matriculad)|ingressantes\s+(?:at[ée]|antes)", trecho):
                    nota = (nota + "; " if nota else "") + "com ressalva (ultratividade) para situações constituídas sob a norma revogada"
            if rel == "ALTERA" and re.search(r"(?i)restabelec\w*\s+(?:a\s+)?vig[êe]ncia|repristin", frase_antes + " " + depois[:60]):
                nota = (nota + "; " if nota else "") + "REPRISTINAÇÃO: restabelece a vigência da norma"
        if (ref_lista is not None or bibliog) and rel in ("ALTERA", "REGULAMENTA") or (ref_lista is not None or bibliog) and rel.startswith("REVOGA"):
            if ref_lista is not None and alvo != ref_lista["destino"]:
                out.append(dict(origem=ref_lista["destino"], disp_origem="norma inteira", destino=alvo, disp_destino=disp_dest,
                                tipo=rel, tipo_transcrito="", parte="citação indireta", tipo_norma=tipo_norma, citacao=re.sub(r"\s+", " ", n_cit)[:120],
                                trecho=trecho, confianca="média", nota=f"ementa da norma citada em lista de legislação/bibliografia de {meu_id}", pos=pos_ini))
            rel, nota = "REMETE A", (nota + "; " if nota else "") + ("ementa de outra norma em lista de legislação/bibliografia (não é ato desta norma)" if ref_lista is not None else "referência bibliográfica (não é ato desta norma)")
        tipo_transcrito = ""
        if transcrito and rel != "REMETE A" and rel != "CITA RELAÇÃO":
            tipo_transcrito, rel = rel, "REMETE A"
            nota = (nota + "; " if nota else "") + f"ato ({tipo_transcrito}) contido em nova redação transcrita; a base decide se é reafirmação ou ato novo"
        elif transcrito and rel == "CITA RELAÇÃO":
            rel = "REMETE A"
        out.append(dict(origem=meu_id, disp_origem=disp_orig, destino=alvo, disp_destino=disp_dest, tipo=rel, tipo_transcrito=tipo_transcrito,
                        disp_transcrito=disp_transcrito, transcr_de="", _transcr_ini=transcr_reg[0] if transcrito else None,
                        parte=parte, tipo_norma=tipo_norma, citacao=re.sub(r"\s+", " ", n_cit)[:120],
                        trecho=trecho, confianca=conf, nota=nota, pos=pos_ini, fim=pos_fim, frase=(a0, a1),
                        _part_revoga=part_revoga and rel.startswith("REVOGA")))

    # --- citações numeradas -------------------------------------------------
    spans_cit = []
    # órgão explícito de cada (número, ano) em qualquer ponto do documento
    org_explicita = {}
    for m0 in CIT_RE.finditer(t):
        if not m0.group("RES"):
            continue
        o0 = org_res((m0.group("preorg") or "").strip()) or classifica_org_pos(t[m0.end():m0.end() + 120])[0]
        if o0 in ("CONSEPE", "CONSUNI", "CURADOR"):
            for num0, b0, c0, d0 in re.findall(rf"({NUMERO})\s*(?:/\s*(\d{{2,4}})(?!\d)|,?\s*(?:de\s+\d{{1,2}}\s*(?:º|°|o)?\s+de\s+[A-Za-zçÇ]+\s+de\s+(\d{{4}}))|,\s*de\s+(\d{{4}})(?!\d))", m0.group("lista")):
                n0, s0 = numint(num0)
                if n0 is not None:
                    org_explicita.setdefault((n0, s0, ano4(b0 or c0 or d0)), set()).add(o0)
    ult_org = (None, -999)
    for m in CIT_RE.finditer(t):
        tipo = next(k for k, _ in TIPOS if m.group(k))
        ult_org_cand = None
        preorg = (m.group("preorg") or "").strip()
        lista = m.group("lista")
        post = t[m.end():m.end() + 120]
        itens = [(a, b, c or d) for a, b, c, d in re.findall(rf"({NUMERO})\s*(?:/\s*(\d{{2,4}})(?!\d)|,?\s*(?:de\s+\d{{1,2}}\s*(?:º|°|o)?\s+de\s+[A-Za-zçÇ]+\s+de\s+(\d{{4}}))|,\s*de\s+(\d{{4}})(?!\d))", lista)]
        pos_org, _ = classifica_org_pos(post) if tipo == "RES" else (None, None)
        for k_item, (num_s, a1, a2) in enumerate(itens):
            n, suf = numint(num_s)
            if n is None:
                continue
            ano = ano4(a1 or a2)
            if ano < 1900 or ano > 2030:
                continue
            alvo, conf, nota = None, "alta", ""
            if tipo == "RES":
                o = org_res(preorg) if preorg else None
                sigla = preorg.replace(" ", "") if preorg and re.fullmatch(r"[A-Z]{2,8}(?:/[A-Z]{2,8})?(?:-[A-Z]{2,4})?", preorg.replace(" ", "")) else ""
                if not o and sigla and sigla not in ("UFPB", "CEPE", "CONSEP", "CONSUN", "NO", "NS", "NA", "N", "NOS", "NR"):
                    o = "SIGLA:" + sigla
                    if sigla in ("COSEPE", "CONSEPPE"):
                        o, nota = "CONSEPE", "sigla grafada como " + sigla + " no texto"
                if o and pos_org and pos_org != "SELF" and pos_org != o and k_item == len(itens) - 1 and len(itens) > 1:
                    o = pos_org
                if not o:
                    o2, _ = classifica_org_pos(post)
                    o = meu_cons if o2 == "SELF" else o2
                    if o2 == "SELF":
                        nota = "deste Conselho"
                if not o:
                    # cadeia "X do CONSEPE, alterada pela Resolução nº Y": Y herda o órgão de X
                    gap = re.sub(r"\s+", " ", t[ult_org[1]:m.start()]) if 0 <= m.start() - ult_org[1] <= 70 else None
                    if ult_org[0] and gap is not None and re.search(r"(?i)(alterad|modificad|revogad|complementad|e\s+suas\s+altera|com\s+as\s+altera|bem\s+como|,|\be\b)", gap):
                        o, conf, nota = ult_org[0], "média", "órgão herdado da citação anterior na mesma enumeração/cadeia"
                    elif len(org_explicita.get((n, suf, ano), set())) == 1:
                        o, conf, nota = next(iter(org_explicita[(n, suf, ano)])), "média", "órgão indicado em outra menção do mesmo número no texto"
                if o in ("CONSEPE", "CONSUNI", "CURADOR"):
                    ult_org_cand = o
                if o and o.startswith("SIGLA:"):
                    sg = o[6:].replace("/", "-")
                    sg = {"CES": "CNE-CES", "CEB": "CNE-CEB", "CD-ANPD": "ANPD", "RDC": "ANVISA-RDC", "CFE": "CFE"}.get(sg, sg)
                    externas = ("CFO", "CFN", "CFF", "CFC", "CFM", "COFEN", "CONFEA", "CONFE", "CFP", "CFESS", "CFMV", "CONTRAN", "CNS", "ANVISA", "CONAMA",
                                "CONANDA", "CNJ", "CNMP", "ANS", "ANATEL", "ANEEL", "CFBIO", "CREFITO", "COFFITO", "CFFA", "CONFEF", "CONRERP", "CFQ", "CODEFAT", "CONAES", "CONSAD", "CAPES", "FNDE", "INEP", "ANP", "CONARQ", "CEE", "MEC")
                    externas = externas + ("CNE", "ANPD", "CFBM", "CONTER", "CNRMS", "CFBIO")
                    UNID_UFPB = re.compile(r"^(?:CC[A-Z]*|CT|CTDR|CE|CI|CEAR|CBIOTEC|CAVN|CP-CAVN|CCD|CCG[A-Z]*|CSEB|PRPG|PRG|PROEX|PRAC|PROPESQ|PROGEP|CPT|ETS|UFPB-[A-Z]+|[A-Z]+-UFPB)(?:-[A-Z]+)*$")
                    if sg.split("-")[0] in externas:
                        alvo, conf, nota = f"BR-{sg}-RES-{n}{suf}-{ano}", "média", "órgão externo identificado pela sigla"
                    elif UNID_UFPB.match(sg):
                        alvo, conf, nota = f"UFPB-{sg.replace('UFPB-', '').replace('-UFPB', '')}-RES-{n}{suf}-{ano}", "média", "resolução de unidade/colegiado da UFPB (N9) identificada pela sigla"
                    else:
                        alvo, conf, nota = f"OUTRO-{sg}-RES-{n}{suf}-{ano}", "baixa", "órgão identificado apenas pela sigla (não reconhecido)"
                elif o in ("CONSEPE", "CONSUNI", "CURADOR"):
                    alvo = id_ufpb(o, n, suf, ano)
                elif o:
                    alvo = f"BR-{o}-RES-{n}{suf}-{ano}"
                elif re.search(r"(?i)Dispon[íi]vel\s+em|Acesso\s+em|\(BRASIL|BRASIL\.|Diretrizes\s+Curriculares\s+Nacionais|\bDCNs?\b|Conselho\s+Nacional\s+de\s+Educa|ANVISA|RDC", t[max(0, m.start() - 150):m.end() + 150]):
                    alvo, conf, nota = f"BR-?-RES-{n}{suf}-{ano}", "baixa", "referência externa (bibliografia/DCN) sem órgão identificado"
                else:
                    # sem órgão: resolve pela existência no inventário
                    cands = [c for c in ("CONSEPE", "CONSUNI", "CURADOR") if id_ufpb(c, n, suf, ano) in inventario]
                    if meu_cons in cands:
                        alvo, conf, nota = id_ufpb(meu_cons, n, suf, ano), "média", "órgão não indicado; atribuído ao mesmo conselho"
                    elif len(cands) == 1:
                        alvo, conf, nota = id_ufpb(cands[0], n, suf, ano), "baixa", "órgão não indicado; único conselho com esse número no SIGRH (o acervo tem lacunas)"
                    elif meu_cons:
                        alvo, conf, nota = id_ufpb(meu_cons, n, suf, ano), "baixa", "órgão não indicado e número não encontrado no inventário"
                    else:
                        alvo, conf, nota = f"UFPB-?-RES-{str(n).zfill(2)}-{ano}", "baixa", "órgão não identificado"
            elif tipo in ("LEI", "LC", "DL", "DEC", "MP", "EC"):
                esc = sem_acento(m.group(tipo)).lower()
                if "estadual" in esc:
                    alvo, nota = f"PB-{tipo}-{n}{suf}-{ano}", "norma estadual (verificar UF)"
                else:
                    alvo = f"BR-{tipo}-{n}{suf}-{ano}"
            elif tipo == "PORT":
                o = (preorg or "") + " " + post[:60]
                so = sem_acento(o).upper()
                tp = sem_acento(m.group(tipo)).lower()
                norm = "PORTNORM" if "normativa" in tp else "PORTINTER" if "interministerial" in tp else "PORT"
                if re.search(r"\bMEC\b|MINISTERIAL|MINISTRO\s+DE\s+ESTADO\s+DA\s+EDUCA|MINISTERIO\s+DA\s+EDUCA", so) or "ministerial" in tp:
                    alvo = f"BR-MEC-{norm}-{n}{suf}-{ano}"
                elif re.search(r"\b(CAPES|CNPQ|INEP|SESU|SETEC|SERES|MPOG|SEGES|SGP|ME|MS|MCTI|MCT|FNDE|CGU|TCU|AGU|SEDGG|SLTI)\b", so):
                    og = re.search(r"\b(CAPES|CNPQ|INEP|SESU|SETEC|SERES|MPOG|SEGES|SGP|ME|MS|MCTI|MCT|FNDE|CGU|TCU|AGU|SEDGG|SLTI)\b", so).group(1)
                    alvo = f"BR-{og}-PORT-{n}{suf}-{ano}"
                elif re.search(r"\b(GR|R/GR|REITOR|REITORIA|UFPB|PRG|PRPG|PROPESQ|PROEX|PRAC|PROGEP|SRH|PRA|PROPLAN|PRAPE|SODS|PROAD)\b", so):
                    og = re.search(r"\b(PRG|PRPG|PROPESQ|PROEX|PRAC|PROGEP|SRH|PRA|PROPLAN|PRAPE|SODS|PROAD)\b", so)
                    alvo = f"UFPB-{og.group(1) if og else 'GR'}-PORT-{str(n).zfill(2)}-{ano}"
                else:
                    pre = sem_acento(t[max(0, m.start() - 110):m.start()]).upper()
                    og = re.findall(r"\b(MEC|CAPES|CNPQ|INEP|SESU|SETEC|SERES|MPOG|SEGES|SGP|MCTI|MCT|FNDE|CGU|TCU|AGU|SEDGG|SLTI|MINISTERIO\s+DA\s+EDUCACAO|REITOR|REITORIA|PRG|PRPG|PROGEP)\b", pre)
                    if og:
                        o_ = og[-1].replace("MINISTERIO DA EDUCACAO", "MEC")
                        alvo, conf, nota = (f"UFPB-{'GR' if o_ in ('REITOR','REITORIA') else o_}-PORT-{str(n).zfill(2)}-{ano}" if o_ in ("REITOR", "REITORIA", "PRG", "PRPG", "PROGEP") else f"BR-{o_}-PORT-{n}{suf}-{ano}"), "média", "órgão da portaria inferido do contexto anterior"
                    else:
                        alvo, conf, nota = f"BR-?-PORT-{n}{suf}-{ano}", "baixa", "órgão emissor da portaria não identificado"
            elif tipo == "PAR":
                o = sem_acento((preorg or "") + " " + post[:40]).upper()
                if "CNE/CES" in o.replace(" ", "") or "CNECES" in o.replace(" ", ""):
                    alvo = f"BR-CNE-CES-PAR-{n}{suf}-{ano}"
                elif "CNE/CP" in o.replace(" ", ""):
                    alvo = f"BR-CNE-CP-PAR-{n}{suf}-{ano}"
                elif "CNE" in o:
                    alvo = f"BR-CNE-PAR-{n}{suf}-{ano}"
                elif "CFE" in o:
                    alvo = f"BR-CFE-PAR-{n}{suf}-{ano}"
                elif re.search(r"PROCURADORIA|PF/UFPB|AGU|PGF|CONJUR", o):
                    alvo, nota = f"BR-AGU-PAR-{n}{suf}-{ano}", "parecer jurídico (não normativo, salvo vinculante)"
                else:
                    alvo, conf, nota = f"?-PAR-{n}{suf}-{ano}", "baixa", "órgão do parecer não identificado"
            elif tipo in ("IN", "ON"):
                o = sem_acento((preorg or "") + " " + post[:60]).upper()
                og = re.search(r"\b(SGP|SEGES|SEDGG|MPOG|MP|ME|MEC|CGU|TCU|SLTI|SRH|SEGEP|AGU|RFB|INSS|CAPES|PROGEP|PRG|PRPG)\b", o)
                alvo = f"BR-{tipo}-{og.group(1) if og else '?'}-{n}{suf}-{ano}"
                if not og:
                    conf, nota = "baixa", "órgão da instrução/orientação não identificado"
            if alvo and alvo != meu_id and alvo != re.sub(r'-B$', '', meu_id):
                add(tipo, alvo, m.group(0), m.start(), m.end(), conf, nota)
        spans_cit.append((m.start(), m.end()))
        if tipo == "RES":
            ult_org = (ult_org_cand, m.end())

    # --- normas nomeadas (Estatuto, Regimentos, CF) --------------------------
    for alvo, rx in NOMEADAS_RE:
        for m in rx.finditer(t):
            if alvo == meu_id:
                continue
            ctx = t[max(0, m.start() - 15):m.start()].lower()
            if alvo == "UFPB-CONSUNI-RES-07-2002" and ("novo estatuto" in t[max(0, m.start() - 12):m.end()].lower() or "minuta" in ctx):
                continue
            conf_n = "alta" if alvo != "UFPB-CONSUNI-RES-07-2002" or "ufpb" in m.group(0).lower() or "universidade" in m.group(0).lower() else "média"
            alvo_n, nota_n = alvo, ""
            if alvo == "UFPB-CONSUNI-RES-07-2002":
                if (fecho_meu and fecho_meu < "2002-11-22") or (not fecho_meu and meu_ano and meu_ano < 2002):
                    alvo_n = "UFPB-ESTATUTO-ANTERIOR-2002"
                    nota_n = "norma anterior à vigência do Estatuto de 2002 (Portaria MEC 3.198, DOU 22/11/2002): a referência é ao Estatuto então vigente"
                elif not fecho_meu and meu_ano == 2002:
                    conf_n, nota_n = "baixa", "norma de 2002 sem data identificada: pode referir-se ao Estatuto anterior"
            if any(q["destino"] == alvo_n and q["origem"] == meu_id and q.get("fim") is not None and
                   (0 <= m.start() - q["fim"] <= 25 or 0 <= q["pos"] - m.end() <= 25) for q in out):
                continue
            add("NOMEADA", alvo_n, m.group(0), m.start(), m.end(), conf_n, nota_n)

    # --- anotações de consolidação: (Redação dada pela Resolução nº X) ------
    for m in ANOTACAO_RE.finditer(t):
        ref = m.group("ref")
        verb = sem_acento(m.group("verb")).lower()
        for c in CIT_RE.finditer(ref):
            tipo = next(k for k, _ in TIPOS if c.group(k))
            itens = [(a, b or c2 or d) for a, b, c2, d in re.findall(rf"({NUMERO})\s*(?:/\s*(\d{{2,4}})(?!\d)|,?\s*de\s+\d{{1,2}}\s*(?:º|°|o)?\s+de\s+[A-Za-zçÇ]+\s+de\s+(\d{{4}})|,\s*de\s+(\d{{4}})(?!\d))", c.group("lista"))]
            for num_s, a in itens:
                n, suf = numint(num_s)
                if n is None:
                    continue
                ano = ano4(a)
                if tipo == "RES":
                    o = org_res(c.group("preorg") or "") or classifica_org_pos(ref[c.end() - c.start():])[0]
                    o = meu_cons if o in (None, "SELF") else o
                    alvo = id_ufpb(o, n, suf, ano) if o in ("CONSEPE", "CONSUNI", "CURADOR") else f"BR-{o}-RES-{n}{suf}-{ano}"
                else:
                    alvo = f"BR-{tipo}-{n}{suf}-{ano}"
                art = art_em(arts, m.start(), 0)
                rel = "REVOGA (parcial)" if "revogad" in verb or "suprimid" in verb else "ALTERA"
                trecho_a = re.sub(r"\s+", " ", t[max(0, m.start() - 160):m.end()]).strip()[-380:]
                cit_a = re.sub(r"\s+", " ", m.group(0))[:160]
                # parêntese logo após uma citação: descreve a norma citada ("Resolução 79/2013 (alterada pela Resolução 34/2014)")
                junto = [q for q in out if q["origem"] == meu_id and q.get("fim") is not None and q["fim"] <= m.start()
                         and m.start() - q["fim"] <= 70 and not re.search(r"[.;:]\s|\n\s*\n|\bArt", t[q["fim"]:m.start()])]
                _aa = re.search(r"-(\d{4})(?:-B)?$", alvo)
                ano_alvo = int(_aa.group(1)) if _aa else None
                if junto and junto[-1]["destino"] != alvo and not (junto[-1]["destino"].startswith(("BR-", "PB-")) and alvo.startswith("UFPB-")):
                    q = junto[-1]
                    rel_j = ("REVOGA (total)" if q["disp_destino"] == "norma inteira" else "REVOGA (parcial)") if ("revogad" in verb or "anulad" in verb) else "ALTERA"
                    out.append(dict(origem=alvo, disp_origem="norma inteira", destino=q["destino"], disp_destino=q["disp_destino"],
                                    tipo=rel_j, parte="anotação junto a citação", tipo_norma=tipo, citacao=cit_a, trecho=trecho_a,
                                    confianca="média", nota=f"relação mencionada entre parênteses no texto de {meu_id}", pos=m.start()))
                elif ano_alvo and meu_ano and ano_alvo < meu_ano and alvo.startswith("UFPB-") and meu_id.startswith("UFPB-"):
                    out.append(dict(origem=meu_id, disp_origem=("art. " + art) if art else "norma inteira", destino=alvo, disp_destino="norma inteira",
                                    tipo="REMETE A", parte="anotação junto a citação", tipo_norma=tipo, citacao=cit_a, trecho=trecho_a,
                                    confianca="média", nota="anotação transcrita de outra norma (a norma anotada é anterior a esta)", pos=m.start()))
                elif alvo.startswith(("BR-", "PB-", "OUTRO-")) and meu_id.startswith("UFPB-"):
                    out.append(dict(origem=meu_id, disp_origem=("art. " + art) if art else "norma inteira", destino=alvo, disp_destino="norma inteira",
                                    tipo="REMETE A", parte="anotação junto a citação", tipo_norma=tipo, citacao=cit_a, trecho=trecho_a,
                                    confianca="média", nota="anotação de norma externa em texto transcrito ou bibliografia (norma externa não altera o texto desta resolução)", pos=m.start()))
                else:
                    out.append(dict(origem=alvo, disp_origem="norma inteira", destino=meu_id,
                                    disp_destino=("art. " + art) if art else "dispositivo não identificado",
                                    tipo=rel, parte="anotação de consolidação", tipo_norma=tipo,
                                    citacao=cit_a, trecho=trecho_a,
                                    confianca="alta", nota="anotação no texto consolidado", pos=m.start()))
    # --- leis/decretos citados sem ano ------------------------------------
    for m in LEI_SEM_ANO.finditer(t):
        if any(a <= m.start() < b for a, b in spans_cit):
            continue
        n, suf = numint(m.group("n") + (m.group("s") or ""))
        if n is None or n < 100:
            continue
        tp = "LEI" if m.group("t").lower().startswith("lei") else "DEC"
        ano = (ano_lei or {}).get((tp, n))
        if ano:
            add(tp, f"BR-{tp}-{n}{suf}-{ano}", m.group(0), m.start(), m.end(), "média", "ano não indicado no texto; atribuído pelo número")
        else:
            add(tp, f"BR-{tp}-{n}{suf}-?", m.group(0), m.start(), m.end(), "baixa", "ano não indicado no texto")

    # --- pós-processamento ---------------------------------------------------
    spans = [(m.start(), m.end()) for m in ANOTACAO_RE.finditer(t)]
    ANOT = ("anotação de consolidação", "anotação junto a citação")
    out = [r for r in out if r["parte"] in ANOT or not any(a <= r["pos"] < b for a, b in spans)]
    cit = sorted([r for r in out if r["parte"] not in ANOT and r["parte"] != "citação indireta"], key=lambda r: r["pos"])
    derivs = []
    for k, r in enumerate(cit):
        if r["tipo"] != "CITA RELAÇÃO":
            continue
        prev = [q for q in cit[:k] if q["fim"] <= r["pos"] and (r["pos"] - q["fim"]) < 170 and q["destino"] != r["destino"]]
        if prev:
            bruto = t[prev[-1]["fim"]:r["pos"]]
            entre = re.sub(r"\s+", " ", bruto)
            m_ent = PASSIVO_RE.search(entre)
            if not m_ent:
                dme = DISP_FIM_RE.search(entre)
                if dme:
                    m_ent = PASSIVO_RE.search(entre[:dme.start()].rstrip() + " ")
            if not m_ent or len(entre[:m_ent.start()].strip(" ,;()–-")) > 45 or re.search(r"(?:^|\n)\s*(?:\(\*+\)\s*)?Art(?:igo)?\.?\s*\d|[.;]\s*\n", bruto) \
                    or re.search(r"[.;]\s", entre[:m_ent.start()]):
                prev = []
        pre_v = re.sub(r"\s+", " ", t[max(0, r["pos"] - 130):r["pos"]])
        verb = PASSIVO_RE.search(pre_v)
        disp_o_deriv = "norma inteira"
        if not verb:
            dmv = DISP_FIM_RE.search(pre_v)
            if dmv:
                verb = PASSIVO_RE.search(pre_v[:dmv.start()].rstrip() + " ")
                if verb:
                    disp_o_deriv = re.sub(r"\s+", " ", dmv.group(1)).strip(" ,")
        if not prev and verb:
            ini_cl = max(t.rfind("\n", 0, r["pos"]), 0)
            prefixo = t[ini_cl:r["pos"]]
            ini_fr = max(t.rfind(". ", 0, r["pos"]), t.rfind(".\n", 0, r["pos"]), ini_cl)
            nota_solta = ini_fr > ini_cl and re.fullmatch(r"[.\s]*" + _VERBO_ANOT + r"\s*", t[ini_fr:r["pos"]], re.I)
            if (ANOT_INICIO_RE.fullmatch(prefixo) or nota_solta) and not re.search(r"regulamentad", verb.group(1), re.I) and not (r["destino"].startswith(("BR-", "PB-", "OUTRO-")) and meu_id.startswith("UFPB-")):
                v = verb.group(1).lower()
                art = art_em(arts, r["pos"], 0)
                tp = "REVOGA (parcial)" if ("revogad" in v or "anulad" in v or "suprimid" in v) else "ALTERA"
                derivs.append(dict(origem=r["destino"], disp_origem="norma inteira", destino=meu_id,
                                   disp_destino=("art. " + art) if art else "dispositivo não identificado", tipo=tp,
                                   parte="anotação de consolidação", tipo_norma=r["tipo_norma"], citacao=r["citacao"], trecho=r["trecho"],
                                   confianca="média", nota="nota de alteração/revogação no próprio dispositivo", pos=r["pos"], fim=r["fim"], frase=r["frase"]))
        if prev and verb:
            q = prev[-1]
            idx = cit.index(q)
            while idx > 0 and q.get("_passivo"):
                cand = cit[idx - 1]
                if q["pos"] - cand["fim"] < 120:
                    q = cand; idx -= 1
                else:
                    break
            v = verb.group(1).lower()
            tp = "REVOGA (total)" if ("revogad" in v or "anulad" in v) else "REGULAMENTA" if "regulamentad" in v else "ALTERA"
            if tp.startswith("REVOGA") and q["disp_destino"] != "norma inteira":
                tp = "REVOGA (parcial)"
            gap = re.sub(r"\s+", " ", t[q["fim"]:r["pos"]])
            gm = PASSIVO_RE.search(gap)
            conf_d = "média" if gm and len(gap[:gm.start()].strip()) <= 3 else "baixa"
            derivs.append(dict(origem=r["destino"], disp_origem=disp_o_deriv, destino=q["destino"], disp_destino=q["disp_destino"],
                               tipo=tp, parte="citação indireta", tipo_norma=r["tipo_norma"], citacao=r["citacao"], trecho=r["trecho"],
                               confianca=conf_d, nota=f"relação mencionada no texto de {meu_id}", pos=r["pos"], fim=r["fim"], frase=r["frase"]))
        r["tipo"] = "REMETE A"; r["_passivo"] = True
        r["nota"] = (r["nota"] + "; " if r["nota"] else "") + "citada como norma que alterou/revogou/regulamentou outra"
    out += derivs
    for r in out:
        if r.get("_transcr_ini") is not None:
            intro = [q for q in out if q.get("_transcr_ini") is None and q["origem"] == meu_id and q.get("fim") is not None
                     and q["fim"] <= r["_transcr_ini"] and r["_transcr_ini"] - q["fim"] < 600 and q["parte"] == "dispositivo"]
            if intro:
                q = max(intro, key=lambda q: q["fim"])
                if q["tipo"] == "ALTERA":
                    r["transcr_de"] = q["destino"]
                    if not r["disp_transcrito"] and q["disp_destino"] != "norma inteira":
                        r["disp_transcrito"] = q["disp_destino"]
    for r in out:
        for k in ("tipo_transcrito", "disp_transcrito", "transcr_de"):
            r.setdefault(k, "")
        r.pop("fim", None); r.pop("frase", None); r.pop("_passivo", None); r.pop("_part_revoga", None); r.pop("_transcr_ini", None)
    ement_txt = re.sub(r"\s+", " ", t[ementa[0]:ementa[1]]).strip() if ementa else ""
    return out, dict(ementa=bool(ementa), resolve=bool(ini), artigos=len(arts), ementa_texto=ement_txt[:600], efeitos=efeitos_temporais(t))

def efeitos_temporais(t):
    """Cláusulas sobre o tempo dos efeitos da própria norma: retroação, vigência temporária, restabelecimento de redação anterior."""
    tt = re.sub(r"\s+", " ", t)
    tt = re.sub(r"(?i)\b(arts?|n[º°o]?|inc|incs|al|par|cap)\.(?=\s*\d)", r"\1·", tt)
    ef = []
    def dt(s):
        d = re.search(r"(\d{1,2})\s*(?:º|°|o)?\s+de\s+([A-Za-zçÇ]+)\s+de\s+(\d{4})", s)
        if d and MESES.get(sem_acento(d.group(2).lower())):
            return f"{int(d.group(3)):04d}-{MESES[sem_acento(d.group(2).lower())]:02d}-{int(d.group(1)):02d}"
        return ""
    for m in re.finditer(r"(?i)retroag\w*[^.;]{0,160}", tt):
        ctx = tt[max(0, m.start() - 160):m.start() + 30]
        if re.search(r"(?i)\b(?:n[ãa]o|vedad\w*|sem)\s+(?:\w+\s+){0,2}$", tt[max(0, m.start() - 30):m.start()]):
            continue
        if re.search(r"(?i)(?:esta|presente|desta|da\s+presente)\s+(?:Resolu|[Nn]orma)|seus\s+e\w+itos|os\s+efeitos|vig[êe]ncia\s+desta", ctx):
            ef.append(dict(tipo="efeito retroativo", data=dt(m.group(0)), trecho=m.group(0)[:220]))
    for m in re.finditer(r"(?i)(?:produzir[áa]|ter[áa])\s+efeitos?\s+(?:apenas\s+|somente\s+|exclusivamente\s+)?at[ée][^.;]{0,220}|vigorar[áa]\s+(?:por|pelo|durante)\s+(?:um\s+|o\s+)?(?:prazo|per[íi]odo)[^.;]{0,240}", tt):
        ef.append(dict(tipo="vigência temporária", data="", trecho=m.group(0)[:300]))
    for m in re.finditer(r"(?i)voltar[áa]\s+a\s+vigorar[^.;]{0,200}|vig[êe]ncia\s+restabelecid[oa][^.;]{0,160}|restabelec\w*\s+(?:a\s+)?(?:sua\s+)?reda[çc][ãa]o\s+(?:original|anterior)[^.;]{0,160}", tt):
        ef.append(dict(tipo="restabelecimento da redação anterior", data="", trecho=m.group(0)[:260]))
    for m in re.finditer(r"(?i)entra(?:r[áa])?\s+em\s+vigor\s+(?:(?:no|na|a\s+partir\s+d[oae]s?)\s+(?:primeiro|1\s*[ºo°]|in[íi]cio|per[íi]odo|semestre|ano\s+(?:letivo|acad)|pr[óo]xim|dia\s+\d|\d{1,2}\s*(?:º|°|o)?\s+de\s+[a-zç]+|data\s+de\s+\d)|ap[óo]s\s+(?:decorrid|o\s+prazo|\d+|sua\s+homologa))[^.;]{0,180}", tt):
        ef.append(dict(tipo="vigência diferida", data=dt(m.group(0)), trecho=m.group(0)[:240]))
    if re.search(r"(?i)entra(?:r[áa])?\s+em\s+vigor\s+na\s+data\s+d[ae]\s+(?:sua\s+)?aprova[çc][ãa]o", tt):
        ef.append(dict(tipo="vigência a partir da aprovação", data="", trecho=re.search(r"(?i)entra(?:r[áa])?\s+em\s+vigor\s+na\s+data\s+d[ae]\s+(?:sua\s+)?aprova[çc][ãa]o", tt).group(0)))
    for m in re.finditer(r"(?i)(?:ser[áa]\s+(?:permitid[oa]|facultad[oa]|assegurad[oa])|fica(?:m)?\s+(?:facultad[oa]|assegurad[oa]|garantid[oa]))\s+(?:a[o]?s?\s+)?(?:alun|discent|estudant|servidor|docent)\w*[^.;]{0,160}(?:enquadr|opt|migr|permanec|concluir|regid|vincul)\w*[^.;]{0,100}"
                         r"|passa\s+a\s+regulamentar[^.;]{0,140}ingressantes[^.;]{0,80}"
                         r"|sem\s+preju[íi]zo\s+d[oa]s?\s+(?:procedimentos|processos|atos|situa[çc][õo]es)\s+(?:j[áa]\s+)?(?:iniciad|em\s+curso|constitu)\w*[^.;]{0,100}"
                         r"|(?:garantind|resguardand|assegurand)\w*(?:-se)?\s+(?:a[o]?s?\s+)?(?:alun|discent|estudant)\w*[^.;]{0,180}", tt):
        ef.append(dict(tipo="regime de transição", data="", trecho=m.group(0)[:280]))
    for e in ef:
        e["trecho"] = e["trecho"].replace("·", ".")
    return ef

# ---------------------------------------------------------------------------
def datas(texto):
    t = prepara(texto)
    def conv(d, me, a):
        mm = MESES.get(sem_acento(me.lower()))
        if not mm or not (1 <= int(d) <= 31) or not (1950 <= int(a) <= 2030):
            return None
        return f"{int(a):04d}-{mm:02d}-{int(d):02d}"
    D_ = r"(\d{1,2})\s*(?:º|°|o)?\s*(?:de\s+)?([A-Za-zçÇ]+)\s+(?:de\s+)?(\d{4})"
    ses = re.search(rf"reuni[ãa]o[^.;]{{0,80}}?(?:realizada\s+)?(?:em|no\s+dia|de|do\s+dia)\s+{D_}", t, re.I)
    fechos = [m for m in re.finditer(rf"(?:Jo[ãa]o\s+Pessoa|Pessoa)\s*(?:\(PB\))?,?\s*(?:em\s+)?(?:de\s+)?{D_}", t, re.I) if conv(*m.groups())]
    fecho = conv(*fechos[-1].groups()) if fechos else None
    if not fecho:
        ult = [m for m in re.finditer(rf"(?:^|[\s,])(?:em\s+)?{D_}", t[-1200:]) if conv(*m.groups())]
        fecho = conv(*ult[-1].groups()) if ult else None
    return (conv(*ses.groups()) if ses else None), fecho

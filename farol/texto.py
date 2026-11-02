"""Texto integral: leitura do Markdown do acervo e conversão em HTML navegável.

O arquivo de cada norma tem um cabeçalho YAML, um resumo (ementa, situação,
relações) e a seção "## Texto integral" (ou "## Texto", nas normas federais).
Só a seção de texto é renderizada aqui; o resumo vem da base.

A conversão:
- junta linhas quebradas pelo pdftotext/OCR em parágrafos;
- abre um parágrafo novo em artigo, parágrafo, inciso, alínea e cabeçalhos
  (TÍTULO, CAPÍTULO, SEÇÃO, ANEXO…);
- dá âncora a cada artigo (``id="art-12"``; repetições viram ``art-12-2``);
- transforma as citações registradas na base em links para a norma citada;
- mantém ``~~tachado~~`` (redação revogada, textos do planalto) como <s>.

Nada do texto é alterado além disso: o que não é reconhecido fica como está.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .rotulos import slug

_RE_FRONT = re.compile(r"^---\n(.*?)\n---\n", re.S)
_RE_SECAO_TEXTO = re.compile(r"^## Texto( integral)?\s*$", re.M)
_RE_ART = re.compile(
    r"^\s*(?:~~)?(?:\(\*+\)\s*)*Art(?:igo|\.)?\s*\.?\s*(\d+)"
    r"(?:\s*[ºo°\.]?[\s\-–.:]|[ºo°](?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ]))",  # "Art. 1º " ou "Art. 1ºA" (sem espaço)
    re.I,
)
_RE_INICIO_UNIDADE = re.compile(
    r"^\s*(?:~~)?(?:\(\*+\)\s*)*("
    r"Art(?:igo|\.)?\s*\.?\s*\d+"  # artigo
    r"|§\s*\d*|Parágrafo\s+[úu]nico|Par[áa]grafo\s+[úu]nico"  # parágrafo
    r"|[IVXLC]+\s*[-–—.)]"  # inciso
    r"|[a-z]\)"  # alínea
    r"|\d+\.\s"  # item numerado
    r")",
    re.I,
)
_RE_CABECALHO = re.compile(
    r"^\s*(?:~~)?(T[IÍ]TULO|CAP[IÍ]TULO|SE[CÇ]{1,2}[ÃA]O|SUBSE[CÇ]{1,2}[ÃA]O|ANEXO|LIVRO|PARTE)\b", re.I
)
_RE_SO_MARCADOR = re.compile(r"^\s*(?:[IVXLC]+|§(?:\s*\d+[ºo°]?)?|Art\.?)\s*$", re.I)
_RE_PAGINA = re.compile(r"^\s*\[p[áa]gina\s+\d+\]\s*$", re.I)
_RE_TACHADO = re.compile(r"~~(.+?)~~", re.S)


@dataclass
class Texto:
    id: str
    cabecalho: dict
    corpo: str  # texto da seção "Texto integral", sem conversão
    paragrafos: list[str] = field(default_factory=list)


def ler(path: Path) -> Texto:
    s = path.read_text(encoding="utf-8")
    cab: dict = {}
    m = _RE_FRONT.match(s)
    if m:
        try:
            cab = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            cab = {}
        s_resto = s[m.end():]
    else:
        s_resto = s
    ms = _RE_SECAO_TEXTO.search(s_resto)
    corpo = s_resto[ms.end():] if ms else ""
    t = Texto(id=str(cab.get("id") or path.stem), cabecalho=cab, corpo=corpo)
    t.paragrafos = reflow(corpo)
    return t


def reflow(corpo: str) -> list[str]:
    """Junta linhas quebradas e separa unidades do texto normativo."""
    paras: list[str] = []
    atual: list[str] = []
    pendente_marcador = ""  # "I" ou "§ 1º" numa linha só, a juntar com a próxima

    def fecha():
        nonlocal atual
        if atual:
            paras.append(" ".join(x.strip() for x in atual).strip())
            atual = []

    for linha in corpo.split("\n"):
        if _RE_PAGINA.match(linha):
            fecha()
            paras.append(linha.strip())
            continue
        if not linha.strip():
            if pendente_marcador:
                continue
            fecha()
            continue
        if _RE_SO_MARCADOR.match(linha):
            fecha()
            pendente_marcador = (pendente_marcador + " " + linha.strip()).strip()
            continue
        if pendente_marcador:
            linha = pendente_marcador + " " + linha.strip()
            pendente_marcador = ""
            fecha()
            atual = [linha]
            continue
        if _RE_INICIO_UNIDADE.match(linha) or _RE_CABECALHO.match(linha):
            fecha()
        atual.append(linha)
    if pendente_marcador:
        atual.append(pendente_marcador)
    fecha()
    return [p for p in paras if p]


def _classe(p: str) -> str:
    if _RE_PAGINA.match(p):
        return "pagina"
    if _RE_CABECALHO.match(p) and len(p) < 120:
        return "cab"
    if _RE_ART.match(p):
        return "art"
    if re.match(r"^\s*(?:~~)?(?:\(\*+\)\s*)*(§|Par[áa]grafo\s+[úu]nico)", p, re.I):
        return "par"
    if re.match(r"^\s*(?:~~)?[IVXLC]+\s*[-–—.)]", p):
        return "inc"
    if re.match(r"^\s*(?:~~)?[a-z]\)", p):
        return "ali"
    if p.isupper() and len(p) < 100:
        return "cab2"
    return "p"


def _escapar(p: str) -> str:
    s = html.escape(p, quote=False)
    s = _RE_TACHADO.sub(r"<s>\1</s>", s)
    return s


class Ligador:
    """Transforma citações registradas na base em links.

    ``citacoes`` é um dicionário texto-citado → (id_destino, dispositivo_destino).
    Só entram textos que apontam para uma única norma; os ambíguos ficam de fora.
    """

    def __init__(self, citacoes: dict[str, tuple[str, str]], prefixo: str = "../../norma/"):
        itens = sorted(citacoes.items(), key=lambda kv: -len(kv[0]))
        self.itens = [(html.escape(c, quote=False), dest, disp) for c, (dest, disp) in itens if len(c) >= 4]
        self.prefixo = prefixo
        self.contagem = 0

    def aplicar(self, s_html: str) -> str:
        if not self.itens:
            return s_html
        # protege trechos já linkados: marca posições ocupadas
        ocupado: list[tuple[int, int]] = []
        saida = s_html
        for cit, dest, disp in self.itens:
            pos = 0
            while True:
                i = saida.find(cit, pos)
                if i < 0:
                    break
                j = i + len(cit)
                if any(a <= i < b or a < j <= b for a, b in ocupado):
                    pos = j
                    continue
                anc = _ancora_dispositivo(disp)
                link = f'<a class="cit" href="{self.prefixo}{slug(dest)}/{anc}" title="{html.escape(dest)}">{cit}</a>'
                saida = saida[:i] + link + saida[j:]
                desloc = len(link) - len(cit)
                ocupado = [(a + desloc, b + desloc) if a >= i else (a, b) for a, b in ocupado]
                ocupado.append((i, i + len(link)))
                pos = i + len(link)
                self.contagem += 1
        return saida


_RE_ART_SUFIXO = re.compile(
    r"^\s*(?:~~)?(?:\(\*+\)\s*)*Art(?:igo|\.)?\s*\.?\s*\d+[ºo°]?-([A-Z])\b"  # "Art. 7º-A" (sem espaço antes do hífen; "Art. 3º - A presente…" não é sufixo)
)
_RE_DISP_ART = re.compile(r"^\s*art(?:igos?|s)?\.?\s*(\d+)[ºo°]?(?:-([A-Za-z])\b)?", re.I)


def _chave_artigo(p: str) -> str:
    """Número do artigo com o sufixo de letra, quando houver: "7" ou "7-A"."""
    num = _RE_ART.match(p).group(1)
    ms = _RE_ART_SUFIXO.match(p)
    return f"{num}-{ms.group(1)}" if ms else num


def _ancora_dispositivo(disp: str) -> str:
    m = _RE_DISP_ART.match(disp or "")
    if not m:
        return ""
    return f"#art-{m.group(1)}" + (f"-{m.group(2).upper()}" if m.group(2) else "")


def render_html(t: Texto, ligador: Ligador | None = None, notas: dict[str, str] | None = None) -> tuple[str, dict]:
    """HTML do texto e um índice de artigos (número → âncora).

    ``notas`` mapeia o artigo ("12", "7-A") a um bloco HTML já pronto, inserido
    logo após o caput da primeira ocorrência do artigo (anotações de vigência:
    quem o altera, revoga ou supera). O texto em si não é alterado.
    """
    partes: list[str] = []
    vistos: dict[str, int] = {}
    indice: dict[str, str] = {}
    notas = notas or {}
    for p in t.paragrafos:
        cl = _classe(p)
        rev = p.lstrip().startswith("~~")  # redação tachada no texto consolidado: não recebe âncora
        s = _escapar(p)
        if ligador:
            s = ligador.aplicar(s)
        if rev and cl in ("art", "cab"):
            partes.append(f'<p class="{"p" if cl == "art" else "cab2"} rev">{s}</p>')
            continue
        if rev:
            partes.append(f'<p class="{cl} rev">{s}</p>')
            continue
        if cl == "pagina":
            partes.append(f'<div class="pagina">{s}</div>')
        elif cl == "cab":
            partes.append(f'<h3 class="cab">{s}</h3>')
        elif cl == "cab2":
            partes.append(f'<p class="cab2">{s}</p>')
        elif cl == "art":
            num = _chave_artigo(p)
            vistos[num] = vistos.get(num, 0) + 1
            anc = f"art-{num}" if vistos[num] == 1 else f"art-{num}-{vistos[num]}"
            indice.setdefault(num, anc)
            partes.append(f'<p class="art" id="{anc}"><a class="anc" href="#{anc}" aria-label="Link para o artigo {num}">¶</a>{s}</p>')
            if vistos[num] == 1 and num in notas:
                partes.append(notas[num])
        else:
            partes.append(f'<p class="{cl}">{s}</p>')
    return "\n".join(partes), indice

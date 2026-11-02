"""Geração do site estático em site/ a partir da base e dos textos."""

from __future__ import annotations

import csv
import html
import json
import re
import shutil
from collections import Counter
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from . import grafo, texto as mod_texto
from .base import Base, Norma
from .rotulos import CHAVE_RELACAO, NIVEIS, NOME_NIVEL, NOME_SITUACAO, rotulo as fn_rotulo, slug

AQUI = Path(__file__).parent
DESTAQUES = [
    "UFPB-CONSUNI-RES-07-2002", "UFPB-REGIMENTO-GERAL", "UFPB-CONSUNI-RES-279-1978",
    "UFPB-CONSUNI-RES-257-1979", "UFPB-CONSEPE-RES-29-2020", "BR-LEI-9394-1996",
    "BR-LEI-8112-1990", "UFPB-NT-MINUTA-ESTATUTO-2019",
]
_RE_ID = re.compile(r"\b((?:UFPB|BR|PB|OUTRO)-[A-Z0-9?\-]+-[0-9A-Z]+-(?:\d{4}|\?))\b")
_RE_DISP_RESTO = re.compile(r"\bart(?:igo)?s?\.?\s*|\d+\s*[ºo°]?(?:-[A-Za-z]\b)?|\b(?:e|a|ou|até)\b|[;,]", re.I)


def _br(v) -> str:
    try:
        return f"{int(v):,}".replace(",", ".")
    except (TypeError, ValueError):
        return str(v)


def _data_br(d: str) -> str:
    d = (d or "").strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", d):
        a, m, dd = d.split("-")
        return f"{dd}/{m}/{a}"
    return d or "—"


class Gerador:
    def __init__(self, raiz: str | Path, saida: str | Path | None = None):
        self.raiz = Path(raiz)
        self.saida = Path(saida) if saida else self.raiz / "site"
        self.base = Base.carregar(self.raiz)
        self.env = Environment(
            loader=FileSystemLoader(str(AQUI / "templates")),
            autoescape=select_autoescape(["html"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        b = self.base
        self.env.filters["br"] = _br
        self.env.filters["slug"] = slug
        self.env.filters["data_br"] = _data_br
        self.env.filters["nome_situacao"] = lambda k: NOME_SITUACAO.get(k, k)
        self.env.filters["nome_nivel"] = lambda k: NOME_NIVEL.get(k, k)
        self.env.filters["rotulo"] = lambda i: b.normas[i].rotulo if i in b.normas else fn_rotulo(i)
        self.env.filters["ids_para_links"] = self._ids_para_links
        self.env.filters["abbr_ocr"] = self._abbr_ocr
        self.env.globals["OCR_EXPLICACAO"] = self._OCR
        self.meta = {"rodada": "Rodada 4", "data_base": "2026-11-02", "data_base_br": "02/11/2026"}
        self.contadores: Counter = Counter()

    # ---- utilidades ----------------------------------------------------
    def _ids_para_links(self, s: str):
        from markupsafe import Markup

        def sub(m):
            i = m.group(1)
            if i in self.base.normas:
                return f'<a href="{self._raiz_rel}norma/{slug(i)}/" target="_blank" rel="noopener">{html.escape(self.base.normas[i].rotulo)}</a>'
            return html.escape(i)

        return Markup(_RE_ID.sub(sub, html.escape(s or "")))

    _OCR = ("OCR (reconhecimento óptico de caracteres): o texto foi lido automaticamente da imagem do PDF digitalizado, "
            "sem camada de texto; números e letras podem ter sido trocados. Confira no PDF oficial antes de citar.")

    def _abbr_ocr(self, s: str):
        """Marca a sigla OCR com a explicação (aparece ao passar o mouse)."""
        from markupsafe import Markup

        return Markup(html.escape(s or "").replace("OCR", f'<abbr class="tip" tabindex="0" data-tip="{html.escape(self._OCR)}">OCR</abbr>'))

    _raiz_rel = "../../"

    def _escrever(self, rel: str, conteudo: str) -> None:
        p = self.saida / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(conteudo, encoding="utf-8")

    def _render(self, tpl: str, rel: str, raiz: str, **ctx) -> None:
        self._raiz_rel = raiz
        t = self.env.get_template(tpl)
        ctx.setdefault("meta", self.meta)
        self._escrever(rel, t.render(raiz=raiz, **ctx))

    # ---- etapas --------------------------------------------------------
    def gerar(self, limite_textos: int | None = None) -> dict:
        b = self.base
        if self.saida.exists():
            shutil.rmtree(self.saida)
        (self.saida / "assets").mkdir(parents=True)
        for f in (AQUI / "static").iterdir():
            shutil.copy(f, self.saida / "assets" / f.name)
        self._dados()
        self._index()
        self._normas(limite_textos)
        self._teia()
        self._busca()
        self._estrutura()
        self._vigencia()
        self._divergencias()
        self._fila()
        self._sobre()
        (self.saida / ".nojekyll").write_text("")
        return dict(self.contadores)

    def _dados(self):
        d = grafo.dados_teia(self.base)
        self.meta_teia = d["meta"]
        self._escrever("dados/teia.json", json.dumps(d, ensure_ascii=False, separators=(",", ":")))
        self._escrever("dados/fichas.json", json.dumps(grafo.dados_fichas(self.base), ensure_ascii=False, separators=(",", ":")))

    def _index(self):
        b = self.base
        dest = [b.normas[i] for i in DESTAQUES if i in b.normas]
        m = dict(self.meta_teia)
        self._render("index.html", "index.html", "./", secao="inicio", meta={**self.meta, **m}, destaques=dest)

    def _nota_artigo(self, art: str, rels: list) -> str:
        """Bloco HTML inserido sob o caput do artigo: quem o altera, revoga ou supera."""
        b = self.base
        itens = []
        for r in rels:
            n = b.normas.get(r.origem)
            rot = html.escape(n.rotulo if n else fn_rotulo(r.origem))
            anc = (mod_texto._ancora_dispositivo(r.disp_origem) or "#texto") if (n and n.texto_path) else ""
            link = f'<a class="n" href="../../norma/{slug(r.origem)}/{anc}" target="_blank" rel="noopener">{rot}</a>' if n else rot
            det = []
            if r.disp_origem and r.disp_origem != "norma inteira":
                det.append(f"na outra: {html.escape(r.disp_origem)}")
            if _RE_DISP_RESTO.sub("", r.disp_destino or "").strip(" ;,.-–()"):  # há mais que a lista de artigos
                det.append(f"alcança: {html.escape(r.disp_destino[:140])}")
            if r.inicio_efeito:
                det.append(f"efeito desde {_data_br(r.inicio_efeito)}")
            if r.ressalva:
                det.append(html.escape(r.ressalva))
            det.append(f"fonte: {html.escape(r.base or '—')}" + (f" · confiança {html.escape(r.confianca)}" if r.confianca else ""))
            q = f'<span class="q">“{html.escape(r.trecho[:240])}{"…" if len(r.trecho) > 240 else ""}”</span>' if r.trecho else ""
            itens.append(f'<div class="it"><span class="k {r.chave}">{html.escape(r.tipo)}</span>{link}<span class="d">{" · ".join(det)}</span>{q}</div>')
        chaves = {r.chave for r in rels}
        classe = "R" if "R" in chaves else "P" if "P" in chaves else "S" if "S" in chaves and "A" not in chaves else "A"
        return (f'<div class="nota-art {classe}" role="note"><span class="t">Vigência deste artigo · registrado na base</span>'
                + "".join(itens) + "</div>")

    def _normas(self, limite_textos):
        b = self.base
        decisoes = {d["norma"]: d for d in b.decisoes.get("situacao", [])}
        feitos_texto = 0
        for n in b.normas.values():
            texto_html = ""
            n_links = n_arts = n_notas = 0
            versao = ""
            if n.texto_path is not None and (limite_textos is None or feitos_texto < limite_textos):
                try:
                    t = mod_texto.ler(n.texto_path)
                    lig = mod_texto.Ligador(grafo.citacoes_para_links(b, n), prefixo="../../norma/")
                    notas = {a: self._nota_artigo(a, rels) for a, rels in grafo.notas_por_artigo(b, n.id).items()}
                    texto_html, indice = mod_texto.render_html(t, lig, notas)
                    n_links, n_arts = lig.contagem, len(indice)
                    n_notas = sum(1 for a in notas if a in indice)
                    versao = str(t.cabecalho.get("versao") or "")
                    feitos_texto += 1
                    self.contadores["textos"] += 1
                    self.contadores["links_em_textos"] += n_links
                    self.contadores["artigos_ancorados"] += n_arts
                    self.contadores["artigos_anotados"] += n_notas
                except Exception as e:  # noqa: BLE001 — um texto ruim não derruba o site
                    self.contadores["textos_com_erro"] += 1
                    texto_html = f'<p class="hint">Não foi possível renderizar o texto: {html.escape(str(e))}</p>'
            entrada = [(r, r.origem) for r in b.entrada.get(n.id, [])]
            saida = [(r, r.destino) for r in b.saida.get(n.id, [])]
            entrada.sort(key=lambda x: (x[0].citacao_simples, x[0].tipo, x[1]))
            saida.sort(key=lambda x: (x[0].citacao_simples, x[0].tipo, x[1]))
            irmas, paralelas = grafo.sugestoes(b, n.id)
            self._render(
                "norma.html", f"norma/{slug(n.id)}/index.html", "../../",
                secao="norma", n=n, entrada=entrada, saida=saida,
                dispositivos=grafo.por_dispositivo(b, n.id), irmas=irmas, paralelas=paralelas,
                decisao=decisoes.get(n.id), texto_html=texto_html, n_links=n_links, n_arts=n_arts, n_notas=n_notas, versao=versao,
                descricao=(n.ementa or n.ementa_sigrh)[:160],
            )
            self.contadores["paginas_norma"] += 1

    def _teia(self):
        self._render("teia.html", "teia/index.html", "../", secao="teia")

    def _busca(self):
        self._render("busca.html", "busca/index.html", "../", secao="busca")

    def _link(self, i: str) -> str:
        n = self.base.normas.get(i)
        return f'<a href="../norma/{slug(i)}/">{html.escape(n.rotulo if n else i)}</a>'

    def _vigencia(self):
        b = self.base
        por = Counter(n.situacao_chave for n in b.normas.values())
        resumo = [(NOME_SITUACAO[k], v) for k, v in sorted(por.items(), key=lambda kv: -kv[1])]
        blocos = []
        # normas da UFPB com alteração ou revogação, por situação
        for chave, titulo, texto in [
            ("conflito", "Conflitos de vigência", "Leituras contraditórias registradas como divergência; o acervo não escolhe a leitura."),
            ("verificar", "A verificar", "O arquivo do SIGRH contém o texto de outra norma."),
            ("revogada", "Normas revogadas", "Revogação expressa e integral por norma posterior, conferida no texto da revogadora."),
            ("alterada", "Normas alteradas ou revogadas em parte", "Inclui dispositivos superados por norma superior."),
        ]:
            linhas = []
            for n in sorted((x for x in b.normas.values() if x.situacao_chave == chave and not x.federal), key=lambda x: (x.orgao, x.ano, x.numero)):
                linhas.append([self._link(n.id), html.escape(n.orgao), html.escape(n.ano), html.escape(n.situacao), self._ids_para_links_html(n.situacao_base)])
            blocos.append({"id": chave, "titulo": titulo + " (UFPB)", "texto": texto, "colunas": ["Norma", "Órgão", "Ano", "Situação", "Base"], "linhas": linhas})
        self._render("painel.html", "vigencia/index.html", "../", secao="vigencia", titulo="Quadro de vigência",
                     lead="Situação de cada norma conforme o texto das normas posteriores. As normas federais seguem a anotação do texto compilado do planalto e das notas oficiais do CNE.",
                     resumo=resumo, blocos=blocos)

    def _estrutura(self):
        """Estatuto, regimentos comuns e minuta em tramitação: a espinha dorsal do acervo."""
        b = self.base
        descr = {
            "UFPB-CONSUNI-RES-07-2002": "Norma máxima da universidade (N5), homologada pela Portaria MEC 3.198/2002. Define fins, estrutura, órgãos e competências; é a base de todos os regimentos.",
            "UFPB-REGIMENTO-GERAL": "Disciplina a organização e o funcionamento comuns aos órgãos e serviços da UFPB (art. 107 do Estatuto). Texto consolidado pela SODS, com as redações revogadas tachadas.",
            "UFPB-CONSUNI-RES-279-1978": "Regimento dos Órgãos Deliberativos da Administração Superior: funcionamento do CONSUNI, do CONSEPE e do Conselho Curador, sessões, pedidos de reconsideração e recursos.",
            "UFPB-CONSUNI-RES-257-1979": "Regimento da Reitoria: estrutura e atribuições dos órgãos executivos da administração superior.",
            "UFPB-ESTATUTO-ANTERIOR-2002": "Estatuto substituído pela Res. CONSUNI 07/2002; citado por normas antigas e ainda sem texto no acervo.",
            "UFPB-NT-MINUTA-ESTATUTO-2019": "Minuta do novo Estatuto aprovada no CONSEPE (16/03/2020) e em análise no CONSUNI. Sem força normativa: serve só para sinalizar a mudança em discussão.",
        }
        def bloco(titulo, texto, niveis):
            linhas = []
            for n in sorted((x for x in b.normas.values() if x.nivel in niveis), key=lambda x: (NIVEIS.index(x.nivel), x.ano, x.orgao)):
                alt = [r for r in b.entrada.get(n.id, []) if r.tipo in grafo.TIPOS_VIGENCIA and not r.sugestao]
                arts = {a for r in alt for a in grafo.artigos_do_dispositivo(r.disp_destino)}
                situ = f'<span class="pill {n.situacao_chave}">{html.escape(NOME_SITUACAO.get(n.situacao_chave, n.situacao_chave))}</span>'
                texto_col = (f'<a href="../norma/{slug(n.id)}/#texto">texto integral</a><br><span class="hint">{html.escape(n.metodo_texto or "")}</span>'
                             if n.texto_path else '<span class="hint">sem texto no acervo</span>')
                vig = (f"{len(alt)} relação(ões) de alteração, revogação ou superação; {len(arts)} artigo(s) alcançado(s)" if alt else "nenhuma registrada")
                linhas.append([self._link(n.id) + f'<br><span class="hint">{html.escape(descr.get(n.id, n.ementa or n.ementa_sigrh)[:300])}</span>',
                               f'<span class="pill lvl">{n.nivel}</span>', situ, html.escape(vig), texto_col])
            return {"id": niveis[0].lower(), "titulo": titulo, "texto": texto, "colunas": ["Norma", "Nível", "Situação", "Vigência registrada", "Texto"], "linhas": linhas}
        blocos = [
            bloco("Estatuto (N5)", "Res. CONSUNI 07/2002. Cada alteração anotada no texto consolidado foi conferida com a resolução alteradora.", ["N5"]),
            bloco("Regimentos comuns (N6)", "Previstos no art. 107 do Estatuto: Regimento Geral, Regimento dos Órgãos Deliberativos (Res. 279/78) e Regimento da Reitoria (Res. 257/79).", ["N6"]),
            bloco("Em tramitação (NT)", "Sem força normativa. O Farol mostra o que a minuta prevê e deixa claro que ainda não vigora.", ["NT"]),
            bloco("Regimentos de unidades (N8)", "Regimentos internos das pró-reitorias, superintendências e centros de ensino. Estão na fila de coleta: ainda sem texto, número ou data no acervo.", ["N8"]),
        ]
        self._render("painel.html", "estrutura/index.html", "../", secao="estrutura", titulo="Estatuto e regimentos",
                     lead="As normas estruturais da UFPB, de onde partem as demais: o Estatuto, os três regimentos comuns e a minuta do novo Estatuto. No texto integral de cada uma, os artigos alterados, revogados ou superados trazem a anotação e o link para a norma que os alcança.",
                     resumo=None, blocos=blocos)

    def _ids_para_links_html(self, s: str) -> str:
        def sub(m):
            i = m.group(1)
            return self._link(i) if i in self.base.normas else html.escape(i)
        return _RE_ID.sub(sub, html.escape(s or ""))

    def _divergencias(self):
        b = self.base
        blocos = []
        dec = b.decisoes
        linhas = [[html.escape(d.get("divergencia", "")), self._link(d["norma"]), html.escape(d.get("situacao", "")), self._ids_para_links_html(d.get("situacao_base", "")), html.escape(d.get("fundamento", ""))] for d in dec.get("situacao", [])]
        blocos.append({"id": "decisoes", "titulo": "Decisões de vigência fundamentadas", "texto": dec.get("descricao", ""), "colunas": ["Div.", "Norma", "Situação decidida", "Base", "Fundamento"], "linhas": linhas})
        sug = [[self._link(s["origem"]), html.escape(s.get("tipo", "")), self._link(s["destino"]), html.escape(s.get("natureza", "")), html.escape(s.get("obs", ""))] for s in dec.get("sugestoes", [])]
        blocos.append({"id": "sugestoes", "titulo": "Sugestões de alvo provável (não aplicadas à vigência)", "colunas": ["Origem", "Tipo", "Destino provável", "Natureza", "Obs."], "linhas": sug})
        p = self.raiz / "base" / "divergencias" / "divergencias_r2.csv"
        if p.exists():
            with open(p, encoding="utf-8", newline="") as f:
                rows = list(csv.DictReader(f))
            linhas = [[html.escape(r["tipo"]), self._link(r["norma"]), html.escape(r["descricao"]), self._link(r["relacionada"]) if r.get("relacionada") in b.normas else html.escape(r.get("relacionada", ""))] for r in rows]
            blocos.append({"id": "r2", "titulo": "Divergências da Rodada 2 (atos do CNE)", "colunas": ["Tipo", "Norma", "Descrição", "Relacionada"], "linhas": linhas})
        p = self.raiz / "base" / "divergencias" / "registro_divergencias.md"
        if p.exists():
            import markdown

            md = p.read_text(encoding="utf-8")
            blocos.append({"id": "registro", "titulo": "Registro de divergências (Rodadas 0 e 1)", "html": '<div class="card md">' + markdown.markdown(self._ids_para_links_html_md(md), extensions=["tables"]) + "</div>"})
        self._render("painel.html", "divergencias/index.html", "../", secao="divergencias", titulo="Divergências e decisões",
                     lead="Conflitos de vigência, fundamentos em norma revogada, números citados que não correspondem ao assunto e decisões tomadas pela leitura direta dos textos. Nada aqui resolve o conflito: registra e explica.",
                     resumo=None, blocos=blocos)

    def _ids_para_links_html_md(self, md: str) -> str:
        def sub(m):
            i = m.group(1)
            if i in self.base.normas:
                return f"[{self.base.normas[i].rotulo}](../norma/{slug(i)}/)"
            return i
        return _RE_ID.sub(sub, md)

    def _fila(self):
        b = self.base
        grupos: dict[str, list[Norma]] = {}
        for n in b.normas.values():
            if not n.fantasma:
                continue
            if n.id.startswith("UFPB-CONS") or n.id.startswith("UFPB-CURADOR"):
                g = "Resoluções dos conselhos superiores (pedido à SODS)"
            elif n.id.startswith("UFPB-REGIMENTO-"):
                g = "Regimentos de unidades: pró-reitorias, superintendências e centros (pedido da coordenação)"
            elif n.id.startswith("UFPB-"):
                g = "Normas de unidades, pró-reitorias e reitoria da UFPB"
            elif n.id.startswith("BR-CNE") or n.id.startswith("BR-CFE") or n.id.startswith("BR-MEC") or n.id.startswith("BR-CAPES") or n.id.startswith("BR-SERES") or n.id.startswith("BR-INEP"):
                g = "MEC, CNE, CAPES e autarquias"
            elif n.id.startswith("BR-LEI") or n.id.startswith("BR-DEC") or n.id.startswith("BR-DL") or n.id.startswith("BR-LC") or n.id.startswith("BR-EC") or n.id.startswith("BR-MP"):
                g = "Leis, decretos e emendas"
            elif n.id.startswith("?") or n.id.startswith("OUTRO") or n.id.startswith("BR-?"):
                g = "Órgão não identificado ou outra instituição"
            else:
                g = "Outros órgãos federais, conselhos profissionais e estaduais"
            grupos.setdefault(g, []).append(n)
        blocos = []
        ordem = sorted(grupos.items(), key=lambda kv: (0 if "coordenação" in kv[0] else 1, -len(kv[1])))
        for g, lst in ordem:
            if "coordenação" in g:
                lst.sort(key=lambda n: (0 if "Pró-Reitoria" in n.ementa else 1 if "Superintendência" in n.ementa else 2, n.orgao))
                texto = "Regimentos internos das unidades listadas no site oficial da UFPB, postos na fila em 02/11/2026 a pedido da coordenação do Farol (não entraram por citação). Número, data e ato de aprovação só depois de localizar o texto no site da unidade, na SODS ou no SIGRH."
            else:
                lst.sort(key=lambda n: -b.grau_entrada(n.id))
                texto = ""
            linhas = [[self._link(n.id), html.escape(n.status_coleta), self._vigencia_registrada(n), _br(b.grau_entrada(n.id)),
                       html.escape(n.ementa or n.obs) + (f' · <a href="{html.escape(n.fonte)}" target="_blank" rel="noopener">site da unidade ↗</a>' if n.id.startswith("UFPB-REGIMENTO-") and n.fonte else "")] for n in lst]
            blocos.append({"id": re.sub(r"[^a-z]+", "-", g.lower()), "titulo": g, "texto": texto, "colunas": ["Norma", "Situação da coleta", "Vigência registrada no acervo", "Citada por", "Descrição / observação"], "linhas": linhas})
        resumo = [("na fila, sem texto", sum(len(v) for v in grupos.values()))] + [(g, len(v)) for g, v in ordem]
        self._render("painel.html", "fila/index.html", "../", secao="fila", titulo="Fila de coleta",
                     lead="Normas ainda sem texto no acervo: as citadas por outras normas (aparecem tracejadas na Teia) e os regimentos de unidades pedidos pela coordenação. A coluna de vigência mostra o que as normas já lidas dizem sobre cada uma; nada aqui afirma que uma norma não lida está em vigor. A lista das resoluções dos conselhos superiores é o pedido feito à SODS.",
                     resumo=resumo, blocos=blocos)

    def _vigencia_registrada(self, n: Norma) -> str:
        """O que as normas já lidas dizem sobre uma norma sem texto: revogação, alteração ou superação registradas na base."""
        b = self.base
        rels = [r for r in b.entrada.get(n.id, []) if r.tipo in grafo.TIPOS_VIGENCIA and not r.sugestao]
        partes = []
        if n.situacao_chave not in ("nao_localizada", "desconhecida"):
            partes.append(f'<span class="pill {n.situacao_chave}">{html.escape(NOME_SITUACAO.get(n.situacao_chave, n.situacao_chave))}</span>')
        if not rels:
            partes.append('<span class="hint">nenhuma alteração ou revogação registrada</span>')
            return " ".join(partes)
        rotulo_tipo = {"REVOGA (total)": "revogada por", "REVOGA (parcial)": "revogada em parte por", "ALTERA": "alterada por", "SUPERA": "superada por"}
        por_tipo: dict[str, list[str]] = {}
        for r in sorted(rels, key=lambda r: (grafo._data_norm(r.inicio_efeito) or "9999", r.origem)):
            lk = self._link(r.origem) + (f' <span class="hint">({html.escape(r.disp_destino)})</span>' if r.disp_destino and r.disp_destino != "norma inteira" else "")
            if lk not in por_tipo.setdefault(r.tipo, []):
                por_tipo[r.tipo].append(lk)
        for t in ("REVOGA (total)", "REVOGA (parcial)", "SUPERA", "ALTERA"):
            if t in por_tipo:
                partes.append(f'<span class="k {CHAVE_RELACAO[t]}">{html.escape(t)}</span> {rotulo_tipo[t]} ' + ", ".join(por_tipo[t]))
        return "<br>".join(partes)

    def _sobre(self):
        b = self.base
        por = Counter(n.nivel for n in b.normas.values())
        niveis = [(nv, NOME_NIVEL[nv], por.get(nv, 0)) for nv in NIVEIS if por.get(nv)]
        rodadas = []
        pasta = self.raiz / "docs" / "rodadas"
        if pasta.exists():
            import markdown

            for p in sorted(pasta.glob("*.md")):
                htm = markdown.markdown(self._ids_para_links_html_md(p.read_text(encoding="utf-8")), extensions=["tables"])
                titulo = re.sub(r"^#\s*(Oraculovski\s*·\s*)?", "", p.read_text(encoding="utf-8").split("\n", 1)[0])
                rel = f"sobre/{p.stem}.html"
                self._raiz_rel = "../"
                self._escrever(rel, self.env.get_template("painel.html").render(raiz="../", meta=self.meta, secao="sobre", titulo=titulo, lead="", resumo=None, blocos=[{"id": "doc", "titulo": "", "html": '<div class="card md">' + htm + "</div>"}]))
                rodadas.append({"arquivo": f"{p.stem}.html", "titulo": titulo})
        self._render("sobre.html", "sobre/index.html", "../", secao="sobre", niveis=niveis, rodadas=rodadas)

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
from .rotulos import NIVEIS, NOME_NIVEL, NOME_SITUACAO, rotulo as fn_rotulo, slug

AQUI = Path(__file__).parent
DESTAQUES = [
    "UFPB-CONSUNI-RES-07-2002", "UFPB-REGIMENTO-GERAL", "UFPB-CONSUNI-RES-279-1978",
    "UFPB-CONSUNI-RES-257-1979", "UFPB-CONSEPE-RES-29-2020", "BR-LEI-9394-1996",
    "BR-LEI-8112-1990", "UFPB-NT-MINUTA-ESTATUTO-2019",
]
_RE_ID = re.compile(r"\b((?:UFPB|BR|PB|OUTRO)-[A-Z0-9?\-]+-[0-9A-Z]+-(?:\d{4}|\?))\b")


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
        self.meta = {"rodada": "Rodada 2", "data_base": "2026-10-20", "data_base_br": "20/10/2026"}
        self.contadores: Counter = Counter()

    # ---- utilidades ----------------------------------------------------
    def _ids_para_links(self, s: str):
        from markupsafe import Markup

        def sub(m):
            i = m.group(1)
            if i in self.base.normas:
                return f'<a href="{self._raiz_rel}norma/{slug(i)}/">{html.escape(self.base.normas[i].rotulo)}</a>'
            return html.escape(i)

        return Markup(_RE_ID.sub(sub, html.escape(s or "")))

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

    def _normas(self, limite_textos):
        b = self.base
        decisoes = {d["norma"]: d for d in b.decisoes.get("situacao", [])}
        feitos_texto = 0
        for n in b.normas.values():
            texto_html = ""
            n_links = n_arts = 0
            versao = ""
            if n.texto_path is not None and (limite_textos is None or feitos_texto < limite_textos):
                try:
                    t = mod_texto.ler(n.texto_path)
                    lig = mod_texto.Ligador(grafo.citacoes_para_links(b, n), prefixo="../../norma/")
                    texto_html, indice = mod_texto.render_html(t, lig)
                    n_links, n_arts = lig.contagem, len(indice)
                    versao = str(t.cabecalho.get("versao") or "")
                    feitos_texto += 1
                    self.contadores["textos"] += 1
                    self.contadores["links_em_textos"] += n_links
                    self.contadores["artigos_ancorados"] += n_arts
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
                decisao=decisoes.get(n.id), texto_html=texto_html, n_links=n_links, n_arts=n_arts, versao=versao,
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
                linhas.append([self._link(n.id), html.escape(n.orgao), html.escape(n.ano), html.escape(n.situacao), self._ids_para_links_html(n.situacao_base[:400])])
            blocos.append({"id": chave, "titulo": titulo + " (UFPB)", "texto": texto, "colunas": ["Norma", "Órgão", "Ano", "Situação", "Base"], "linhas": linhas})
        self._render("painel.html", "vigencia/index.html", "../", secao="vigencia", titulo="Quadro de vigência",
                     lead="Situação de cada norma conforme o texto das normas posteriores. As normas federais seguem a anotação do texto compilado do planalto e das notas oficiais do CNE.",
                     resumo=resumo, blocos=blocos)

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
            blocos.append({"id": "registro", "titulo": "Registro de divergências (Rodadas 0 e 1)", "html": '<div class="card" style="max-width:none">' + markdown.markdown(self._ids_para_links_html_md(md), extensions=["tables"]) + "</div>"})
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
        for g, lst in sorted(grupos.items(), key=lambda kv: -len(kv[1])):
            lst.sort(key=lambda n: -b.grau_entrada(n.id))
            linhas = [[self._link(n.id), html.escape(n.status_coleta), _br(b.grau_entrada(n.id)), html.escape((n.ementa or n.obs)[:200])] for n in lst]
            blocos.append({"id": re.sub(r"[^a-z]+", "-", g.lower()), "titulo": g, "colunas": ["Norma", "Situação da coleta", "Citada por", "Descrição / observação"], "linhas": linhas})
        resumo = [("citadas, sem texto", sum(len(v) for v in grupos.values()))] + [(g, len(v)) for g, v in sorted(grupos.items(), key=lambda kv: -len(kv[1]))]
        self._render("painel.html", "fila/index.html", "../", secao="fila", titulo="Fila de coleta",
                     lead="Normas citadas por outras normas do acervo e ainda sem texto. Aparecem tracejadas na Teia. A lista das resoluções dos conselhos superiores é o pedido feito à SODS.",
                     resumo=resumo, blocos=blocos)

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
                titulo = re.sub(r"^#\s*", "", p.read_text(encoding="utf-8").split("\n", 1)[0])
                rel = f"sobre/{p.stem}.html"
                self._raiz_rel = "../"
                self._escrever(rel, self.env.get_template("painel.html").render(raiz="../", meta=self.meta, secao="sobre", titulo=titulo, lead="", resumo=None, blocos=[{"id": "doc", "titulo": "", "html": '<div class="card" style="max-width:none">' + htm + "</div>"}]))
                rodadas.append({"arquivo": f"{p.stem}.html", "titulo": titulo})
        self._render("sobre.html", "sobre/index.html", "../", secao="sobre", niveis=niveis, rodadas=rodadas)

"""Leitura e validação da base (base/nos.csv, base/arestas.csv e anexos)."""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from .rotulos import (
    CHAVE_RELACAO,
    NIVEIS,
    SITUACAO_CHAVE,
    ano_do_id,
    federal,
    rotulo,
)

csv.field_size_limit(10**9)


@dataclass
class Norma:
    id: str
    tipo: str
    orgao: str
    numero: str
    data: str  # AAAA-MM-DD, AAAA ou vazio
    data_sessao: str
    ementa: str
    ementa_sigrh: str
    nivel: str
    temas: list[str]
    situacao: str  # texto da base
    situacao_base: str
    status_coleta: str
    metodo_texto: str
    aviso_texto: str
    fonte: str
    fonte_arquivo: str
    texto_acervo: str
    data_coleta: str
    obs: str
    rotulo: str = ""
    situacao_chave: str = ""
    fantasma: bool = False
    ano: str = ""
    texto_path: Path | None = None

    @property
    def federal(self) -> bool:
        return federal(self.id)

    @property
    def data_norm(self) -> str:
        """Data em AAAA-MM-DD; ano solto vira AAAA-01-01; vazio permanece vazio."""
        d = (self.data or "").strip()
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", d):
            return d
        if re.fullmatch(r"\d{4}", d):
            return d + "-01-01"
        return ""


@dataclass
class Relacao:
    origem: str
    disp_origem: str
    destino: str
    disp_destino: str
    tipo: str
    natureza: str
    inicio_efeito: str
    fim_efeito: str
    ressalva: str
    base: str
    confianca: str
    evidencias: str
    parte: str
    fonte_texto: str
    citacao: str
    trecho: str
    obs: str

    @property
    def chave(self) -> str:
        return CHAVE_RELACAO.get(self.tipo, "M")

    @property
    def sugestao(self) -> bool:
        n = self.natureza or ""
        return n.startswith("sugestão") or n.startswith("não aplicada") or self.base == "inferência"

    @property
    def citacao_simples(self) -> bool:
        return self.tipo == "REMETE A"


@dataclass
class Base:
    raiz: Path
    normas: dict[str, Norma] = field(default_factory=dict)
    relacoes: list[Relacao] = field(default_factory=list)
    decisoes: dict = field(default_factory=dict)
    saida: dict[str, list[Relacao]] = field(default_factory=dict)
    entrada: dict[str, list[Relacao]] = field(default_factory=dict)
    problemas: list[str] = field(default_factory=list)

    # ---- leitura -------------------------------------------------------
    @classmethod
    def carregar(cls, raiz: str | Path) -> "Base":
        raiz = Path(raiz)
        b = cls(raiz=raiz)
        with open(raiz / "base" / "nos.csv", encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                n = Norma(
                    id=r["id"],
                    tipo=r.get("tipo", ""),
                    orgao=r.get("orgao", ""),
                    numero=r.get("numero", ""),
                    data=r.get("data", ""),
                    data_sessao=r.get("data_sessao", ""),
                    ementa=r.get("ementa", ""),
                    ementa_sigrh=r.get("ementa_sigrh", ""),
                    nivel=r.get("nivel", "") or "?",
                    temas=[t.strip() for t in (r.get("temas", "") or "").split(";") if t.strip()],
                    situacao=r.get("situacao", ""),
                    situacao_base=r.get("situacao_base", ""),
                    status_coleta=r.get("status_coleta", ""),
                    metodo_texto=r.get("metodo_texto", ""),
                    aviso_texto=r.get("aviso_texto", ""),
                    fonte=r.get("fonte", ""),
                    fonte_arquivo=r.get("fonte_arquivo", ""),
                    texto_acervo=r.get("texto_acervo", ""),
                    data_coleta=r.get("data_coleta", ""),
                    obs=r.get("obs", ""),
                )
                n.rotulo = rotulo(n.id, n.orgao)
                n.fantasma = not n.status_coleta.startswith("texto")
                n.situacao_chave = SITUACAO_CHAVE.get(n.situacao, "desconhecida")
                if n.fantasma and n.situacao_chave == "desconhecida":
                    n.situacao_chave = "nao_localizada"
                n.ano = n.data[:4] if n.data[:4].isdigit() else ano_do_id(n.id)
                n.texto_path = b._localizar_texto(n)
                if n.id in b.normas:
                    b.problemas.append(f"ID duplicado em nos.csv: {n.id}")
                b.normas[n.id] = n
        with open(raiz / "base" / "arestas.csv", encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                rel = Relacao(**{k: r.get(k, "") for k in Relacao.__dataclass_fields__})
                b.relacoes.append(rel)
        dec = raiz / "base" / "decisoes_vigencia.json"
        if dec.exists():
            b.decisoes = json.loads(dec.read_text(encoding="utf-8"))
        b._indexar()
        b._validar()
        return b

    def _localizar_texto(self, n: Norma) -> Path | None:
        """Caminho do texto integral, se existir no repositório.

        A base registra caminhos antigos (Downloads/Oraculovski/textos/...,
        acervo/textos/...); aqui vale a pasta textos/ do repositório, procurada
        primeiro pelo caminho registrado e depois pelo ID.
        """
        t = n.texto_acervo or ""
        candidatos: list[Path] = []
        if "textos/" in t:
            candidatos.append(self.raiz / ("textos/" + t.split("textos/", 1)[1]))
        for p in candidatos:
            if p.exists():
                return p
        # busca pelo ID (índice preguiçoso)
        idx = self._indice_textos()
        return idx.get(n.id)

    _idx_textos: dict[str, Path] | None = None

    def _indice_textos(self) -> dict[str, Path]:
        if self._idx_textos is None:
            idx: dict[str, Path] = {}
            pasta = self.raiz / "textos"
            if pasta.exists():
                for p in pasta.rglob("*.md"):
                    idx.setdefault(p.stem, p)
            self._idx_textos = idx
        return self._idx_textos

    def _indexar(self) -> None:
        self.saida = {}
        self.entrada = {}
        for rel in self.relacoes:
            if rel.origem not in self.normas or rel.destino not in self.normas:
                continue
            self.saida.setdefault(rel.origem, []).append(rel)
            self.entrada.setdefault(rel.destino, []).append(rel)

    # ---- validação -----------------------------------------------------
    def _validar(self) -> None:
        p = self.problemas
        for rel in self.relacoes:
            if rel.origem not in self.normas:
                p.append(f"aresta com origem ausente: {rel.origem} → {rel.destino}")
            if rel.destino not in self.normas:
                p.append(f"aresta com destino ausente: {rel.origem} → {rel.destino}")
            if rel.tipo not in CHAVE_RELACAO:
                p.append(f"tipo de relação desconhecido: {rel.tipo} ({rel.origem} → {rel.destino})")
        for n in self.normas.values():
            if n.nivel not in NIVEIS:
                p.append(f"nível desconhecido: {n.nivel} em {n.id}")
            if n.situacao not in SITUACAO_CHAVE:
                p.append(f"situação desconhecida: '{n.situacao}' em {n.id}")
            if n.data and not re.fullmatch(r"\d{4}(-\d{2}-\d{2})?|\?", n.data):
                p.append(f"data fora do padrão: '{n.data}' em {n.id}")
            if n.texto_acervo and n.texto_path is None:
                p.append(f"texto registrado na base e ausente em textos/: {n.id} ({n.texto_acervo})")

    # ---- consultas -----------------------------------------------------
    def com_texto(self) -> list[Norma]:
        return [n for n in self.normas.values() if n.texto_path is not None]

    def grau_entrada(self, id_: str) -> int:
        return len(self.entrada.get(id_, []))

    def grau_saida(self, id_: str) -> int:
        return len(self.saida.get(id_, []))

    def resumo(self) -> dict:
        from collections import Counter

        return {
            "normas": len(self.normas),
            "com_texto": sum(1 for n in self.normas.values() if n.texto_path is not None),
            # fila de coleta: sem texto, exceto as alteradoras só anotadas em textos compilados (D90), que ficam fora da fila
            "fantasmas": sum(1 for n in self.normas.values() if n.fantasma and not n.status_coleta.startswith(("alteradora anotada", "fora do escopo"))),
            "fora_fila": sum(1 for n in self.normas.values() if n.fantasma and n.status_coleta.startswith(("alteradora anotada", "fora do escopo"))),
            "relacoes": len(self.relacoes),
            "relacoes_estruturais": sum(1 for r in self.relacoes if not r.citacao_simples),
            "citacoes_simples": sum(1 for r in self.relacoes if r.citacao_simples),
            "por_nivel": dict(Counter(n.nivel for n in self.normas.values())),
            "por_situacao": dict(Counter(n.situacao_chave for n in self.normas.values())),
            "por_tipo": dict(Counter(r.tipo for r in self.relacoes)),
            "problemas": len(self.problemas),
        }

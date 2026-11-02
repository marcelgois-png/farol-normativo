"""Textos coletados das páginas da SODS (Regimento Geral consolidado, anexos do
Regimento dos Órgãos Deliberativos e minuta do novo Estatuto).

As extrações em base/sods/extracoes/ são o "original" desta coleta: texto gerado
no navegador por base/sods/extrator_sods.js a partir do HTML oficial, com hash
conferido. Este módulo só recorta cada extração nas normas que ela contém e
escreve textos/SODS/<ID>.md com cabeçalho YAML. Nada é editado à mão.

    python -m farol sods           # regenera textos/SODS/
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ULTIMA = re.compile(r"\n*Última atualização:[^\n]*\n*$")
SECAO = re.compile(r"^=== (.*) ===$", re.M)

AVISO = (
    "Texto extraído da página oficial da SODS (HTML), sem OCR. Trechos tachados "
    "(~~assim~~) reproduzem a redação revogada ou substituída tal como a página "
    "consolidada a exibe; as notas (*) e (**) são da própria SODS. Em caso de "
    "dúvida, prevalece a publicação oficial."
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _yaml(v) -> str:
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v)
    if s == "" or any(c in s for c in ':#"\'\n') or s.strip() != s or s.lower() in ("yes", "no", "true", "false", "null") or re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def _cabecalho(c: dict) -> str:
    return "---\n" + "\n".join(f"{k}: {_yaml(v)}" for k, v in c.items()) + "\n---\n"


def _sem_rodape(texto: str) -> str:
    return ULTIMA.sub("\n", texto).rstrip("\n") + "\n"


def _secoes(texto: str) -> dict[str, str]:
    """Blocos recolhíveis da página (linhas '=== título ===') → texto de cada um."""
    partes = SECAO.split(texto)
    out: dict[str, str] = {}
    for i in range(1, len(partes), 2):
        out[partes[i].strip()] = partes[i + 1].strip("\n") + "\n"
    return out


def _recorta(texto: str, inicio: str, fim: str | None) -> str:
    a = texto.index(inicio)
    b = texto.index(fim, a + len(inicio)) if fim else len(texto)
    return texto[a:b].strip("\n") + "\n"


def gerar(raiz: Path) -> list[Path]:
    base = raiz / "base" / "sods"
    meta = json.loads((base / "extracoes.json").read_text(encoding="utf-8"))
    pag = {p["url"]: p for p in meta["paginas"]}
    saida = raiz / "textos" / "SODS"
    saida.mkdir(parents=True, exist_ok=True)
    escritos: list[Path] = []

    def carrega(url: str) -> tuple[dict, str]:
        p = pag[url]
        arq = base / p["arquivo"]
        sha = _sha(arq)
        if sha != p["sha256"]:
            raise SystemExit(f"extração {arq} não confere com o hash registrado em extracoes.json")
        return p, arq.read_text(encoding="utf-8")

    def escreve(id_: str, cab: dict, corpo: str, titulo: str, resumo: list[str], contexto: str = "") -> None:
        md = _cabecalho(cab) + f"\n# {titulo}\n\n" + "\n\n".join(resumo) + "\n\n"
        md += f"> **Aviso sobre o texto:** {AVISO}\n\n## Texto integral\n" + corpo
        if contexto:
            md += "\n" + contexto
        out = saida / f"{id_}.md"
        out.write_text(md, encoding="utf-8", newline="\n")
        escritos.append(out)

    def comum(p: dict, id_: str) -> dict:
        return {
            "fonte_oficial": p["url"],
            "atualizacao_pagina": p["atualizacao_pagina"],
            "arquivo_extracao": "base/sods/" + p["arquivo"],
            "sha256": p["sha256"],
            "bytes": p["bytes"],
            "html_sha256": p["html_sha256"],
            "arquivo_local": p["html_arquivo_local"],
            "metodo_texto": "extração do HTML oficial da SODS no navegador (base/sods/extrator_sods.js), conferida por SHA-256",
            "aviso_texto": AVISO,
            "data_coleta": meta["data_coleta"],
        }

    # 1. Regimento Geral consolidado -------------------------------------------
    p, t = carrega("https://www.ufpb.br/sods/regimento-geral/")
    corpo = _sem_rodape(t)
    cab = {
        "id": "UFPB-REGIMENTO-GERAL",
        "tipo": "Regimento",
        "orgao": "CONSUNI (ato de aprovação não indicado no consolidado)",
        "numero": "—",
        "data": "não informada",
        "nivel": "N6",
        "situacao": "alterada e revogada parcialmente",
        "temas": "órgãos colegiados; graduação; pós-graduação; ingresso; pessoal docente; pessoal técnico; representação discente; regime disciplinar",
        "ementa_acervo": "Disciplina os aspectos de organização e funcionamento comuns aos órgãos e serviços da UFPB, complementando o Estatuto (art. 1º).",
        "versao": "consolidado pela SODS, com notas e anotações de alteração; redações revogadas aparecem tachadas",
        **comum(p, "UFPB-REGIMENTO-GERAL"),
    }
    escreve(
        "UFPB-REGIMENTO-GERAL", cab, corpo, "Regimento Geral da UFPB (texto consolidado da SODS)",
        [
            f"**Ementa (resumo do acervo):** {cab['ementa_acervo']}",
            f"**Fonte oficial:** [{p['url']}]({p['url']}) — página atualizada pela SODS em {p['atualizacao_pagina']}.",
            "**Observações:** O consolidado não indica a resolução de aprovação nem a data; ID fixo até localizar o ato. As anotações entre parênteses (Modificado/Redação dada/Revogado pela Resolução…) e as notas (*)/(**) são da SODS. A página liga algumas anotações aos PDFs das resoluções alteradoras; os links estão em base/sods/extracoes/regimento-geral.links.txt.",
        ],
    )

    # 2. Anexos do Regimento dos Órgãos Deliberativos: Res. 147/87 e 82/90 --------
    p, t = carrega("https://www.ufpb.br/sods/regimento-da-sods/")
    t = _sem_rodape(t)
    marca = "SERVIÇO PÚBLICO FEDERAL\n\nUNIVERSIDADE FEDERAL DA PARAÍBA\n\nCONSELHO UNIVERSITÁRIO\n\nRESOLUÇÃO Nº "
    r147 = _recorta(t, marca + "147/87", marca + "82/90")
    r82 = _recorta(t, marca + "82/90", None)
    obs_anexo = ("Texto anexo à página do Regimento dos Órgãos Deliberativos da Administração Superior "
                 "(Res. CONSUNI 279/78) no site da SODS; não localizada no SIGRH.")
    cab = {
        "id": "UFPB-CONSUNI-RES-147-1987", "tipo": "Resolução", "orgao": "CONSUNI", "numero": "147/87",
        "data_assinatura": "1987-11-06", "data_sessao": "não informada", "nivel": "N7",
        "situacao": "sem alteração ou revogação registrada",
        "temas": "órgãos colegiados; eleições e representação",
        "ementa_acervo": "Dispõe sobre a perda de mandato de membros do CONSUNI, CONSEPE e Conselho Curador; revoga os arts. 39 e 42 do Regimento dos Órgãos Deliberativos (Res. 279/78).",
        "versao": "texto anexo ao consolidado da SODS",
        **comum(p, "UFPB-CONSUNI-RES-147-1987"),
    }
    escreve("UFPB-CONSUNI-RES-147-1987", cab, r147, "Resolução CONSUNI nº 147/1987",
            [f"**Ementa (resumo do acervo):** {cab['ementa_acervo']}",
             f"**Fonte oficial:** [{p['url']}]({p['url']}) — página atualizada pela SODS em {p['atualizacao_pagina']}.",
             f"**Observações:** {obs_anexo} Proc. 23074.012.579/87-74; assinada em 06/11/1987."])
    cab = {
        "id": "UFPB-CONSUNI-RES-82-1990", "tipo": "Resolução", "orgao": "CONSUNI", "numero": "82/90",
        "data_assinatura": "1990-12-11", "data_sessao": "1990-10-22", "nivel": "N7",
        "situacao": "sem alteração ou revogação registrada",
        "temas": "órgãos colegiados; eleições e representação",
        "ementa_acervo": "Estabelece normas sobre a perda de mandato de suplentes dos conselheiros dos colegiados superiores.",
        "versao": "texto anexo ao consolidado da SODS",
        **comum(p, "UFPB-CONSUNI-RES-82-1990"),
    }
    escreve("UFPB-CONSUNI-RES-82-1990", cab, r82, "Resolução CONSUNI nº 82/1990",
            [f"**Ementa (resumo do acervo):** {cab['ementa_acervo']}",
             f"**Fonte oficial:** [{p['url']}]({p['url']}) — página atualizada pela SODS em {p['atualizacao_pagina']}.",
             f"**Observações:** {obs_anexo} Deliberação em 22/10/1990 (Proc. 23074.016.419/90-45); assinada em 11/12/1990."])

    # 3. Minuta do novo Estatuto (em tramitação) --------------------------------
    p, t = carrega("https://www.ufpb.br/sods/estatuinte/")
    sec = _secoes(_sem_rodape(t))
    minuta = next(v for k, v in sec.items() if k.startswith("Minuta do Estatuto"))
    contexto = "\n## Contexto (não normativo): demais blocos da página do Processo Estatuinte\n\n"
    for k, v in sec.items():
        if k.startswith("Minuta do Estatuto"):
            continue
        contexto += f"### {k}\n\n{v}\n"
    cab = {
        "id": "UFPB-NT-MINUTA-ESTATUTO-2019", "tipo": "Minuta de Estatuto",
        "orgao": "Congresso Estatuinte / CONSEPE / CONSUNI", "numero": "Proc. 23074.051188/2019-12",
        "data": "2020-03-16", "data_sessao": "não informada", "nivel": "NT", "situacao": "em tramitação",
        "temas": "estatuto; estrutura; órgãos colegiados",
        "ementa_acervo": "Minuta do novo Estatuto (118 artigos), aprovada no CONSEPE (reuniões de 11/10/2019 a 16/03/2020) e em análise no CONSUNI, que reiniciou o exame pelo art. 1º em 30/07/2025.",
        "versao": "minuta publicada na página do Processo Estatuinte",
        **comum(p, "UFPB-NT-MINUTA-ESTATUTO-2019"),
    }
    escreve("UFPB-NT-MINUTA-ESTATUTO-2019", cab, minuta, "Minuta do novo Estatuto da UFPB (norma em tramitação)",
            [f"**Ementa (resumo do acervo):** {cab['ementa_acervo']}",
             f"**Fonte oficial:** [{p['url']}]({p['url']}) — página atualizada pela SODS em {p['atualizacao_pagina']}.",
             "**Observações:** NORMA EM TRAMITAÇÃO — sem força normativa. A numeração de incisos e alíneas vem das listas HTML da página (estilo romano/alfabético). Os demais blocos da página (notícia da retomada em 30/07/2025, relatório da Comissão Geral Estatuinte e calendário das reuniões extraordinárias do CONSUNI em 2025) estão ao final, como contexto."],
            contexto)
    return escritos


if __name__ == "__main__":  # pragma: no cover
    import sys
    for p in gerar(Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()):
        print(p)

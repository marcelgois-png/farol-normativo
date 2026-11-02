from pathlib import Path

import pytest

from farol.base import Base

RAIZ = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def base():
    return Base.carregar(RAIZ)


def test_base_carrega_sem_erros_graves(base):
    graves = [p for p in base.problemas if p.startswith(("ID duplicado", "aresta com", "tipo de relação", "nível desconhecido", "situação desconhecida"))]
    assert graves == []
    r = base.resumo()
    assert r["normas"] > 6000 and r["relacoes"] > 20000


def test_normas_estruturais_presentes(base):
    for i in ["UFPB-CONSUNI-RES-07-2002", "UFPB-CONSUNI-RES-279-1978", "UFPB-CONSUNI-RES-257-1979", "UFPB-REGIMENTO-GERAL", "BR-LEI-9394-1996", "BR-LEI-8112-1990"]:
        assert i in base.normas
    assert base.normas["UFPB-CONSUNI-RES-07-2002"].nivel == "N5"
    assert base.normas["UFPB-REGIMENTO-GERAL"].nivel == "N6"


def test_decisoes_de_vigencia_preservadas(base):
    """As decisões fundamentadas (D44–D73) são casos de teste: a base não pode contrariá-las."""
    dec = {d["norma"]: d["situacao"] for d in base.decisoes.get("situacao", [])}
    assert dec["UFPB-CONSEPE-RES-15-2003"] == "revogada"
    assert base.normas["UFPB-CONSEPE-RES-15-2003"].situacao_chave == "revogada"
    assert base.normas["UFPB-CONSUNI-RES-257-1979"].situacao_chave == "conflito"
    assert base.normas["UFPB-CONSEPE-RES-55-1995"].situacao_chave == "conflito"


def test_relacao_conhecida(base):
    """Res. CONSUNI 21/2020 altera o art. 202 do Regimento Geral (D12)."""
    rels = [r for r in base.saida["UFPB-CONSUNI-RES-21-2020"] if r.destino == "UFPB-REGIMENTO-GERAL" and r.tipo == "ALTERA"]
    assert any(r.disp_destino.startswith("art. 202") for r in rels)
    # CNE/CES 11/2002 revogada pela CNE/CES 2/2019
    rev = [r for r in base.entrada["BR-CNE-CES-RES-11-2002"] if r.tipo == "REVOGA (total)"]
    assert any(r.origem == "BR-CNE-CES-RES-2-2019" for r in rev)


def test_notas_por_artigo_regimento_geral(base):
    from farol.grafo import notas_por_artigo

    notas = notas_por_artigo(base, "UFPB-REGIMENTO-GERAL")
    # D-casos: a Res. CONSUNI 21/2020 altera o art. 202 do Regimento Geral
    assert any(r.origem == "UFPB-CONSUNI-RES-21-2020" and r.tipo == "ALTERA" for r in notas.get("202", []))
    # sugestões nunca entram nas anotações
    assert not any(r.sugestao for lst in notas.values() for r in lst)

from pathlib import Path

from farol.texto import Ligador, ler, reflow, render_html

FIXTURE = Path(__file__).parent / "fixtures" / "norma_exemplo.md"


def test_reflow_junta_linhas_e_separa_unidades():
    corpo = "Art. 1º Esta norma dispõe sobre\nalgo que continua na linha seguinte.\n§ 1º Primeiro parágrafo.\nI\n- primeiro inciso;\nII - segundo inciso.\nArt. 2º Outro artigo."
    paras = reflow(corpo)
    assert paras[0] == "Art. 1º Esta norma dispõe sobre algo que continua na linha seguinte."
    assert paras[1] == "§ 1º Primeiro parágrafo."
    assert paras[2] == "I - primeiro inciso;"
    assert paras[3] == "II - segundo inciso."
    assert paras[4] == "Art. 2º Outro artigo."


def test_render_ancoras_e_links():
    t = ler(FIXTURE)
    assert t.id == "TESTE-RES-1-2000"
    lig = Ligador({"Resolução nº 16/2015": ("UFPB-CONSEPE-RES-16-2015", "art. 294")}, prefixo="../../norma/")
    html, indice = render_html(t, lig)
    assert indice["1"] == "art-1" and indice["2"] == "art-2"
    assert 'id="art-1"' in html and 'id="art-2"' in html
    # artigo repetido (anexo) recebe sufixo
    assert 'id="art-1-2"' in html
    assert lig.contagem == 1
    assert 'href="../../norma/UFPB-CONSEPE-RES-16-2015/#art-294"' in html
    # tachado vira <s>
    assert "<s>redação antiga</s>" in html
    # HTML é escapado
    assert "&lt;script&gt;" in html


def test_ligador_ignora_citacoes_curtas_e_sobreposicao():
    lig = Ligador({"Lei": ("BR-LEI-1-2000", ""), "Lei nº 9.394/1996": ("BR-LEI-9394-1996", "")})
    out = lig.aplicar("conforme a Lei nº 9.394/1996 e a Lei.")
    assert out.count("<a ") == 1
    assert "BR-LEI-9394-1996" in out

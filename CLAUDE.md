# Farol Normativo UFPB

Sistema de consulta ao ecossistema normativo da Universidade Federal da Paraíba: acervo de normas, mapa das relações entre elas (Teia), ficha e texto de cada norma, quadro de vigência e, em etapa posterior, um assistente de perguntas (Oráculo). Nasceu do projeto Oraculovski. Coordenação: Marcel de Gois Pinto (Diretor do Centro de Tecnologia).

Leia `docs/plano.md` antes de propor mudanças de rumo. Este arquivo tem as regras que valem para qualquer tarefa no repositório.

## Estrutura

- `base/` — a base do acervo. `nos.csv` (uma linha por norma), `arestas.csv` (uma linha por relação, com trecho e citação literal), `decisoes_vigencia.json`, `fila_coleta.md`, `quadro_vigencia.*`, `manifesto_originais.tsv` (SHA-256 dos originais), `divergencias/` e `controles/` (resultados das conferências e correções de identificação das rodadas), `sods/` (extrações de texto das páginas da SODS com hash conferido, o extrator usado e `extracoes.json`).
- `textos/` — um Markdown por norma com texto integral, em `textos/<ÓRGÃO>/<ano>/<ID>.md` (UFPB), `textos/<GRUPO>/<ID>.md` (federais, CNE, PB para leis da Paraíba, outros) ou `textos/SODS/<ID>.md` (textos consolidados das páginas da SODS, gerados por `python -m farol sods` a partir de `base/sods/`). Cabeçalho YAML com id, datas, nível, situação, fonte oficial, método de extração e aviso de OCR; depois um resumo e a seção `## Texto integral` (ou `## Texto`).
- `farol/` — o gerador (Python). `base.py` lê e valida; `texto.py` converte o Markdown em HTML com âncoras e links; `grafo.py` deriva dados da Teia, sugestões, dispositivos e as anotações de vigência por artigo (`notas_por_artigo`); `site.py` monta as páginas; `templates/` e `static/` (CSS com os tokens da identidade UFPB, marca `ufpb-lockup.png`, brasão `ufpb-brasao.png`, `favicon.svg`).
- `site/` — saída gerada; não é versionada. Publicada no GitHub Pages pela ação em `.github/workflows/`.
- `docs/` — plano, relatórios das rodadas e material para a SODS.
- `tests/` — testes do gerador (pytest).

## Comandos

```
pip install -r requirements.txt
python -m farol validar            # lê a base e lista problemas (sai com 1 se houver erro grave)
python -m farol gerar              # gera site/ completo (~20 s)
python -m farol gerar --limite-textos 20 --saida /tmp/site   # geração rápida para testes
python -m farol sods               # regenera textos/SODS/ a partir de base/sods/extracoes/
python -m pytest -q
python -m http.server 8000 --directory site   # para abrir o site localmente
```

## Regras do acervo (não negociáveis)

1. **Só fonte oficial.** SIGRH, site da SODS, sig-arq, planalto.gov.br, in.gov.br, gov.br/mec e sites oficiais de órgãos. Resumo de terceiro não é fonte. Cada original tem hash no manifesto.
2. **Nunca alterar um texto em `textos/` à mão.** Textos vêm de extração do original (camada de texto, OCR ou HTML oficial) e são regenerados pelo pipeline. Correção de OCR só com nova extração ou conferência contra o PDF, registrada no cabeçalho.
3. **Nunca inventar número de resolução, artigo ou data.** Se não está na base, a resposta é "não está no acervo" e a norma entra na fila de coleta.
4. **Hierarquia** (nível pelo órgão que editou o ato): N1 Constituição; N2 leis, LC, decretos-lei, MP; N3 decretos; N4 MEC, CNE, CAPES, CGU, outros órgãos federais e conselhos profissionais; N5 Estatuto (Res. CONSUNI 07/2002); N6 Regimento Geral, Regimento dos Órgãos Deliberativos (Res. 279/78) e Regimento da Reitoria (Res. 257/79); N7 resoluções do CONSUNI, CONSEPE e Conselho Curador; N8 regimentos editados pelas próprias unidades; N9 conselhos de centro, departamentos, colegiados e PPGs; N10 Reitoria e pró-reitorias. NT = em tramitação (sem força normativa); MA = material de apoio. Norma inferior não contraria superior; conflito aparente é registrado e explicado, nunca resolvido pelo sistema.
5. **Tipos de relação**, sempre com estes rótulos: FUNDAMENTA-SE EM, REGULAMENTA, ALTERA, REVOGA (total), REVOGA (parcial), SUPERA, REMETE A, DELEGA COMPETÊNCIA, PROPÕE SUBSTITUIR. Cada relação registra origem e dispositivo, destino e dispositivo, data de início de efeito, base (texto, SIGRH, anotação de consolidação, inferência), confiança, trecho e citação literal. Relação inferida (co-citação, acoplamento, alvo provável) tem `natureza` começando por "sugestão" e nunca entra na vigência.
6. **Vigência** é conferida no texto das normas posteriores. Regras: o texto prevalece sobre o registro do SIGRH; norma inferior não altera nem revoga superior; arquivo trocado no SIGRH não gera relação; revogação expressa prevalece sobre alteração posterior (LINDB, art. 2º, § 3º); revogação contradita por atos posteriores ou de assunto distinto vira conflito registrado; decisões fundamentadas ficam em `base/decisoes_vigencia.json`.
7. **IDs**: `UFPB-<ÓRGÃO>-RES-<NÚMERO>-<ANO>` (ex.: UFPB-CONSEPE-RES-29-2020), `BR-LEI-9394-1996`, `BR-DEC-9235-2017`, `BR-CNE-CES-RES-2-2019`, `BR-MEC-PORT-554-2013`. Fixos: `UFPB-REGIMENTO-GERAL`, `UFPB-NT-MINUTA-ESTATUTO-2019`. Nunca renomear um ID sem registrar a reidentificação em `base/divergencias/`.
8. **Toda rodada de coleta** produz relatório em `docs/rodadas/` com: normas coletadas, relações novas, o que ficou na fila, conferência independente por amostra. As divergências D1–D73 e seguintes são casos de teste: uma mudança no gerador ou na base não pode mudar uma decisão registrada sem nova decisão.
9. **O Farol orienta e não decide.** Qualquer texto de interface ou resposta do Oráculo deixa claro que não substitui parecer da Procuradoria Federal junto à UFPB nem a deliberação dos conselhos.

## Convenções de código

- Python 3.10+, sem framework web; dependências em `requirements.txt` (Jinja2, Markdown, PyYAML, pytest).
- Nomes em português, como no acervo. Comentários curtos. Funções puras onde der; o estado fica em `Base`.
- O site é estático: nada no `site/` depende de servidor. JavaScript só o necessário (busca e Teia). Bibliotecas externas apenas de CDN com versão fixa (hoje só d3 7.9.0 na Teia); fontes do Google Fonts (IBM Plex).
- Identidade visual: a do Manual de Identidade Visual da UFPB. Cores só da paleta oficial (azul #284f9e, azul escuro #1e3766, azul claro #92c3eb, amarelo #ffc636, amarelo escuro #ce9c30, laranja #e76d27, cinza #bcbcbc, preto, branco) e seus gradientes; tipografia IBM Plex Sans (oficial), com IBM Plex Serif no texto das normas e Condensed em rótulos; a marca "UFPB" (aplicação preferencial: brasão + "UFPB") fica sempre ao lado do nome do sistema, separada por filete, e não se recorta nem se recolore. Os tokens estão só em `farol/static/farol.css`, que a Teia também carrega (o CSS de `_teia_head.html` é só o do layout dela). A barra de título (`templates/_cabecalho.html`) aparece em todas as páginas, inclusive na Teia. A flor de lis é a oficial, recortada do manual (`static/flor-de-lis.png`).
- Anotações de vigência por artigo: vêm só das relações ALTERA, REVOGA e SUPERA da base (sem sugestões) cujo `disp_destino` cita artigo; aparecem sob o caput e nunca alteram o texto. A redação nova fica na norma alteradora (texto compilado é entrega do estágio 3).
- Tabelas dos painéis: rolagem própria (`.tabela`), cabeçalho fixo e ordenável por qualquer coluna (`static/tabelas.js`); as células nunca cortam palavras nem truncam o conteúdo da base.
- Escopo da fila (D104): só normas da UFPB e normas externas citadas diretamente por elas. Depois de integrar qualquer rodada, rodar `python scripts/escopo.py`, que marca as demais sem texto como "fora do escopo" (cadeia de vigência ou citadas só por normas externas) e devolve à fila as que passarem a ser citadas pela UFPB. Nada sai da base.
- Fila de coleta: além das normas citadas, aceita pedidos da coordenação (os 34 regimentos de unidades, IDs `UFPB-REGIMENTO-<SIGLA>`, nível N8). Regimento aprovado por resolução de conselho superior vira nó com texto em `textos/REGIMENTOS/` (Markdown gerado a partir do texto da resolução, nunca editado à mão), relação FUNDAMENTA-SE EM com o ato de aprovação e situação herdada dele; os ainda não localizados apontam, como sugestão, o ato de criação/estrutura da unidade. A coluna "Vigência registrada no acervo" só repete o que as normas já lidas dizem (relações ALTERA, REVOGA e SUPERA); nunca afirma que uma norma não lida está em vigor.
- Na página de cada norma, os links para outras normas abrem em nova aba; a sigla OCR traz a explicação ao passar o mouse (`abbr_ocr`, `.tip`).
- Mudança em template ou CSS: gerar com `--limite-textos 20`, abrir no navegador, só então gerar o site inteiro.
- Textos de OCR podem ter números trocados; links de citação no texto vêm da coluna `citacao` da base e só são criados quando a citação aponta para uma única norma.

## Pendências conhecidas

- Páginas da SODS (Regimento Geral consolidado, Regimento dos Órgãos Deliberativos com as Res. 147/1987 e 82/1990 anexas, minuta do novo Estatuto): o texto vem do HTML oficial lido no navegador com `base/sods/extrator_sods.js`; a extração é conferida por SHA-256 e guardada em `base/sods/extracoes/`. Para recoletar: abrir a página, rodar o extrator no console, salvar o texto, atualizar `extracoes.json` e rodar `python -m farol sods`. Os HTML completos ficam fora do repositório (`originais/SODS/` no acervo local).
- A Res. CONSUNI 279/78 consolidada da página da SODS não foi convertida em texto (o acervo usa o HTML do SIGRH em `textos/CONSUNI/1978/`); a extração completa da página está em `base/sods/extracoes/regimento-da-sods.txt`.
- 148 resoluções dos conselhos superiores citadas e ausentes do SIGRH: pedido à SODS em `docs/rodadas/pedido_sods_resolucoes_nao_localizadas.md`.
- Pareceres do CNE (`BR-CNE-*-PAR-*`) não têm efeito normativo próprio: relações ALTERA/REVOGA encontradas em seus projetos de resolução anexos ficam como REMETE A (D78).
- Rodada 3 (02/11/2026): relatório em `docs/rodadas/relatorio_rodada3.md`; scripts da coleta e da integração em `scripts/r3/`. Pendentes: regimento da STI (o PDF do site é arquivo errado, D79), atos do CFE e portarias GR/PRG/PROGEP sem fonte on-line.
- O extrator de citações e relações usado nas Rodadas 1 a 4 está em `scripts/extrator.py` (`extrai(texto, id, conselho, inventario)`); os scripts de cada rodada o importam de lá, para que as relações sejam comparáveis entre rodadas.
- Rodada 4 (02/11/2026): relatório em `docs/rodadas/relatorio_rodada4.md`; scripts em `scripts/r4/` (busca no DOU por título em `dou_busca.js`, decisões do bloco C em `decisoes_blocoC.tsv`). O índice pesquisável do DOU (in.gov.br) só tem texto desde 2013: 84 atos do MEC/CAPES anteriores ficam "não localizada em fonte oficial acessível" (D84). Pendente da coordenação: padrão único de ID para instruções normativas e fusão dos duplicados (D87). Dentro de lei estadual, "Lei nº" sem qualificativo é lei do mesmo ente (D85) — regra a incorporar ao extrator.
- Rodada 5 (02/11/2026): relatório em `docs/rodadas/relatorio_rodada5.md`; scripts em `scripts/r5/` (`processa_r5.py` lê as páginas do planalto e da Câmara; `merge_r5.py` integra; decisões de identificação em `decisoes_r5.tsv`). Prioridade da fila pelo número de citações. Regras de revogação em `scripts/r5/regras_r5.py`, aplicadas aos textos da R5 e reaplicadas às Rodadas 2–4 (`correcoes_r5.py`): D92 (citação em artigo "Revogam-se:/Ficam revogados:" é REVOGA parcial ou total; itens que mantêm, ressalvam ou acrescem ficam REMETE A) e D93 ("revoga dispositivos da…" é parcial); revogação com "a partir de <data>" futura fica como revogação programada, sem mudar a situação; D102: relação estrutural com origem anterior ao destino vira REMETE A. Pendente: DLG 143/2002 e 66/1990 no Senado.
- O Oráculo (estágio 2 do plano) exige serviço no servidor; não faz parte do site estático.

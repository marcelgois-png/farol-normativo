# Farol Normativo · Relatório da Rodada 5

Data: 02/11/2026. Critério da rodada: **prioridade pelo número de citações**. Escopo: limpeza da fila e leis, decretos, decretos-lei, medidas provisórias, leis complementares e emendas citados **por normas da UFPB** ou **por duas ou mais normas do acervo**. Originais em `Documents\Oraculovski\originais_r5\FEDERAL` (planalto.gov.br e Câmara dos Deputados), com SHA-256 no manifesto. Scripts em `scripts/r5/`.

## Resumo

| | Antes (Rodada 4) | Depois (Rodada 5) |
|---|---|---|
| Normas na base | 6.401 | 7.772 |
| Normas com texto integral | 3.437 | **3.728** (+291) |
| Relações | 24.855 | 30.203 (+5.359 tiradas dos textos da rodada; +84 revogações e −90 citações simples na reaplicação às rodadas anteriores) |
| Relações estruturais (altera, revoga, regulamenta…) | 7.430 | 9.514 |
| Fila de coleta (sem texto) | 2.964 | 2.833 |
| — citadas por normas da UFPB | 590 | 587 |
| — citadas por 2 ou mais normas | 499 | 678 |
| Alteradoras só anotadas em texto compilado (fora da fila, D90) | — | 1.211 |

**Leitura dos números.** Dos 313 alvos do planalto, só 13 eram citados por resoluções da UFPB — e esses 13 são leis estaduais e municipais (feriados, polos UAB, Escola de Enfermagem), fora da fonte federal. O ganho da rodada foi completar a cadeia federal (Código de Processo Civil de 1973, Código de Processo Penal, LC 123/2006, ação civil pública, FUNDEB de 2007, leis de pessoal e de carreiras). As leis coletadas citam 981 normas que ainda não estavam no acervo, quase todas uma única vez e só por outras leis: elas entram no fim da fila. As 587 normas citadas pela UFPB que restam são resoluções dos conselhos (pedido à SODS), atos do MEC/CAPES anteriores a 2013, normas de unidades e atos de outros órgãos — escopo das Rodadas 6 e 7.

## 1. Limpeza da fila (antes da coleta)

- **D89** — 7 nós residuais de reidentificações da Rodada 2, sem nenhuma relação, removidos.
- **D90** — 885 leis e decretos que só apareciam como alteradoras anotadas nos textos compilados do planalto ("Redação dada pela Lei…") saíram da fila com status próprio. Não são citados por norma alguma; o efeito deles já está no texto compilado do destino. Nesta rodada, mais 410 entraram nessa condição e 83 voltaram à fila porque passaram a ser citados.
- **D91** — padrão único de ID para instruções normativas (`BR-<ÓRGÃO>-IN-<n>-<ano>`) e Ministério do Planejamento sempre `BR-MPOG`; 20 renomeações e fusões (`reidentificacoes_r5.csv`).

## 2. Coleta

- **291 normas com texto**: 265 do planalto (73 na versão compilada) e 26 da Câmara dos Deputados — atos de 1931 a 2011 que o planalto não publica (Decreto 20.158/1931 do ensino comercial, DL 421/1938 do ensino superior, Lei 1.711/1952, antigo Estatuto dos Funcionários, Lei 5.276/1967 dos nutricionistas, Lei 7.177/1983 de escolha de dirigentes de fundações, entre outros). Por tipo: 192 leis, 47 decretos, 28 decretos-lei, 10 medidas provisórias, 7 leis complementares, 6 emendas constitucionais, 1 lei delegada.
- **Ficha conferida contra a epígrafe**: número e ano da epígrafe têm de bater com o ID; 3 páginas que não bateram foram descartadas e as citações reidentificadas (abaixo).
- **Situação pela fonte oficial**: 39 normas da rodada registradas como revogadas pela nota da própria página (ex.: CPC/1973 pela Lei 13.105/2015; Decreto 6.571/2008 pelo Decreto 7.611/2011) ou por estarem integralmente tachadas (D98); 2 como revogadas parcialmente, porque a nota ressalva artigos (Lei 5.988/1973, "excetuando-se o art. 17"; Lei 11.494/2007, FUNDEB, "ressalvando o art. 12"). A Lei 7.834/1989 (revogada e depois revigorada) e o DL 2.425/1988 (rejeitado pelo Congresso) ficam sem situação, com a nota para conferência (D101). Medidas provisórias tachadas ficam sem situação, com a nota "convertida na Lei nº…" ou "sem eficácia".
- **Compilado conferido**: o link "texto compilado" só é usado se a epígrafe dele conferir com a norma; em 4 páginas ele apontava para outra lei e foi usada a página principal (D100).

## 3. Relações

5.361 relações novas: 3.346 REMETE A, 1.303 ALTERA, 612 REVOGA (parcial), 94 REVOGA (total) e 6 REGULAMENTA. Agregadas por par de normas e tipo, com os dispositivos listados e o número de ocorrências, como na Rodada 2. As anotações dos textos compilados ("Redação dada pela Lei…", "Revogado pelo Decreto…") viram relações da alteradora para a norma coletada.

Duas regras novas, ambas aplicadas só aos textos desta rodada:

- **D92 (era a pendência P2/D86)** — citação em item de artigo de revogação ("Revogam-se:", "Ficam revogados:") é REVOGA, não REMETE A: **parcial** quando o item nomeia artigo, parágrafo, inciso, anexo ou "dispositivos"; **total** quando nomeia só a norma. Ficam REMETE A as notas "(Vide…)", as ementas transcritas no item e a norma posterior à revogadora. Também ficam REMETE A a lei alteradora mencionada no item ("com as alterações do Decreto-Lei nº 34", "acrescentado pelo art. 2º"). O artigo de revogação termina no próximo artigo, no fecho ("Brasília, …") ou no primeiro anexo; o dispositivo de destino é o do item inteiro ou a lista que segue "os seguintes dispositivos:". Resultado: 219 revogações parciais e 42 totais que antes sairiam como simples citação.
- **D93** — "revoga dispositivos da Lei X" é revogação parcial (o extrator das Rodadas 1–4 a registrava como total): 26 correções.
- **Revogação com efeito futuro** — a cláusula "Ficam revogados, a partir de 1º de janeiro de 2033:" grava a data de início de efeito. A LC 214/2025 (reforma tributária) programa 73 revogações para 2027 e 2033 (LC 116/2003, DL 406/1968, leis do PIS/Cofins…); elas ficam registradas como **revogação programada**, sem mudar a situação atual das normas.

Efeito em normas que já estavam no acervo: 9 passaram a revogadas pelo texto lido nesta rodada (ex.: Lei 9.317/1996, SIMPLES, revogada pela LC 123/2006, art. 89, a partir de 1º/07/2007; Lei 4.611/1965 pela Lei 9.099/1995) e as demais afetadas pela LC 214/2025 receberam só a nota de revogação programada.

## 4. Citações reidentificadas (`scripts/r5/decisoes_r5.tsv`)

- Sem ano, fundidas com a norma já no acervo: Lei 9.394 (LDB), Lei 12.772/2012, Lei 10.172/2001 (PNE).
- "Lei 13/1992" → **Lei Delegada 13/1992** (coletada).
- Decretos legislativos registrados como decretos: DLG 186/2008 e DLG 6/2020 (já no acervo), DLG 66/1990 e, como provável, **DLG 143/2002** — a citação "DLG 143/2003" da Convenção 169 da OIT aponta para uma outorga de rádio em Recife (D94).
- A Res. CONSUNI 33/2010 escreve "Dec. Lei nº 1.445/76" e "Dec. Lei nº 2.140/84": são decretos-lei, já no acervo.
- "(Vide Decreto nº 2.365, de 1987)" nas páginas do DL 200/1967 e da Lei 5.645/1970 → provável **Decreto-Lei 2.365/1987** (o Decreto 2.365 é de 1997, indulto) (D95).
- Fora da fonte federal: "Decreto 1.633/2022" é decreto municipal de Mamanguape (D97). Não localizada: EC 1/1969 (o planalto publica a EC 1/1992 no endereço padrão). A Lei estadual 6.306 do Hemocentro tem data divergente no SAPL (D96).

## 5. Conferência independente

Um agente que não participou da coleta conferiu 59 itens por amostra, lendo só a base, os textos e os originais, e fez varreduras completas de 393 hashes, das 73 revogações programadas, das 235 relações da regra D92 e das 44 normas marcadas revogadas. Confirmados: números, datas, ementas e SHA-256 das fichas; as revogações programadas da LC 214/2025 (datas de 2027 e 2033 conferidas no caput dos arts. 542 e 543, nenhum destino marcado revogado); as 7 revogações aplicadas a normas antigas; as 11 reidentificações; a integridade (nenhuma relação órfã, nenhum ID antigo remanescente, nenhum ato inferior alterando superior).

Apontou 6 problemas de substância, **todos corrigidos no script e reprocessados antes da publicação**: (1) 4 textos "compilados" que eram de outra lei (Leis 12.998/2014, 13.324/2016, 4.771/1965 e 8.981/1995; 74 relações erradas) — D100; (2) a regra D92 tomava a lei alteradora como alvo ("com as alterações do DL 34", "introduzidas pela Lei 9.065"); (3) "Art. 6º Fica revogado o Decreto 8.977" saía como revogação parcial porque o "Art." do caput contava como dispositivo; (4) Lei 7.834/1989 revigorada; (5) Leis 5.988/1973 e 11.494/2007 com artigo ressalvado; (6) DL 2.425/1988 rejeitado pelo Congresso — D101. Observações de completude também aplicadas: dispositivo de destino completo nas listas ("os seguintes dispositivos:", "…todos da Lei"), prefixo espúrio "Anexo V" retirado do dispositivo de origem quando a citação está antes do fecho. Não aplicadas: datas de efeito escalonadas dentro de incisos já vencidas (ex.: Lei 9.532/1997, art. 82, II); alterações e suspensões listadas nas fichas da Câmara (ex.: Resolução do Senado 86/1986 sobre a Lei 6.686/1979); data e ementa dos DLG 66/1990 e 143/2002 (ainda sem texto); dispositivo de origem do Decreto 7.212/2010 (art. 60 em vez de 617, erro do extrator).

## 6. O que ficou na fila (2.833)

| Grupo | Sem texto | Citadas pela UFPB | Fonte provável |
|---|---|---|---|
| Resoluções dos conselhos superiores | 273 | 266 | pedido à SODS |
| MEC e autarquias | 124 | 81 | DOU (só desde 2013), legin/Câmara, memória do MEC/CAPES |
| Outros federais, conselhos profissionais e estaduais | 179 | 128 | sites dos órgãos |
| Normas de unidades, pró-reitorias e reitoria | 60 | 58 | sites das unidades |
| CNE/CFE/CONAES | 59 | 20 | portal do CNE, biblioteca do INEP |
| Sem órgão identificado | 26 | 21 | identificação pelo contexto |
| Leis e decretos | 2.095 | 13 (estaduais e municipais) | planalto/Câmara; 493 citados 2+ vezes, todos só por normas federais |
| Regimentos de unidades | 17 | (pedido da coordenação) | direções das unidades |

## 7. Correções aprovadas pela coordenação (02/11/2026)

Feitas com `scripts/r5/correcoes_r5.py`, a partir das pendências 1 e 2 deste relatório; cada mudança está listada em `base/controles/correcoes_r5.tsv`.

1. **Regras D92 e D93 reaplicadas aos textos federais das Rodadas 2–4** (432 textos do planalto, Câmara e DOU, 308 do CNE, 70 de outros órgãos e 4 da Paraíba; 225 têm artigo de revogação). Resultado: 84 revogações novas (52 totais, 32 parciais), 90 citações simples retiradas porque eram a própria revogação e 31 revogações totais corrigidas para parciais ("revoga dispositivos da…"). Situação de 57 normas atualizada pelo texto (39 revogadas, 15 revogadas parcialmente, 3 alteradas e revogadas parcialmente); nenhuma tinha decisão fundamentada em `decisoes_vigencia.json`. Na revisão da lista, a regra foi endurecida antes de aplicar: ficam de fora os itens que mantêm ou ressalvam normas ("mantidos em vigor as Leis 6.533 e 6.615", na Lei 9.610/1998; "não alteradas pelas Leis 9.131 e 9.192", no art. 92 da LDB) e os que tratam de acréscimo ("na parte em que acresce…"); a revogação total só vale quando o item nomeia apenas normas.
2. **Relação errada retirada**: Decreto 9.191/2017 → LC 95/1998 (D99). A relação correta, Decreto 9.191 → Decreto 4.176/2002, já estava registrada.
3. **Relações cronologicamente impossíveis** (D102): 8 relações em que a norma anterior "altera" ou "revoga" a posterior (ex.: Lei 5.540/1968 → LDB de 1996; Lei 10.667/2003 → MP 1.042/2021) — anotações de redação ligadas no sentido inverso — rebaixadas a REMETE A, sem efeito na vigência.
4. **"Lei nº 13.241, de 1941"** na página do planalto da Lei 11.196/2005 é a Lei 13.241/2015 (D103).

## 8. Pendências

1. DLG 143/2002 e DLG 66/1990: texto no Senado Federal (legis.senado.leg.br), ainda não coletado.
2. Os cabeçalhos dos textos `.md` das Rodadas 2–4 mostram a situação da época em que foram gerados; a situação atualizada está na base (`nos.csv`) e no site.

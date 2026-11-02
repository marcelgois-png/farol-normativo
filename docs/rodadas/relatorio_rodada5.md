# Farol Normativo · Relatório da Rodada 5

Data: 02/11/2026. Critério da rodada: **prioridade pelo número de citações**. Escopo: limpeza da fila e leis, decretos, decretos-lei, medidas provisórias, leis complementares e emendas citados **por normas da UFPB** ou **por duas ou mais normas do acervo**. Originais em `Documents\Oraculovski\originais_r5\FEDERAL` (planalto.gov.br e Câmara dos Deputados), com SHA-256 no manifesto. Scripts em `scripts/r5/`.

## Resumo

| | Antes (Rodada 4) | Depois (Rodada 5) |
|---|---|---|
| Normas na base | 6.401 | 7.766 |
| Normas com texto integral | 3.437 | **3.728** (+291) |
| Relações | 24.855 | 30.178 (+5.327 tiradas dos textos) |
| Relações estruturais (altera, revoga, regulamenta…) | 7.430 | 9.451 |
| Fila de coleta (sem texto) | 2.964 | 2.827 |
| — citadas por normas da UFPB | 590 | 587 |
| — citadas por 2 ou mais normas | 499 | 688 |
| Alteradoras só anotadas em texto compilado (fora da fila, D90) | — | 1.211 |

**Leitura dos números.** Dos 313 alvos do planalto, só 13 eram citados por resoluções da UFPB — e esses 13 são leis estaduais e municipais (feriados, polos UAB, Escola de Enfermagem), fora da fonte federal. O ganho da rodada foi completar a cadeia federal (Código de Processo Civil de 1973, Código de Processo Penal, LC 123/2006, ação civil pública, FUNDEB de 2007, leis de pessoal e de carreiras). As leis coletadas citam 975 normas que ainda não estavam no acervo, quase todas uma única vez e só por outras leis: elas entram no fim da fila. As 587 normas citadas pela UFPB que restam são resoluções dos conselhos (pedido à SODS), atos do MEC/CAPES anteriores a 2013, normas de unidades e atos de outros órgãos — escopo das Rodadas 6 e 7.

## 1. Limpeza da fila (antes da coleta)

- **D89** — 7 nós residuais de reidentificações da Rodada 2, sem nenhuma relação, removidos.
- **D90** — 885 leis e decretos que só apareciam como alteradoras anotadas nos textos compilados do planalto ("Redação dada pela Lei…") saíram da fila com status próprio. Não são citados por norma alguma; o efeito deles já está no texto compilado do destino. Nesta rodada, mais 409 entraram nessa condição e 83 voltaram à fila porque passaram a ser citados.
- **D91** — padrão único de ID para instruções normativas (`BR-<ÓRGÃO>-IN-<n>-<ano>`) e Ministério do Planejamento sempre `BR-MPOG`; 20 renomeações e fusões (`reidentificacoes_r5.csv`).

## 2. Coleta

- **291 normas com texto**: 265 do planalto (73 na versão compilada) e 26 da Câmara dos Deputados — atos de 1931 a 2011 que o planalto não publica (Decreto 20.158/1931 do ensino comercial, DL 421/1938 do ensino superior, Lei 1.711/1952, antigo Estatuto dos Funcionários, Lei 5.276/1967 dos nutricionistas, Lei 7.177/1983 de escolha de dirigentes de fundações, entre outros). Por tipo: 192 leis, 47 decretos, 28 decretos-lei, 10 medidas provisórias, 7 leis complementares, 6 emendas constitucionais, 1 lei delegada.
- **Ficha conferida contra a epígrafe**: número e ano da epígrafe têm de bater com o ID; 3 páginas que não bateram foram descartadas e as citações reidentificadas (abaixo).
- **Situação pela fonte oficial**: 44 normas da rodada registradas como revogadas pela nota da própria página (ex.: CPC/1973 pela Lei 13.105/2015; Decreto 6.571/2008 pelo Decreto 7.611/2011; Lei 11.494/2007, FUNDEB, pela Lei 14.113/2020) ou por estarem integralmente tachadas (D98). Medidas provisórias tachadas ficam sem situação, com a nota "convertida na Lei nº…" ou "sem eficácia".

## 3. Relações

5.327 relações novas: 3.305 REMETE A, 1.310 ALTERA, 619 REVOGA (parcial), 87 REVOGA (total) e 6 REGULAMENTA. Agregadas por par de normas e tipo, com os dispositivos listados e o número de ocorrências, como na Rodada 2. As anotações dos textos compilados ("Redação dada pela Lei…", "Revogado pelo Decreto…") viram relações da alteradora para a norma coletada.

Duas regras novas, ambas aplicadas só aos textos desta rodada:

- **D92 (era a pendência P2/D86)** — citação em item de artigo de revogação ("Revogam-se:", "Ficam revogados:") é REVOGA, não REMETE A: **parcial** quando o item nomeia artigo, parágrafo, inciso, anexo ou "dispositivos"; **total** quando nomeia só a norma. Ficam REMETE A as notas "(Vide…)", as ementas transcritas no item e a norma posterior à revogadora. O artigo de revogação termina no próximo artigo, no fecho ("Brasília, …") ou no primeiro anexo. Resultado: 222 revogações parciais e 35 totais que antes sairiam como simples citação.
- **D93** — "revoga dispositivos da Lei X" é revogação parcial (o extrator das Rodadas 1–4 a registrava como total): 26 correções.
- **Revogação com efeito futuro** — a cláusula "Ficam revogados, a partir de 1º de janeiro de 2033:" grava a data de início de efeito. A LC 214/2025 (reforma tributária) programa 73 revogações para 2027 e 2033 (LC 116/2003, DL 406/1968, leis do PIS/Cofins…); elas ficam registradas como **revogação programada**, sem mudar a situação atual das normas.

Efeito em normas que já estavam no acervo: 13 passaram a revogadas pelo texto lido nesta rodada (ex.: Lei 9.317/1996, SIMPLES, revogada pela LC 123/2006, art. 89, a partir de 1º/07/2007; Lei 4.611/1965 pela Lei 9.099/1995) e 32 receberam a nota de revogação programada.

## 4. Citações reidentificadas (`scripts/r5/decisoes_r5.tsv`)

- Sem ano, fundidas com a norma já no acervo: Lei 9.394 (LDB), Lei 12.772/2012, Lei 10.172/2001 (PNE).
- "Lei 13/1992" → **Lei Delegada 13/1992** (coletada).
- Decretos legislativos registrados como decretos: DLG 186/2008 e DLG 6/2020 (já no acervo), DLG 66/1990 e, como provável, **DLG 143/2002** — a citação "DLG 143/2003" da Convenção 169 da OIT aponta para uma outorga de rádio em Recife (D94).
- A Res. CONSUNI 33/2010 escreve "Dec. Lei nº 1.445/76" e "Dec. Lei nº 2.140/84": são decretos-lei, já no acervo.
- "(Vide Decreto nº 2.365, de 1987)" nas páginas do DL 200/1967 e da Lei 5.645/1970 → provável **Decreto-Lei 2.365/1987** (o Decreto 2.365 é de 1997, indulto) (D95).
- Fora da fonte federal: "Decreto 1.633/2022" é decreto municipal de Mamanguape (D97). Não localizada: EC 1/1969 (o planalto publica a EC 1/1992 no endereço padrão). A Lei estadual 6.306 do Hemocentro tem data divergente no SAPL (D96).

## 5. Conferência independente

(preenchida após a conferência)

## 6. O que ficou na fila (2.827)

| Grupo | Sem texto | Citadas pela UFPB | Fonte provável |
|---|---|---|---|
| Resoluções dos conselhos superiores | 273 | 266 | pedido à SODS |
| MEC e autarquias | 124 | 81 | DOU (só desde 2013), legin/Câmara, memória do MEC/CAPES |
| Outros federais, conselhos profissionais e estaduais | 179 | 128 | sites dos órgãos |
| Normas de unidades, pró-reitorias e reitoria | 60 | 58 | sites das unidades |
| CNE/CFE/CONAES | 59 | 20 | portal do CNE, biblioteca do INEP |
| Sem órgão identificado | 26 | 21 | identificação pelo contexto |
| Leis e decretos | 2.089 | 13 (estaduais e municipais) | planalto/Câmara; 493 citados 2+ vezes, todos só por normas federais |
| Regimentos de unidades | 17 | (pedido da coordenação) | direções das unidades |

## 7. Pendências para decisão

1. Reaplicar as regras D92 e D93 aos textos federais das Rodadas 2–4 (mudaria relações já registradas; precisa de decisão por ser caso de teste).
2. Corrigir a relação antiga REVOGA (total) Decreto 9.191/2017 → LC 95/1998 (Rodada 2, nota do Decreto 4.176/2002 mal ligada; D99).
3. DLG 143/2002 e DLG 66/1990: texto no Senado Federal (legis.senado.leg.br), ainda não coletado.

# Farol Normativo · Relatório da Rodada 4: atos do MEC e autarquias no DOU, leis da Paraíba e identificação de citações sem órgão

**Data:** 02/11/2026 · **Escopo combinado:** (A) os 168 atos do MEC, CAPES, CNPq, Ministério do Planejamento e outros órgãos federais citados por resoluções da UFPB e ainda sem texto, procurados no Diário Oficial da União (in.gov.br) e no gov.br; (B) as leis estaduais da Paraíba citadas, procuradas no SAPL da Assembleia Legislativa (sapl.al.pb.leg.br); (C) identificação, pelo contexto da citação, dos 168 nós cujo órgão não estava identificado (`BR-?-`, `BR-IN-?-`, `OUTRO-`). Coleta pelo navegador (Claude in Chrome) com gravação direta em `Documents\Oraculovski\originais_r4` e manifesto SHA-256 por site; os domínios oficiais seguem bloqueados para o ambiente em nuvem.

## Números da rodada

| Item | Quantidade |
|---|---|
| Atos coletados com texto integral | **52** |
| — Portarias e portarias normativas do MEC (inclusive SETEC e SERES) | 33 |
| — Portarias da CAPES | 11 |
| — CNPq (1), CGU (1), Ministério da Saúde (1), Orientação Normativa SEGRT/MP (1) | 4 |
| — Leis estaduais da Paraíba (SAPL/ALPB) | 4 |
| Normas com texto integral no acervo (Rodadas 0 a 4) | 3.437 (eram 3.385) |
| Nós / relações na base | 6.401 / 24.855 (eram 6.414 / 24.582) |
| Relações tiradas dos textos da Rodada 4 | 278 (ALTERA 6, REVOGA total 14, REVOGA parcial 2, REGULAMENTA 1, FUNDAMENTA-SE EM 93, REMETE A 162), já com as correções da conferência |
| Citações reidentificadas (órgão, número ou ente errados; IDs duplicados fundidos) | 168 arestas, 161 IDs antigos (`base/divergencias/reidentificacoes_r4.csv`) |
| Nós removidos por reidentificação ou por não serem norma | 157; 93 nós novos criados por reidentificação (atos agora com órgão identificado, ainda sem texto) |
| Atos marcados "não localizada em fonte oficial acessível (Rodada 4)" | 118 (84 anteriores a 2013, 25 ausentes do índice do DOU, 9 com homônimo de outro órgão) |
| Situações de vigência atualizadas por texto lido nesta rodada | 21 (revogações totais e parciais, alterações e complementos) |
| Fila de coleta após a rodada | 2.964 normas sem texto (eram 3.029) |

## A. MEC e autarquias no DOU (168 na fila)

- **48 textos coletados** no portal da Imprensa Nacional (in.gov.br), pela busca por título ("PORTARIA Nº n" no campo título, com intervalo de datas), gravando a página HTML oficial de cada ato (`.texto-dou`). Entre eles: as portarias do MEC sobre regulação e supervisão (PN 21/2013 e-MEC, PN 22 e 13/2016, PN 9 e 11/2017, PN 23/2017 consolidada, 1.428/2018 EaD, PN 2.117/2019 carga horária EaD, 554/2013 e 554/2019), a cadeia pandêmica do MEC (343→345→376→473→544→1.030→1.038/2020, 882/2020), as portarias de reconhecimento de cursos de 2018 (1.348 a 1.351, 1.403, 1.035, 1.210), as portarias da CAPES sobre bolsas e avaliação (10/2013, 183/2016 e 249/2018, 15, 131 e 214/2017, 256/2018, 36/2020, 302/2022, 290 e 291/2024), a Portaria MEC 389/2013 (Bolsa Permanência), as portarias de inclusão e acessibilidade do MEC e a Portaria CGU 1.196/2017 (apuração de infrações disciplinares), a Portaria CNPq 2.014/2024 e a ON SEGRT 2/2016 (estágio probatório).
- **Relações estruturais lidas:** CAPES 302/2022 revoga 262/2018; MEC 1.428/2018 revoga 1.134/2016; PN 2.117/2019 revoga 1.428/2018; MEC 514/2024 revoga 413/2016; MEC 612/2024 revoga 375/2024; PN 23/2017, art. 105, revoga as PN 40/2007, 24/2012, 19/2016, 23/2016 e 10/2017; MEC 383/2020 revoga 374/2020; MS 913/2022 revoga 188/2020; PN 11/2017 revoga dispositivos da PN 40/2007 e a PN 18/2016 por inteiro (D86); MEC 1.038/2020 altera 544/2020 e 1.030/2020; MEC 345/2020 altera 343/2020; CAPES 249/2018 regulamenta o art. 7º da 183/2016. Todas aplicadas à situação do destino.
- **Textos com aviso:** o HTML do DOU junta palavras nas quebras de linha; as fichas trazem `aviso_texto` e o cabeçalho do `.md` repete o aviso. Nenhum texto foi editado à mão.
- **Não localizados (118):** o índice pesquisável do DOU só tem texto a partir de 2013, e nem o gov.br/mec nem o gov.br/capes publicam os atos antigos em página localizável — ficam de fora 84 atos anteriores a 2013 (ex.: Portaria CNPq PO-085/2011, PN MEC 18/2012, PN 40/2007, Portaria MEC 4.059/2004) (D84). Outros 25 (2013 em diante) não foram encontrados pela busca por título; 9 buscas devolveram apenas ato homônimo de outro órgão ou com data divergente da citada, descartado após conferência (D82). Três citações eram IDs duplicados de atos já na base: "Resolução MEC 7/2018" = Res. CNE/CES 7/2018; "Portaria SERES 389/2013" = Portaria MEC 389/2013; "Portaria MEC 17/2016" = Portaria SETEC 17/2016 (D83).

## B. Leis da Paraíba (SAPL/ALPB)

- **4 leis coletadas** (PDF oficial do SAPL): Lei 1.366/1955 (cria a Universidade da Paraíba), Lei 1.070/1954, Lei 6.308/1996 (Política Estadual de Recursos Hídricos) e Lei 10.601/2015 (feriado de 5 de agosto). As duas leis dos anos 1950 são digitalizações e foram lidas por OCR (aviso no cabeçalho). Ficam em `textos/PB/`, nível N2 (lei), ente "Paraíba".
- **Reidentificações:** "Lei 6.908/96" é a Lei estadual 6.308/1996 (D80); "Lei 1.366/1955", registrada como federal, é a lei estadual já cadastrada (D81). A Lei 875/1953 (Escola de Auxiliares de Enfermagem) não consta do SAPL em 1953–1954; segue na fila.
- **Correção de método:** dentro de lei estadual, "Lei nº" sem qualificativo é lei do mesmo ente; o extrator havia apontado as Leis 3.936/1977, 5.404/1991 e 5.583/1992 (art. 29 da Lei 6.308/1996) para IDs federais — corrigidas para PB-LEI (D85). "Revogam-se as disposições do art. 2º da Lei 3.489/1967" (Lei 10.601/2015) passou de REMETE A para REVOGA (parcial).

## C. Citações sem órgão identificado (168)

- Um agente independente leu só o contexto das citações (`blocoC_contexto.txt`) e as ementas das resoluções citantes, sem internet, e decidiu caso a caso (`scripts/r4/decisoes_blocoC.tsv`, com fundamento e grau de confiança): **143 reidentificadas** (110 com confiança alta, 33 média), **22 indeterminadas** (mantidas como estão) e **3 que são autorreferências** (a própria resolução citante ou seus anexos), descartadas.
- Das 143, 53 apontam para nós já existentes (ex.: "Portaria 36/2020" = CAPES 36/2020; "Resolução 7/2002" citada pelo Parecer CNE/CES 112/2002 = Estatuto da UFPB; "IN 1/2016" = IN MP/CGU 1/2016; "Resoluções 1/1999, 10/1999, 13/2000, 14/2000, 14/2001 e 43/2002" = resoluções do CONSEPE sobre o PSS) e 90 criam nós novos com órgão identificado e sem texto (ex.: IN TCU 71/2012, Portaria SERES 1.347/2017, portarias do Ministério do Turismo do Cadastur citadas pela Res. CONSUNI 08/2018, portarias GM/MS citadas por PPCs da saúde, INs do MAPA citadas por PPCs de Zootecnia e Agroecologia, portarias de centros e da ETS).
- Achados a decidir pela coordenação, sem alteração nesta rodada (D87): IDs duplicados do mesmo ato (IN SGP 90/2021 em três grafias; IN CGU 3/2017 em duas) e padrão inconsistente para instruções normativas (`BR-IN-<ÓRGÃO>` × `BR-<ÓRGÃO>-IN`) e para o Ministério do Planejamento (`BR-MPOG` × `BR-MP`).

## Conferência independente por amostra

Um agente que não participou da coleta conferiu 41 itens lendo só a base, os textos e os insumos da rodada: 10 reidentificações (todas compatíveis com o trecho citado e com a ficha do destino), as 18 relações estruturais com origem nos atos coletados, 6 fichas (número, data, ementa, fonte e SHA-256 iguais ao texto e ao manifesto), as regras (nenhuma sugestão com tipo estrutural; nenhuma norma inferior alterando superior; os 118 "não localizados" seguem na fila) e a integridade (todo nó referido existe; nenhum ID antigo como destino; nenhum texto curto). Apontou 7 problemas de substância, todos corrigidos em `scripts/r4/conferencia_r4.py` e conferidos no texto: (1) o dispositivo da PN MEC 11/2017 que revoga a PN 18/2016 é o art. 32, não o 13, e a revogação parcial da PN 40/2007 pelo mesmo artigo não tinha sido registrada; (2) o art. 105 da PN 23/2017 revoga também as PN 24/2012, 19/2016, 23/2016 e 10/2017, que estavam como REMETE A a nós sem órgão; a PN 40/2007 tinha dois IDs, fundidos; (3) a Portaria MEC 374/2020 não estava marcada revogada; (4) na Lei PB 10.601/2015 a cláusula revogadora é o art. 2º (o OCR leu "Art. r") e o destino passou a "revogada parcialmente"; (5) a Lei PB 1.366/1955, art. 24, revoga a Lei PB 1.070/1954 — o OCR degradado ("Arte 2h2") impediu a extração; a relação foi registrada depois da leitura da página 7 do PDF oficial; (6) oito nós "BR-?-" criados por citações dentro de portarias do MEC: seis identificados como atos do próprio MEC (dois eram duplicatas de nós existentes) e dois mantidos com a justificativa da indeterminação na ficha; (7) um nó antigo remanescente de reidentificação do bloco C (BR-?-PORT-270-2021) removido. Observações de completude aplicadas: `inicio_efeito` preenchido nas relações estruturais da rodada; confiança "alta" nas revogações expressas; leis estaduais todas em N2; tipo, órgão e número preenchidos nos nós criados por citação; uma sugestão redundante (1.038/2020 → 544/2020, agora confirmada no texto) retirada; 132 linhas repetidas do manifesto (textos da Rodada 3 acrescentados mais de uma vez) removidas. Não aplicadas, por decisão da coordenação: as ementas do DOU com palavras unidas (o aviso fica na ficha) e o padrão de ID das instruções normativas (D87).

## O que ficou na fila (2.964)

- 273 resoluções dos conselhos superiores (pedido à SODS, inalterado);
- 117 atos do MEC e autarquias (dos quais 118 marcados "não localizada em fonte oficial acessível"); 61 do CNE/CFE/CONAES; 177 de outros órgãos federais, conselhos profissionais e órgãos estaduais; 23 sem órgão identificado (eram 147);
- 2.224 leis e decretos (quase todos citados só por normas federais; os citados por resoluções da UFPB que faltam são estaduais e municipais);
- 60 normas de unidades, pró-reitorias e reitoria e 17 regimentos de unidades.

## Divergências novas

D80 a D88 em `base/divergencias/registro_divergencias.md`: Lei 6.908/96 → Lei estadual 6.308/1996; leis estaduais registradas como federais; homônimos de outros órgãos no DOU; atos citados com órgão errado (CNE/CES 7/2018, MEC 389/2013, SETEC 17/2016); atos do MEC e da CAPES anteriores a 2013 sem fonte on-line; citação de lei dentro de lei estadual; art. 32 da PN MEC 11/2017; IDs duplicados; "Portaria 34/2013" e "CONSEE 16/2015".

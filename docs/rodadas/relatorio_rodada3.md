# Farol Normativo · Relatório da Rodada 3: leis e decretos citados, atos do CNE, regimentos de unidades e normas das pró-reitorias

**Data:** 02/11/2026 · **Escopo combinado:** (1) leis e decretos citados por resoluções da UFPB e ainda sem texto (58); (2) atos do CNE/CFE/CONAES na fila (104); (3) regimentos das 34 unidades listadas no site oficial da UFPB (pedido da coordenação); (4) normas de unidades, pró-reitorias e reitoria citadas (52). Coleta feita pelo navegador (Claude in Chrome) com gravação direta em `Documents\Oraculovski\originais_r3` e manifesto SHA-256 por site; os domínios oficiais seguem bloqueados para o ambiente em nuvem e para o shell do computador, o que obrigou a essa rota.

## Números da rodada

| Item | Quantidade |
|---|---|
| Atos coletados com texto integral | **92** |
| — Leis e decretos (Portal da Legislação da Câmara dos Deputados; planalto não os publica) | 25 |
| — Resoluções e pareceres do CNE (gov.br/mec) | 60 (36 pareceres, 24 resoluções) |
| — Portarias de pró-reitorias (PRAPE 2, PRPG 5) | 7 |
| Regimentos de unidades localizados como anexo de resolução já no acervo (`textos/REGIMENTOS/`) | **17** de 34 |
| Normas com texto integral no acervo (Rodadas 0 a 3) | 3.384 (eram 3.281) |
| Nós / relações na base | 6.414 / 24.581 (eram 6.333 / 23.798) |
| Relações tiradas dos textos da Rodada 3 | 759 (ALTERA 12, REVOGA total 16, REVOGA parcial 2, REGULAMENTA 3, FUNDAMENTA-SE EM 169, REMETE A 557) + 17 relações regimento → ato de aprovação + 10 sugestões regimento → ato de estrutura |
| Citações reidentificadas (número, ano ou câmara errados; IDs sem ano fundidos) | 129 arestas, 86 IDs antigos (`base/divergencias/reidentificacoes_r3.csv`) |
| Nós removidos por reidentificação ou por não serem norma | 87 |
| Situações de vigência atualizadas por texto lido nesta rodada | 15 |
| Fila de coleta após a rodada | 3.030 normas sem texto (eram 3.058) |

## 1. Leis e decretos (58 citados)

- **25 textos coletados** na Câmara dos Deputados (publicação original; "Dados da Norma" com situação e vide). Entre eles, a cadeia estatutária da UFPB que faltava: Decreto 50.148/1961 (Estatuto da Universidade da Paraíba, federalizada pela Lei 3.835/60), Decreto 65.464/1969 (Estatuto da UFPB), Decreto 73.701/1974 (plano de reestruturação), Decreto 30.236/1951 (reconhecimento do curso de Ciências Econômicas), Decreto 83.103/1979 (reconhecimento de Psicologia), Lei 4.881-A/1965 (Estatuto do Magistério Superior), Decreto 76.119/1975 (livre-docência), Decretos 87.497/1982 e 89.467/1984 (estágio), Decreto 53.558/1964 (colégios agrícolas, Vidal de Negreiros). Os decretos que aprovam estatutos trazem só o ato de aprovação; o texto do estatuto "que com este baixa" foi publicado à parte no DOU e não está no portal — registrado na ficha.
- **Erros de citação corrigidos** (todos conferidos pelo contexto e pela data citada): Lei 5.962/71 → 5.692/71; Lei 10.630/2003 → 10.639/2003; Decreto 53.358/64 → 53.558/64; Decreto 80.467/84 → 89.467/84; Decreto 87.497/92 → 87.497/82; Decreto 79.239 → 79.329/77; Decreto 15.596/1911 → 15.596/1922; Lei 10.257/2012 → 10.257/2001; Lei 1.044/69 e "Decreto 200/66" → Decretos-Leis 1.044/69 e 200/67; "Lei 8.079" e "Lei 9.500" (citadas pela CLT e pela Lei do Serviço Militar) → Decretos-Leis 8.079/45 e 9.500/46; prováveis: Lei 9.892/2000 → 9.985/2000 (SNUC) e Decreto 5.285/2011 → 5.825/2006 (PCCTAE). 29 IDs sem ano (ex.: BR-LEI-13105-?) foram fundidos com a norma já no acervo.
- **15 citações são leis ou decretos estaduais e municipais** (Paraíba: Lei 875/1953 da Escola de Auxiliares de Enfermagem, Lei 1.366/1955 que cria a Universidade da Paraíba, Lei 6.908/96 e Lei 6.306/91; municípios de João Pessoa, Santa Rita, Rio Tinto e Mamanguape: feriados). Ficam na fila com status próprio; a fonte oficial é a Assembleia Legislativa ou a Câmara Municipal, fora do escopo federal desta rodada.
- **3 citações não são normas** (PEC da federalização da educação citada como "Lei 155/2013"; "12/2017" é a Coletânea de Legislação Arquivística; PL 425/2003 de Gastronomia) e saíram da fila.

## 2. CNE/CFE/CONAES (104 na fila)

- **60 atos coletados** no gov.br/mec, a partir de um índice completo das páginas de resoluções (CES, CEB, CP, 1996–2026) e de pareceres (1996–2009 e 2020), gravado em `originais_r3/_indices/`. Dois PDFs com tabela de referências danificada foram lidos com pypdf; os demais, por pdftotext.
- **33 citações sem câmara ou com câmara errada** foram resolvidas pela data, pelo assunto e pela câmara mencionada no trecho (ex.: "Resolução CNE/CES 2/2015" sobre licenciaturas é a CNE/CP 2/2015; "CNE/CP 4/99" sobre educação profissional técnica é a CNE/CEB 4/99; "CNE/CNS 2/2019" é a CNE/CES 2/2019). Todas apontam para atos já no acervo.
- **Pareceres não têm efeito normativo próprio.** O extrator encontrou cláusulas de alteração e revogação nos projetos de resolução anexos aos pareceres; essas relações foram rebaixadas para REMETE A, com a explicação na coluna obs. As notas oficiais no cabeçalho dos PDFs ("PARECER REVOGADO PELA RESOLUÇÃO…", "PARECER HOMOLOGADO, despacho publicado no DOU de…") foram registradas na ficha.
- **Achado para a UFPB:** o Parecer CNE/CES 112/2002 é a aprovação das alterações do Estatuto da UFPB (base da Portaria MEC 3.198/2002) — peça que faltava na cadeia Estatuto → homologação.
- **Não localizados (21 do CFE + 6):** os atos do extinto Conselho Federal de Educação (1969–1993), citados 44 vezes, não estão em fonte oficial on-line (fonte: *Documenta*/DOU; pedir à SODS ou à Biblioteca Central); Pareceres CES 776/97, 908/98 e 617/99 e Resolução CES 4/98 não constam do índice do MEC; a Resolução CONAES 1/2010 (NDE) não está no gov.br/mec; "Resolução CNE/CES 214/2008" e "CNE/CP 266/2010" não existem com esses números (prováveis confusões com os Pareceres CES 213/2008 e 266/2010, registradas como divergência).

## 3. Regimentos de unidades (34)

- **17 localizados como anexo de resolução do CONSUNI já coletada no SIGRH**: PRA (08/2024), PRG (20/2019), PROPLAN (16/2017), SCS (33/2025), SEBTT (35/2018), SEAD (24/2019), CCM (11/2009), CCSA (01/2025), CT (14/2014), CCS (25/2025), CCJ (02/2015), CCTA (04/2024), CEAR (28/2012), CI (22/2014), CPT-ETS (14/2024), CCHLA (07/2025), CCAE (02/2026). Cada regimento tem nó N8 com número, data e situação herdados do ato de aprovação, relação FUNDAMENTA-SE EM com a resolução e Markdown gerado a partir do mesmo original (`textos/REGIMENTOS/`). O texto inclui a resolução inteira (preâmbulo, art. 1º e anexo), não só o anexo.
- **17 sem regimento próprio localizado** nos sites das unidades nem nas ementas do SIGRH. Para 10 deles a ficha aponta, como sugestão, o ato de criação ou estrutura que vale enquanto o regimento não aparece: PROGEP (CONSUNI 28/2010), PRAPE (29/2010), PRPG e PROPESQ (Títulos IX e IX-A do Regimento da Reitoria, redação da CONSUNI 01/2017), STI (40/2013; o site publica um "Regimento STI" de 2024 sem ato de aprovação — a coletar), SOF (42/2018), SINFRA (03/2019), SULT (41/2018), SSG (39/2018), SSI (40/2018). Sem nenhum ato localizado: PROEX, CCEN, CE, CBIOTEC, CTDR, CCA, CCHSA — perguntar às direções.

## 4. Normas de unidades, pró-reitorias e reitoria (52)

- **7 coletadas** nos sites das pró-reitorias: PRAPE 09/2019 (apoio a eventos; PDF parcialmente digitalizado, OCR nas páginas 1–9) e 02/2021 (CAAE); PRPG 02/2021, 06/2021, 08/2021 e 09/2021 (retificação da 08) e 02/2022, que formam a cadeia pandêmica da pós-graduação (02/2021 revoga a 54/2020; 06/2021 revoga a 02/2021; 08/2021 altera a 06/2021; 02/2022 revoga a 06/2021). A "Resolução PRPG 79/2013" citada é a Res. CONSEPE 79/2013 republicada pela PRPG (reidentificada).
- **Não localizadas (45):** as portarias da PRG (13), da PROGEP (3) e da Reitoria (10) não estão nos sites (a PRG remete ao SIGRH; as portarias GR saem só no Boletim de Serviço/SIPAC); resoluções de centros e colegiados (CCGB/CCS, CAVN, CBCMD, CCD, CCHSA/COC, CSEB/CCAE) exigem visita a cada site. A Resolução CI 02/2013 está publicada como página HTML no site do CI e será gravada assim que o site for autorizado no navegador.

## 5. Conferência independente por amostra

Um agente que não participou da coleta conferiu 30 itens lendo só a base e os textos: 10 reidentificações (todas compatíveis com o contexto citado), 8 relações estruturais (todas confirmadas no dispositivo citado, com a situação do destino atualizada), a regra dos pareceres (565 arestas com origem em parecer, nenhuma estrutural), 4 regimentos (ementa correta e texto idêntico ao da resolução, byte a byte) e 4 fichas (data e ementa iguais ao cabeçalho do texto). Nenhum erro de substância; quatro observações de completude foram aplicadas (situação de normas já alteradas passa a listar também a alteração lida nesta rodada; sugestões de estrutura nomeiam a resolução; nome da PRA corrigido; ressalva de transição do art. 42 da Res. CNE/CEB 2/2024 registrada na relação).

## 6. O que ficou na fila (3.030)

- 272 resoluções dos conselhos superiores (pedido à SODS, inalterado);
- 148 atos do MEC e autarquias; 50 do CNE/CFE/CONAES (dos quais 21 do CFE); 144 de outros órgãos; 147 sem órgão identificado;
- 2.205 leis e decretos, dos quais só 18 citados por resoluções da UFPB (15 estaduais/municipais e 3 sem localização);
- 49 normas de unidades e 17 regimentos de unidades.

## Divergências novas

Registradas em `base/divergencias/registro_divergencias.md` (D74 a D78): "Pareceres CNE/CP 2/2020" citado por três resoluções do CONSEPE sobre a pandemia, quando o Parecer CNE/CP 2/2020 publicado trata de recurso de credenciamento; "Resolução CNE/CES 214/2008" e "CNE/CP 266/2010" inexistentes; data do Decreto 53.558/64 citada como a de publicação; decretos que aprovam estatutos sem o texto do estatuto no portal.

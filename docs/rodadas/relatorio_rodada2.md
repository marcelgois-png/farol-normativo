# Oraculovski · Relatório da Rodada 2: atos federais citados pelas resoluções (CNE em primeiro lugar) e correção de identificações

**Data:** 20/10/2026 · **Escopo combinado:** passos (c) a (e) do método, aplicados à fila deixada pela Rodada 1. Prioridade para o que muda vigência ou fundamentação das resoluções da UFPB: atos do CNE e do MEC, leis e decretos citados sem ano e normas de outros órgãos citadas várias vezes. Ficaram de fora as 2.085 leis e decretos citados só por outras normas federais.

## Números da rodada

| Item | Quantidade |
|---|---|
| Atos coletados com texto integral | **318** |
| — Resoluções do CNE (gov.br/MEC: todas as publicadas nas páginas de resoluções; 5 recentes pelo DOU) | 253 |
| — Leis e decretos (planalto.gov.br; Decreto 14.118/1920 pela Câmara dos Deputados) | 24 |
| — Outros órgãos: MS (9), CNS (6), Cofen (6), CGU (3), MTE/MTb (3), MEC/SERES/CAPES/INEP pelo DOU (10), CAPES, MTur, ME, MEC/MS | 41 |
| Materiais de apoio do CNE baixados (ofícios e comunicados, categoria MA) | 4 |
| Normas com texto integral no acervo (Rodadas 0 a 2) | 3.271 |
| Nós / relações na base | 6.333 / 23.798 (eram 6.003 / 21.075) |
| Relações tiradas dos atos da Rodada 2 | 2.745 (ALTERA 102, REVOGA total 106, REVOGA parcial 23, REGULAMENTA 11, FUNDAMENTA-SE EM 777, REMETE A 1.726) |
| Citações reidentificadas na base da Rodada 1 | 408 |
| Nós removidos por reidentificação (eram a mesma norma com ID errado ou não eram norma) | 119 |
| Atos do CNE citados por resoluções da UFPB, agora com texto | 103 |

**Situação dos 253 atos do CNE:**
- 164 sem alteração ou revogação registrada;
- 74 revogados;
- 13 alterados;
- 1 alterado e revogado em parte;
- 1 revogado em parte.

As revogações vêm do texto das normas revogadoras e das notas oficiais de consolidação que o CNE publica no próprio texto ("(**) Revogada pela Resolução…").

## Correções na base da Rodada 1

1. **42 "resoluções do CONSEPE/CONSUNI não localizadas" eram de outros órgãos.** Exemplos:
   - Resolução 466/2012 (CNS, ética em pesquisa), 196/1996 e 510/2016 (CNS);
   - 20 resoluções do Conselho Federal de Biomedicina listadas no PPC de Biomedicina;
   - Confea 218/1973, 447/2000 e 1.010/2005; CFN 333/2004 e 600/2018; CNJ 433/2021; CEE 188/1998;
   - resoluções de outras universidades (UFRN, UFT).

   A lista de resoluções dos conselhos superiores realmente não localizadas caiu para **151**, das quais 148 são citadas por outras normas. Ver `pedido_sods_resolucoes_nao_localizadas.md`.
2. **Câmara do CNE identificada.** Muitos textos da UFPB citam "Resolução CNE nº X" sem a câmara. A câmara (CES, CEB ou CP) foi identificada pela data citada, pela câmara mencionada no trecho ou pelo assunto. 13 citações traziam a câmara errada no próprio texto da UFPB (ex.: "CNE/CES" para a CNE/CP 1/2004, Relações Étnico-Raciais) e foram corrigidas pela data.
3. **Erros de número ou ano nos textos da UFPB:**
   - "Resolução 9.394/96" é a LDB;
   - "Lei 10.793, de 2 de dezembro de 2004" é a Lei 10.973/2004 (Inovação);
   - "Lei 11.645/05" é de 2008;
   - "Projeto de Lei 1627" e "Projeto de Lei nº 425" não são normas e foram retirados da fila.
4. **Atos de outros órgãos com órgão identificado:** Cofen 564/2017 (estava duplicada), MS 2.528/2006, 1.823/2012 e 3.088/2011, Portaria MTb 3.214/1978 (NRs), CGU 2.737/2017, MTur 27/2014, entre outros.

## Achados que mudam respostas do Oraculovski

1. **DCN de Engenharia revogada e ainda citada.** A CNE/CES 11/2002 foi revogada pela CNE/CES 2/2019 e continua citada por 23 resoluções da UFPB. Entre elas estão os atos de criação e os PPCs das engenharias do **Centro de Tecnologia**:
   - Civil e Mecânica (2006);
   - Elétrica, Materiais, Química, Ambiental e Produção (2008);
   - Alimentos (2009).

   O novo PPC de Engenharia Química (CONSEPE 04/2026) já cita a DCN de 2019, mas ainda chama o art. 5º da DCN de 2002 de "exigência legal".
2. **Fundamento em ato do CNE revogado: 27 casos**, quase todos posteriores à resolução da UFPB:
   - Res. CONSEPE de Direito (CES 9/2004 → CES 5/2018);
   - formação de professores (CP 2/2015 → CP 2/2019);
   - Arquitetura (CES 2/2010 → CES 1/2025);
   - Medicina (CES 3/2014 → CES 3/2025);
   - revalidação de diplomas (CES 1/2002 → CES 3/2016).

   Ver `divergencias_r2.csv`.
3. **Citações com número que não corresponde ao assunto: 16 alertas.** Exemplos:
   - PPCs de Comunicação Social citam a CES 17/2002, que é a DCN de Ciências Sociais; a de Comunicação Social é a CES 16/2002;
   - os cursos de Química do CCA citam a CES 11/2002 (Engenharia) em vez da CES 8/2002;
   - um PPC de Psicologia cita a CNE/CP 1/2023 (Pedagogia da Alternância).

   Nesses casos a base registra a norma provável como sugestão e não gera divergência de vigência.
4. **Revogações que o SIGRH não informa, agora visíveis por norma federal:**
   - CES 1/2007 (especializações): revogada pela CES 1/2018, alterada pelas CES 4/2018 e 4/2021;
   - CES 1/2001 (pós-graduação): revogada pela CES 7/2017;
   - CEB 4/1999 e CEB 6/2012 (educação profissional técnica): revogadas pela CEB 6/2012 e pela CNE/CP 1/2021.
5. **Planalto:**
   - Decreto 5.707/2006 (política de desenvolvimento de pessoal), citado no Plano de Capacitação: revogado pelo Decreto 9.991/2019;
   - Decreto 5.622/2005 (EaD): revogado pelo Decreto 9.057/2017;
   - Lei 5.540/1968 (Reforma Universitária): revogada pela LDB, segundo a página do planalto;
   - Decreto 7.611/2011 (educação especial): revogado pelo Decreto 12.686/2025.

## Conferência independente

Um agente que não participou da construção conferiu 65 itens nos textos oficiais (intervalos de Wilson a 95%):

| Tipo | Itens | Corretos | Parcialmente corretos | Incorretos | Inconclusivos |
|---|---|---|---|---|---|
| Relações ALTERA/REVOGA de atos do CNE | 25 | 22 (88%; IC 70–96%) | 3 | 0 | 0 |
| Reidentificações | 20 | 19 (95%; IC 76–99%) | 0 | 0 | 1 |
| Situação de vigência de atos do CNE | 12 | 8 | 0 | 4 | 0 |
| Divergências novas | 8 | 3 | 4 | 1 | 0 |

Nenhuma relação estrutural estava com o tipo errado. Os três itens parciais tinham dispositivo genérico ou supressão de inciso registrada como alteração.

**Correções aplicadas depois da conferência:**
- leitor de notas aceitando "n.º" e notas sem câmara (CES 2/1997, 4/1997 e 5/1997 e CEB 4/1999 passaram a constar como revogadas);
- revogação por lista em anexo (CES 11/2006);
- "revogadas … em especial a Resolução X" e "permanecerá em vigor até…" tratados como revogação (CEB 6/2012 → CEB 4/1999; CEB 3/2018 → CEB 2/2012, com efeito diferido);
- "fica suprimido" tratado como revogação parcial;
- nota de consolidação absorvida pela relação equivalente tirada do texto da norma alteradora, que tem dispositivo;
- câmara corrigida pela data citada;
- conferência de assunto antes de gerar divergência de vigência.

## Limites conhecidos

- **Portarias do MEC e da CAPES anteriores a 2018 não têm fonte oficial acessível:** o portal.mec.gov.br não responde, e a busca do DOU só cobre atos recentes. Ficaram sem texto as PN MEC 18/2012, 21/2012 e 40/2007 e as Portarias CAPES 68/2004, 174/2014 e 13/2006, entre outras. A ficha de cada uma traz a identificação e a descrição não oficial, marcada como tal.
- A Portaria CNPq PO-085/2011, citada 93 vezes, não está publicada em fonte oficial on-line. O site do CNPq só traz o relatório da comissão.
- Pareceres do CNE (por exemplo, CNE/CP 5/2020, 8 citações) não foram coletados.
- Resoluções do CNE de 2024 a 2026 estão no acervo só quando localizadas no DOU (5). As demais aparecem pelas notas de revogação nas normas antigas.
- Os 16 alertas de citação são heurísticos; um deles (CONSEPE 29/2023) parece falso positivo.

## Onde está cada coisa

**Pasta do projeto (`acervo/`):**
- `base/nos.csv`, `base/arestas.csv` e `base/citacoes.csv`, atualizados;
- `rodada2/relatorio_rodada2.md`;
- `rodada2/divergencias_r2.csv`;
- `rodada2/reidentificacoes_r2.csv`;
- `rodada2/pedido_sods_resolucoes_nao_localizadas.md`.

**Computador (`Documents\Oraculovski`):**
- `originais_r2\`: arquivos oficiais da rodada, com manifestos (URL, tamanho e SHA-256);
- `_texto_r2\`: texto extraído;
- `textos\CNE\` e `textos\OUTROS\`: um Markdown por ato (ficha, relações e texto integral);
- `base_r2\`: base completa (nós, arestas com trecho, divergências, reidentificações, controles, fontes e scripts).

## Fila para a próxima rodada

| Grupo | Sem texto | Citados por resoluções da UFPB |
|---|---|---|
| Resoluções dos conselhos superiores não localizadas | 151 | 148 (pedido à SODS) |
| Outras normas de conselhos da UFPB ainda citadas | 123 | 119 |
| MEC e autarquias (portarias anteriores a 2018, sobretudo) | 132 | 103 |
| Órgão não identificado ou outra instituição | 152 | 121 |
| Outros órgãos federais, conselhos profissionais e estaduais | 114 | 88 |
| Normas de unidades, pró-reitorias e reitoria da UFPB | 54 | 51 |
| Leis e decretos | 2.232 | 58 |
| CNE/CFE (pareceres, CFE e atos de 2024–2026) | 104 | 40 |

> O Oraculovski orienta e não substitui parecer da Procuradoria Federal junto à UFPB nem a deliberação dos órgãos competentes.

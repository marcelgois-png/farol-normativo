# Oraculovski · Relatório da Rodada 1 — texto integral do SIGRH e normas federais citadas (versão final, após 3 conferências)

**Data:** 18/10/2026 · **Escopo:** passos (b) a (d) do método — todas as resoluções do CONSEPE, CONSUNI e Conselho Curador publicadas no SIGRH, lidas na íntegra, com extração de todas as normas citadas e coleta das leis e decretos federais citados (planalto.gov.br).

## Números da rodada

| Item | Quantidade |
|---|---|
| Arquivos do SIGRH baixados e conferidos (SHA-256) | 2.614 (6,4 GB) |
| Resoluções distintas (após duplicidades e correções de número) | 2608 |
| Texto pela camada de texto do PDF | 1550 |
| Texto por OCR integral (Tesseract, 300 dpi) | 822 |
| PDFs mistos (texto + OCR de páginas escaneadas) | 29 |
| HTML / DOCX | 198 / 2 |
| Texto parcial (PDF truncado no SIGRH) / sem texto (arquivo defeituoso) | 11 / 2 |
| Normas federais coletadas no planalto.gov.br | 359 (de 405 citadas; 41 não localizadas ou com citação errada) |
| Nós no acervo (todas as normas, inclusive citadas) | 6003 |
| Relações (arestas) | 21075 |
| — que envolvem norma da UFPB | 16639 |
| — ALTERA / REVOGA total / REVOGA parcial (UFPB) | 703 / 554 / 57 |
| — FUNDAMENTA-SE EM / REMETE A (UFPB) | 2762 / 12542 |
| Divergências automáticas | 836 |

## Situação das resoluções dos conselhos superiores

| Situação | Quantidade |
|---|---|
| sem alteração ou revogação registrada | 2070 |
| revogada | 437 |
| não localizada | 193 |
| alterada | 186 |
| alterada e revogada parcialmente | 19 |
| revogada parcialmente | 5 |
| a verificar (arquivo do SIGRH com texto de outra norma) | 4 |
| conflito de vigência (ver divergências) | 4 |

"Não localizada": citada por outras resoluções, mas ausente do SIGRH. A maioria é anterior a 1992 (D28). "A verificar": o arquivo do SIGRH é o texto de outra norma (D52).

## Coleta desta rodada (regra 9 do projeto)

- **Normas coletadas:** 2608 resoluções dos conselhos superiores, com texto integral, e 359 leis, decretos e outros atos federais (planalto.gov.br). Com o Regimento Geral e a minuta do novo Estatuto (Rodada 0), o acervo tem texto integral de 2969 normas.
- **Relações registradas:** 21075 no total (eram 396 ao fim da Rodada 0), das quais 3274 de alteração ou revogação e 67 sugestões (inferidas, fora da vigência).
- **Fila:** 3032 normas citadas e ainda sem texto (detalhe em `fila_coleta.md`).

## Regras de vigência aplicadas

1. O texto da norma prevalece sobre o registro do SIGRH; o registro só entra na vigência se o texto o confirma ou se o texto da norma de origem não pôde ser lido.
2. Norma inferior não altera nem revoga norma superior: uma resolução que "revoga" lei vira simples citação (bloqueio hierárquico).
3. Arquivo do SIGRH com texto de outra norma (documento trocado) não gera relações para a norma cadastrada.
4. A revogação expressa prevalece; a alteração posterior de norma revogada não a restabelece (LINDB, art. 2º, § 3º), salvo repristinação expressa ("restabelece a vigência").
5. Revogação contradita por atos posteriores, ou de assunto distinto, fica registrada como conflito e não é resolvida pela base, salvo decisão fundamentada na leitura dos textos (`decisoes_vigencia.json`).
6. O ato que está dentro de uma "nova redação" transcrita pertence à norma que recebe a redação, com efeito a partir da norma alteradora. Relações inferidas ou mencionadas por terceiros são sugestões.

## Conferências independentes

Três conferências feitas por agentes que não participaram da construção da base, lendo os textos oficiais. Intervalos de confiança de 95% pelo método de Wilson.

**1ª conferência (105 itens, base inicial)**

- Precisão das relações ALTERA/REVOGA (tipo e alvo): 59/60 = 98,3% (IC95 91,1–99,7%); com dispositivos razoáveis: 48/60.
- Revogações integrais confirmadas no texto da revogadora: 14/15 = 93,3% (1 era parcial).
- Citações registradas só como REMETE A que deveriam ser ALTERA/REVOGA: 6/20 = 30,0%; com perda real do par: 2/20 = 10,0%.
- Normas sem revogação expressa no acervo: nenhuma perda por citação expressa (0/10).
- *Correções aplicadas:* particípio de revogação com expressão intercalada (a CONSEPE 16/2015 passou a revogar 35 resoluções), revogação parcial lida como total (Regimento da Reitoria × CONSUNI 03/2000), órgão atribuído por omissão, "Regimento Geral" genérico, ementas não detectadas e passivas descritivas.

**2ª conferência (82 itens, base corrigida)**

- Precisão das relações estruturais: 29/30 = 96,7% (IC95 83,3–99,4%); o único erro era um ato contido em nova redação transcrita.
- Falso negativo em REMETE A: 3/20 = 15,0%, sem nenhum par sem ALTERA/REVOGA (perda real 0/20).
- Alertas de vigência que procedem: 8/12 = 66,7%; revogações integrais confirmadas: 10/10.
- Perda por citação numérica: 0/10; incluindo ato por nome, sem número: 1/10 (CONSUNI 02/2026 → Regimento do CCAE).
- *Correções aplicadas:* nova redação transcrita atribuída à norma que a recebe; ementa de outra norma em lista de legislação ou bibliografia deixou de ser ato; "Revoguem-se", "ficando revogados os artigos da", "Alterar a redação da … e seus anexos", "RESOLUÇÂO" sem "Nº"; TABELA I e II (OCR); passiva com dispositivo intercalado; efeitos no tempo (retroação, vigência temporária, repristinação); ressalva de ultratividade; bloqueio hierárquico; documentos trocados; ementas erradas do SIGRH; registros errados do SIGRH; decisões fundamentadas (LINDB, art. 2º, § 3º).

**3ª conferência (64 itens, base final antes das últimas correções)**

- Relações estruturais corretas: 24/25 = 96,0% (IC95 80,5–99,3%); sem nenhuma ressalva: 14/25 (as ressalvas são de dispositivo genérico, data incompleta ou aresta duplicada).
- Citações reclassificadas como não sendo ato da norma (nova redação transcrita, lista de legislação, oração relativa): 9/10 corretas.
- Situação de vigência correta: 9/10; relações e situações juntas: 42/45 = 93,3% (IC95 82,1–97,7%), com erro grave em 3/45.
- Alertas de controle que procedem: 16/19 = 84,2% (documento trocado 4/4; ementa do SIGRH 3/4; revogação de norma já revogada 9/11).
- *Correções aplicadas:* artigos próprios da norma separados dos artigos de texto transcrito (inclusive nova redação sem aspas e renumeração "a seguir:"); blocos entre aspas; verbo dentro de oração relativa que descreve outra norma; cláusula de resguardo não é revogação; verbo de ato coordenado ("e revogar a", "e dar nova redação"); anotação de lei ou portaria transcrita não altera resolução; nota "(Revogado pela...)" na redação antiga vira alteração; datas por extenso em formatos variados; início de efeito na data da sessão quando a norma vigora "na data de sua aprovação"; vigência diferida e regime de transição; revogação por remissão genérica às normas modificadoras; ementa absorvida pelo artigo; relação indireta tirada de considerando (sugestão); ementa × artigo divergentes; alvo trocado 05/2011 → 48-A/2010 e 49/1999 → 51/1995.

## Controles novos desta versão

- Documentos trocados no SIGRH detectados: 4 (CONSEPE 02/1987 contém o texto de CONSEPE 02/1981; CONSUNI 12/2017 contém o texto de CONSEPE 12/2017; CONSEPE 01/2021 contém o texto de CONSUNI 01/2021; CONSUNI 01/2000 contém o texto de CONSEPE 01/2000). 19 relações desses textos deixaram de ser atribuídas às normas cadastradas (D52).
- Ementas cadastradas no SIGRH substituídas pela ementa do texto: 3 (D54).
- Registros do SIGRH excluídos por decisão fundamentada: 2 (D53).
- Relações derivadas (texto de terceiros) que repetiam relação direta, absorvidas: 32.
- Decisões de vigência fundamentadas: 7 normas; sugestões de alvo provável: 10; aresta por identificação manual: 1.
- Relações da Rodada 0 absorvidas pela relação equivalente do texto: 32; relações da ementa absorvidas pelo artigo correspondente: 475; notas "(Revogado pela…)" na redação antiga reclassificadas como alteração: 7.
- Revogações declaradas só na ementa, anotadas com a ressalva de técnica legislativa: 145 (D67). Revogações por remissão genérica às normas modificadoras: 1 (D70). Relação suspensa por erro material reconhecido: 1 (D60). Bloqueios hierárquicos: 1.
- Descrições de resoluções não localizadas tiradas das normas que as citam (marcadas como não oficiais): 79.
- Alertas de triagem: revogação de norma já revogada com possível alvo trocado (9, D59); revogação redundante (12); título, cabeçalho ou órgão divergente do cadastro (20, D58); ementa e artigo da mesma norma revogando normas diferentes (1, D60).

## Achados que mudam respostas do Oraculovski

1. **O SIGRH não basta para saber o que está vigente.** O texto das resoluções registra 399 pares de alteração ou revogação que o SIGRH não anota (D32). Há registros do SIGRH contrariados pelo texto (D33, D53), arquivos trocados (D52) e ementas cadastradas erradas (D54).
2. **Conflitos de vigência (4), não resolvidos.** Regimento da Reitoria (CONSUNI 257/79, D47); Creche-Escola (CONSEPE 55/95, D44); PPC de Gestão em Saúde EAD (CONSEPE 12/2025, revogada por provável erro de número, D48); criação do curso de Antropologia e Culturas Indígenas (CONSEPE 35/2006, D50).
3. **Revogação expressa prevalece sobre alteração posterior.** A CONSEPE 15/2003 (PSS) e a CONSEPE 03/96 (Enfermagem) seguem revogadas, embora normas posteriores as "alterem" (D45, D46).
4. **Efeitos no tempo.** A CONSEPE 09/90 foi repristinada pela 62/2007 (D55). As alterações das CONSEPE 11/2000 e 29/2001 eram temporárias e já se exauriram. Há resoluções com efeitos retroativos, como a CONSEPE 50/2014, cujos efeitos retroagem a 31/10/2014 (D56).
5. **Resoluções fundamentadas em norma federal revogada (27).** Em parte dos casos, a norma já estava revogada quando a resolução foi editada (D41).
6. **Lei 9.192/1995 (lista tríplice) segue em vigor.** A MP 914/2019 perdeu a eficácia (D43).
7. **Regimentos substituídos sem revogação expressa do anterior.** A CONSUNI 14/2014 aprova novo Regimento do Centro de Tecnologia sem revogar o de 2008 (CONSUNI 01/2008); o mesmo ocorre com a CPPD (CONSUNI 20/2020 × 02/1995) e com o CCAE (CONSUNI 02/2026 × 19/2017, D57). A base registra a substituição tácita como sugestão (LINDB, art. 2º, § 1º), sem aplicá-la à vigência. No caso do CT, a CONSUNI 26/2014 ainda alterou o regimento de 2008 depois do novo regimento, para renomear o Departamento de Arquitetura e Urbanismo (D73).

## Limites conhecidos

- Regimentos de centros e órgãos alterados só pelo nome, sem número, ainda não estão mapeados, salvo o do CCAE (D57).
- Textos por OCR podem ter números trocados; o cabeçalho de cada texto indica o método e o PDF oficial deve ser conferido para citação formal (D39).
- Atos do MEC, CNE e CAPES (N4) e as 308 resoluções ausentes do SIGRH estão na fila; a vigência de normas que dependem deles pode mudar.
- Dispositivos de destino ainda genéricos em parte das relações ("norma inteira" ou "dispositivos indicados no trecho") e números citados sem ano (ex.: "Resolução Nº 48-A") não são ligados; nesses casos, o trecho guardado em cada relação permite a conferência.
- O Oraculovski orienta e não substitui parecer da Procuradoria Federal junto à UFPB nem a deliberação dos órgãos competentes.

## Onde está cada coisa

- **Pasta do projeto (acervo/):** `base/nos.csv`, `base/arestas.csv`, `base/citacoes.csv` (versão compacta); `quadro_vigencia.md`; `registro_divergencias.md`; `fila_coleta.md`; `rodada1/relatorio_rodada1.md`.
- **Computador (Downloads\Oraculovski):**
  - `originais\` — 2.614 arquivos oficiais do SIGRH, com `manifesto_originais.tsv` (link sig-arq, tamanho e SHA-256);
  - `originais_federais\` — páginas oficiais do planalto, com o manifesto;
  - `textos\` — um Markdown por norma: ficha, relações e texto integral (CONSEPE, CONSUNI, CURADOR e FEDERAL);
  - `base_completa\` — nós e arestas com trecho, divergências, quadro de vigência, decisões de vigência, controles e os scripts usados.

## Fila para a próxima rodada

- Leis, decretos e emendas federais citados só por normas federais (2º nível): 2085
- Resoluções dos conselhos superiores ausentes do SIGRH: 308
- Atos do MEC, CNE, CAPES e órgãos federais (N4): 265
- Outros órgãos federais e conselhos profissionais: 239
- Leis, decretos e emendas federais citados pelas resoluções: 69
- Normas de unidades, pró-reitorias e reitoria da UFPB (N9/N10): 50
- Órgão não identificado: 12
- Normas estaduais: 3
- Estatuto anterior a 2002: 1

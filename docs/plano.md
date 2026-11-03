# Farol Normativo UFPB · Plano da aplicação (v1, 01/11/2026)

**Nome (decidido em 01/11/2026):** Farol Normativo UFPB; forma curta "Farol". A metáfora orienta sem conduzir, como o sistema orienta sem decidir, e remete ao Farol do Cabo Branco. "Oraculovski" permanece como nome do projeto de origem e do assistente de perguntas (o Oráculo). Componentes: Farol (sistema), Teia (mapa de citações), Ficha, Acervo (textos ligados), Oráculo (assistente). Endereço pretendido: farol.ufpb.br (a pedir à STI); repositório: farol-normativo.

## 1. O que a aplicação é

Um sistema público de consulta ao ecossistema normativo da UFPB, com quatro faces sobre uma mesma base:

1. **Teia**: o mapa de citações, com norma de partida, vigência, máquina do tempo e filtros (já existe como protótipo em artefato).
2. **Ficha**: metadados, situação de vigência e sua base, relações por dispositivo, divergências, link oficial.
3. **Ecossistema**: o texto integral de cada norma com cada citação transformada em link, artigos ancorados, avisos de alteração e revogação ao lado do dispositivo e a lista de quem cita.
4. **Oráculo**: resposta a perguntas em linguagem comum, no formato do item 7 do projeto (resposta, base normativa, cadeia, instância, pontos de atenção, mudança em discussão, fontes). Explica como o assunto é regido e por quem; não decide casos nem resolve conflitos, que remete à Procuradoria e aos conselhos.

Mais duas faces internas, para quem mantém o acervo: o **quadro de vigência, divergências e fila de coleta** (hoje em Markdown e CSV) e o **painel de rodadas** (o que foi coletado, conferido e publicado em cada rodada).

Princípios que já valem no projeto e passam para a aplicação: só fonte oficial; a relação registra trecho, dispositivo e data de efeito; vigência conferida no texto da norma posterior, não no SIGRH; sugestão nunca é relação normativa; o sistema orienta e não substitui parecer da Procuradoria nem deliberação dos conselhos.

Argumento institucional: o Decreto 10.139/2019 obriga os órgãos federais a revisar e consolidar seus atos normativos inferiores a decreto. A UTFPR fez isso à mão com 1.900 atos. O Oraculovski é a ferramenta para a UFPB fazer o mesmo com rastreabilidade.

## 2. Estágios

### Estágio 1 · Site estático gerado pela base (sem servidor de aplicação)

Entrega: Teia, ficha, ecossistema, busca e os painéis internos, como arquivos estáticos gerados por script a partir do repositório da base. Publicação no GitHub Pages de início; migração para servidor da UFPB quando houver.

- Repositório `oraculovski` com três partes: `base/` (nós, arestas, citações com trecho, dispositivos, divergências, decisões, fila, manifestos SHA-256 dos originais), `textos/` (um Markdown por norma, com o cabeçalho padronizado), `gerador/` (Python) e `site/` (saída).
- Gerador: lê a base, valida (IDs, datas, hierarquia, relações sem nó), monta as páginas e os dados JSON (uma vizinhança por norma, grafo compacto para a Teia, índice de busca) e publica.
- Ecossistema: conversão do Markdown em HTML; links de citação inseridos a partir dos trechos registrados na base (a detecção já foi feita na Rodada 1, não se refaz); âncoras de artigo e parágrafo onde a detecção for consistente; textos de OCR marcados e com link para o PDF oficial; avisos por dispositivo ("art. 206, § 1º: alterado pela Res. CONSUNI 21/2020").
- Busca: índice pré-construído no próprio site (sem servidor), com os critérios da busca avançada atual mais o texto integral.
- Teia: o código atual do grafo, lendo vizinhanças por norma em vez de carregar tudo; passa a ter "abrir texto" e, no leitor, "ver na Teia".
- Endereços estáveis por norma (`/norma/UFPB-CONSEPE-RES-29-2020`) e por dispositivo (`#art-12`), para citar em ofícios e pareceres.

### Estágio 2 · Serviço no servidor: oráculo e colaboração

Entrega: API pequena (Python) na frente do mesmo site, com banco de dados, índice vetorial e chamada a um modelo de linguagem.

- Oráculo com recuperação em duas camadas: primeiro o grafo (identifica a norma pelo número, órgão ou tema, segue vigência e relações), depois os trechos do texto; o modelo responde só a partir do que foi recuperado, cita norma e artigo, diz quando a norma não está no acervo e recusa inventar número ou data.
- Avaliação antes de abrir: conjunto de 50 a 100 perguntas reais (SODS, coordenações, PRG, PRPG, PROGEP) com resposta de referência; meta de acerto definida com a SODS; registro de cada resposta e do trecho usado, para auditoria.
- Colaboração: coleções compartilhadas, registro de divergência pela comunidade com triagem da SODS, pedido de coleta de norma ausente.
- Atualização: rotina que lê o SIGRH, detecta resoluções novas e abre a fila da rodada seguinte, com extração de citações e proposta de relações para conferência humana.

### Estágio 3 · Consolidação e institucionalização

- Texto compilado (redação vigente de cada artigo, com histórico), começando pelo Estatuto e pelos três regimentos comuns, que a SODS já consolida à mão.
- Domínio e hospedagem da UFPB, curadoria formal da SODS, integração com o SIGRH como fonte primária e papel definido para a Procuradoria.
- Quadro comparativo Estatuto vigente × minuta, artigo a artigo (produto previsto no projeto).

## 3. Arquitetura (estágio 1 e base do 2)

| Camada | Escolha | Por quê |
|---|---|---|
| Base de dados do acervo | arquivos versionados (CSV/JSON) + SQLite gerado pelo script | auditável linha a linha, sem servidor, vira Postgres no estágio 2 sem mudar o modelo |
| Gerador | Python | os scripts do acervo já são Python (`build_r0.py`, `integra_sigrh.py`, `monta_textos.py`, base completa) |
| Site | HTML/CSS/JS sem framework pesado; d3 para o grafo | é o que a Teia já usa; carrega rápido; qualquer pessoa mantém |
| Busca | índice estático pré-construído (tipo Pagefind ou MiniSearch) | busca no navegador, sem servidor, inclusive no texto integral |
| Hospedagem | GitHub Pages → servidor UFPB | custo zero agora; migração é copiar a pasta `site/` |
| Estágio 2 | FastAPI + Postgres (com índice vetorial) + API de modelo de linguagem | padrão simples, hospedável na STI ou em nuvem |

## 4. Modelo de dados

Entidades já existentes na base, formalizadas:

- **Norma**: ID padronizado, tipo, órgão, número, data de assinatura e de sessão, nível (N1–N10, NT, MA), ementa, temas, situação e base da situação, fonte oficial, método e data de coleta, hash do original.
- **Dispositivo**: artigo, parágrafo, inciso, alínea, com âncora no texto.
- **Relação**: origem e dispositivo, destino e dispositivo, tipo (FUNDAMENTA-SE EM, REGULAMENTA, ALTERA, REVOGA total/parcial, SUPERA, REMETE A, DELEGA COMPETÊNCIA, PROPÕE SUBSTITUIR), início e fim de efeito, ressalva, base (texto, SIGRH, anotação, inferência), confiança, trecho, natureza (normativa ou sugestão).
- **Divergência** (D1, D2…): tipo, normas envolvidas, descrição, situação (aberta, resolvida, conflito não resolvido).
- **Decisão de vigência**: norma, situação decidida, fundamento, fonte, divergência relacionada.
- **Rodada**: escopo, datas, contagens (coletadas, relações novas, fila), conferências independentes e seus resultados.
- **Fila de coleta**: norma citada sem texto, quem cita, onde provavelmente está, status (a coletar, pedida à SODS, não localizada, fonte inacessível).

## 5. Pipeline de cada rodada

1. Coleta dos originais (SIGRH, SODS, planalto, CNE), com manifesto (URL, tamanho, SHA-256).
2. Extração de texto (camada de texto do PDF; OCR quando necessário, marcado).
3. Extração de citações e classificação das relações, com trecho e dispositivo.
4. Regras de vigência (as seis da Rodada 1) e decisões fundamentadas.
5. Conferência independente por amostra, com registro das correções.
6. Geração e publicação do site; relatório da rodada (coletadas, relações novas, fila).

Tudo isso já aconteceu três vezes à mão (Rodadas 0, 1 e 2). O trabalho é transformar os scripts em um pipeline reproduzível, com testes sobre os casos já conferidos (as divergências D1–D73 viram casos de teste).

## 6. Oráculo: desenho

- Entrada: pergunta livre. Primeiro passo: identificar normas citadas pelo número, órgão e tema (busca no grafo), depois recuperar trechos (busca lexical e semântica), sempre filtrando pela vigência.
- Saída: o formato do item 7 do projeto, com link para a norma e o dispositivo no ecossistema e, quando útil, o recorte da Teia.
- Regras: responder só com o acervo; nunca inventar número, artigo ou data; distinguir norma, material de apoio e interpretação; verificar o estado do processo estatuinte; não decidir casos.
- Qualidade: conjunto de perguntas de referência; medir acerto da recuperação e da resposta separadamente (a experiência da USP mostra que o erro costuma estar na recuperação); publicar os números.
- Custo e responsabilidade: chamada a modelo tem custo por consulta e exige chave institucional; definir com a SODS e a STI quem responde pelo serviço antes de abrir à comunidade.

## 7. Governança

- **SODS**: curadoria do acervo, validação de vigência, fonte das resoluções não localizadas (148 pedidas), definição das perguntas de referência.
- **Procuradoria Federal**: consultada sobre o enquadramento do oráculo (orienta, não decide) e sobre os conflitos registrados.
- **STI**: hospedagem, domínio, chave de API, integração com o SIGRH.
- **Direção do CT / Marcel**: coordenação do projeto, método e conferências.
- Licença: código aberto; dados abertos (as normas são públicas e o Decreto 10.139/2019 exige publicidade da consolidação). Decidir se o repositório nasce público ou fica privado até a adesão da SODS.

## 8. Cronograma proposto

| Marco | Conteúdo | Prazo |
|---|---|---|
| M1 | Repositório criado; base e textos migrados do computador; gerador lendo e validando a base | concluído em 02/11/2026 (repositório local `farol-normativo`, aguardando criação no GitHub) |
| M2 | Site v0.1 no ar: ficha e texto de cada norma com links, busca, Teia integrada (base completa da Rodada 2: 6.333 normas, 3.281 textos) | concluído em 02/11/2026 — https://marcelgois-png.github.io/farol-normativo/ (GitHub Pages, repositório público) |
| M3 | Painéis internos (vigência, divergências, fila, rodadas) e endereços estáveis; revisão de OCR nas normas estruturais | +2 semanas |
| M4 | Apresentação à SODS com o site no ar; pedido das 148 resoluções; definição das perguntas de referência | dezembro de 2026 |
| M5 | Rodada 3 (resoluções da SODS, pareceres do CNE, portarias MEC/CAPES) pelo pipeline novo | janeiro de 2027 |
| M6 | Oráculo piloto, fechado, avaliado com as perguntas de referência | fevereiro–março de 2027 |
| M7 | Oráculo aberto à comunidade; colaboração; atualização automática | abril de 2027 |
| M8 | Consolidação do Estatuto e dos regimentos; hospedagem UFPB | 2027, com a SODS |

## 9. Riscos

| Risco | Mitigação |
|---|---|
| Hospedagem institucional demora | começar no GitHub Pages; o site é uma pasta, migra depois |
| OCR quebra links e âncoras | marcar texto por OCR, ligar ao PDF, priorizar revisão das normas mais citadas |
| Oráculo responde errado e perde confiança | piloto fechado, avaliação publicada, resposta sempre com fonte e trecho, "não encontrei no acervo" como resposta válida |
| Custo recorrente do modelo | só no estágio 2, com chave e orçamento institucionais; o site estático não tem custo |
| Base desatualiza | rotina de leitura do SIGRH e rodadas regulares; relatório por rodada |
| Dependência de uma pessoa | repositório documentado, pipeline reproduzível, SODS na curadoria |

## 10. Decisões pendentes

1. Repositório: GitHub pessoal do Marcel ou organização; público desde já ou privado até a SODS aderir.
2. Hospedagem inicial: GitHub Pages (público) ou servidor próprio desde o início.
3. Escopo do ecossistema no site v0.1: todas as 3.112 normas com texto, ou núcleo primeiro.
4. Endereço: pedir farol.ufpb.br à STI (nome já decidido: Farol Normativo UFPB).
5. Modelo de linguagem do oráculo e quem detém a chave (STI, CT ou SODS).
6. Interlocutor na SODS para as perguntas de referência e para o pedido das 148 resoluções.

## 11. Situação em 02/11/2026 e próximo passo

M1 concluído: a base completa da Rodada 2 (6.333 normas, 23.798 relações) e os 3.285 textos foram migrados de `Documents\Oraculovski` para o repositório `farol-normativo`, com o gerador (`python -m farol validar | gerar`), testes, `CLAUDE.md` com as regras do acervo e a ação de publicação no GitHub Pages. O gerador produz o site completo em cerca de 20 s: 6.333 fichas, 3.277 textos com 19.893 links de citação e 70.788 âncoras de artigo, Teia integrada, busca, quadro de vigência, divergências e fila. Cópia do repositório (git bundle) em `Documents\Oraculovski\_scripts\farol-normativo.bundle`.

Repositório criado em `github.com/marcelgois-png/farol-normativo` (privado) com a ação de testes/validação/geração rodando a cada envio; os quatro textos da Rodada 0 foram recoletados do HTML oficial da SODS em 02/11/2026 (`base/sods/`, `textos/SODS/`), com redações revogadas tachadas e numeração de listas restaurada.

Projeto cadastrado no Planeja CT em 02/11/2026 como "Implantar o Farol Normativo UFPB: acervo, mapa de citações e consulta das normas da universidade" (690), com oito atividades: cinco concluídas (base, Teia, plano, repositório, textos da SODS) e três previstas — site v0.1 até 20/11/2026, apresentação à SODS até 18/12/2026 e Rodada 3 até 29/01/2027.

Site v0.1 publicado em 02/11/2026 em https://marcelgois-png.github.io/farol-normativo/ (repositório tornado público; publicação automática a cada envio).

Em 02/11/2026 o site recebeu a identidade visual da UFPB conforme o Manual de Identidade Visual (paleta oficial, IBM Plex Sans/Serif/Condensed, marca "UFPB" na aplicação preferencial ao lado do nome do sistema, brasão no rodapé, flor de lis, filetes ondeados e círculos como elementos de fundo), uma tela inicial com os botões das funcionalidades, a página "Estatuto e regimentos" e as **anotações de vigência por artigo** no texto integral: sob o caput de cada artigo alcançado por relação ALTERA, REVOGA ou SUPERA da base aparece a norma que o alcança, o dispositivo dela, a data de efeito, a fonte e o trecho registrado, com link para o texto da norma alteradora (3.992 artigos anotados). Os textos continuam sendo a redação publicada na fonte oficial; só os consolidados (páginas da SODS, textos compilados do planalto) trazem a redação revogada tachada e a vigente em seguida. O texto compilado do acervo (redação vigente de cada artigo com histórico) permanece como entrega do estágio 3.

Ainda em 02/11/2026: barra de título fixa, tabelas com rolagem própria e ordenação por coluna, botão de busca avançada na abertura, links das normas em nova aba, explicação de OCR ao passar o mouse, coluna de vigência registrada na fila e entrada na fila dos 34 regimentos de unidades (8 pró-reitorias, 9 superintendências e 17 centros de ensino, conforme o site oficial da UFPB), a localizar nos sites das unidades, na SODS e no SIGRH.

Em 03/11/2026: botão de tema claro/escuro na barra de título (escolha guardada no navegador; sem escolha, segue o sistema), pastilhas da abertura nas cores e gradientes do manual e a seção "Comece por aqui" explicada como conjunto de exemplos.

Também em 03/11/2026, a Teia foi reorganizada: barra de ferramentas enxuta (título "Teia de normas" e busca), painéis Controles e Ficha na cor da pastilha da abertura, abertos e recolhidos por abas laterais com rótulo, ficha recolhida ao entrar, cartão da norma de partida junto de "salvar mapa", "seus mapas" e "mapas de exemplo", filtros de relação reunidos em Filtros com "Limpar filtros", e a ordem Partida → Vizinhança → Filtros → Vista → Máquina do tempo → Sobre a base.

Próximo passo (M3): revisão de OCR das normas estruturais mais citadas, vista por artigo na Teia e aproveitamento dos links da página do Regimento Geral na fila; em paralelo, pedir à STI o endereço farol.ufpb.br.

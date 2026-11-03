# Tutoriais do Farol Normativo (Ajuda CT)

Fontes do livro **Tutoriais do Farol Normativo**, publicado no Ajuda CT (https://ajuda.ct.ufpb.br/books/tutoriais-do-farol-normativo), estante Direção de Centro. Elaboração: Direção do Centro de Tecnologia/UFPB, 03/11/2026.

| Código | Página |
|---|---|
| FAROL00 | Apresentação (o que é o Farol, índice do livro, regras do acervo) |
| FAROL01 | Primeiro Acesso, Página Inicial e Navegação |
| FAROL02 | Busca de Normas |
| FAROL03 | Ficha da Norma |
| FAROL04 | Texto Integral e Anotações de Vigência |
| FAROL05 | Teia de Normas: Norma de Partida, Vizinhança e Ficha |
| FAROL06 | Teia de Normas: Filtros, Vista, Máquina do Tempo e Mapas |
| FAROL07 | Estatuto e Regimentos |
| FAROL08 | Quadro de Vigência |
| FAROL09 | Divergências e Decisões |
| FAROL10 | Fila de Coleta |

- `FAROLnn.md`: texto de cada página no modelo do Ajuda CT (seções I a IX). Marcadores: `{{IMG:nome|alt}}` (tela), `{{FLUXO}}` (fluxograma), `{{EXPEDIENTE}}`, `!!! info` (aviso) e links `ajuda:FAROLnn` para outra página do livro.
- `img/`: telas do site, capturadas do site gerado localmente (1280 px de largura; painéis e celular em tamanho real).
- `fluxogramas/`: um `.drawio` por página, gerado por `node scripts/tutorial/fluxogramas.js` no padrão ALM001.
- `scripts/tutorial/ajuda_html.py`: converte o Markdown no HTML das páginas do Ajuda.

Quando o site mudar de aparência ou de comportamento, atualize a tela e o passo correspondentes e publique a revisão no Ajuda (número da revisão R01, R02…, e Data da Revisão no expediente).

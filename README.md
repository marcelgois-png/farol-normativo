# Farol Normativo UFPB

Consulta ao ecossistema normativo da Universidade Federal da Paraíba: as normas que orientam as decisões da universidade, como elas se citam, alteram e revogam umas às outras, e o que está vigente.

O repositório guarda a **base** (normas e relações, com trecho e fonte de cada uma), os **textos integrais** em Markdown e o **gerador** que transforma tudo em um site estático com:

- **Busca** por número, ano, órgão, nível, tema, situação e palavras da ementa;
- **Teia**: mapa interativo de citações, com norma de partida, vigência, máquina do tempo e filtros;
- **Ficha e texto** de cada norma, com as citações em link para a norma citada e âncora por artigo;
- **Quadro de vigência**, **registro de divergências** e **fila de coleta**.

Base atual: Rodada 2 (20/10/2026), com 6.333 normas, 3.277 textos integrais e 23.798 relações.

## Como gerar o site

```
pip install -r requirements.txt
python -m farol validar
python -m farol gerar
python -m http.server 8000 --directory site
```

Abra `http://localhost:8000/`. O site é publicado automaticamente no GitHub Pages a cada envio para `main` (ver `.github/workflows/site.yml`).

## Método

Expansão por citação a partir do Estatuto e dos regimentos comuns, com todas as resoluções dos conselhos superiores lidas na íntegra e cada norma citada entrando numa fila de coleta. A situação de vigência é conferida no texto das normas posteriores, não apenas no registro do SIGRH. Regras completas em `CLAUDE.md`; relatórios de cada rodada em `docs/rodadas/`; plano da aplicação em `docs/plano.md`.

O Farol orienta e não substitui parecer da Procuradoria Federal junto à UFPB nem a deliberação dos órgãos competentes. Em caso de divergência, prevalece o texto oficial publicado.

## Origem

Projeto Oraculovski, coordenado por Marcel de Gois Pinto (Centro de Tecnologia, UFPB).

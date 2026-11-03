"""Converte os tutoriais do Farol (docs/tutorial/FAROLnn.md) no HTML das páginas do Ajuda CT.

Segue o padrão da skill ajuda-ct-procedimentos (seções I–IX, h5, parágrafos justificados, tabela do
expediente) e acrescenta três marcadores próprios dos tutoriais:
  {{IMG:nome|texto alternativo}}  imagem centralizada com borda e link para o original (galeria do Ajuda)
  !!! info texto                  aviso <p class="callout info">
  [rótulo](ajuda:FAROLnn)         link para outra página do livro

Uso: python scripts/tutorial/ajuda_html.py imagens.json saida/
  imagens.json: {"farol01-01-inicio": "https://ajuda.ct.ufpb.br/uploads/images/gallery/…", …}
  (sem o arquivo, a URL de cada imagem fica como %%IMG:nome%%, trocada na publicação pela URL da galeria)
"""
import html
import json
import re
import sys
import unicodedata
from pathlib import Path

import markdown

AJUDA = "https://ajuda.ct.ufpb.br"
LIVRO = "tutoriais-do-farol-normativo"
RAIZ = Path(__file__).resolve().parents[2] / "docs" / "tutorial"

CAMPOS = ['Elaborado por:', 'Data de Elaboração:', 'Data da Revisão:', 'Código do procedimento:', 'Número da revisão:',
          'Setor:', 'Responsável:', 'Horário de funcionamento:', 'Contato:', 'Telefone:']


def expediente(valores):
    tr = ''.join(f'<tr><td style="width: 30.9816%;"><p><strong>{c}</strong></p></td>'
                 f'<td style="width: 69.0184%;"><p>{html.escape(v)}</p></td></tr>' for c, v in zip(CAMPOS, valores))
    return f'<table style="width: 100%;" border="1"><tbody>{tr}</tbody></table>'


def exped(codigo):
    return ['Direção do Centro de Tecnologia/UFPB', '03/11/2026', '—', codigo, '00', 'Direção de Centro', 'Marcel Gois',
            '8h30min às 17h30min', 'https://atendimento.ct.ufpb.br/index.php?category=52&a=add', '(83) 3216-7378']


def slug(nome):
    """Como o Str::slug do Laravel, usado pelo BookStack para o endereço da página."""
    s = unicodedata.normalize('NFKD', nome).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'[^-\w\s]+', '', s)
    return re.sub(r'[-\s_]+', '-', s).strip('-')


def titulo(md):
    return re.match(r'# (.*)', md).group(1).strip()


def paginas():
    """código (FAROL00…) -> (nome, url) de cada página do livro."""
    out = {}
    for f in sorted(RAIZ.glob('FAROL*.md')):
        nome = titulo(f.read_text(encoding='utf-8'))
        out[f.stem] = (nome, f'{AJUDA}/books/{LIVRO}/page/{slug(nome)}')
    return out


def md2ajuda(md, exped_vals, imagens, pags):
    t = re.sub(r'\A# .*\n', '', md)
    t = re.sub(r'\]\(ajuda:(FAROL\d\d)\)', lambda m: '](' + pags[m.group(1)][1] + ')', t)
    linhas = []
    for l in t.split('\n'):
        if re.match(r'^ +([-*]|\d+\.) ', l):
            l = '    ' + l.lstrip()
        if re.match(r'^([-*]|\d+\.) ', l) and linhas and linhas[-1].strip() and not re.match(r'^\s*([-*]|\d+\.) ', linhas[-1]):
            linhas.append('')
        linhas.append(l)
    t = '\n'.join(linhas)
    # avisos e imagens viram marcadores protegidos da conversão
    blocos = {}

    def guarda(h):
        k = f'@@BLOCO{len(blocos)}@@'
        blocos[k] = h
        return '\n\n' + k + '\n\n'

    def aviso(m):
        corpo = markdown.markdown(m.group(2)).removeprefix('<p>').removesuffix('</p>')
        return guarda(f'<p class="callout {m.group(1)}">{corpo}</p>')

    def imagem(m):
        nome, alt = m.group(1), m.group(2)
        url = imagens.get(nome) or f'%%IMG:{nome}%%'   # marcador trocado pela URL da galeria na publicação
        a = html.escape(alt, quote=True)
        return guarda(f'<p style="text-align: center;"><a href="{url}" target="_blank"><img src="{url}" alt="{a}" '
                      f'style="max-width: 100%; border: 1px solid #dddddd;"></a></p>')

    t = re.sub(r'^!!! (info|warning) (.+)$', aviso, t, flags=re.M)
    t = re.sub(r'^\{\{IMG:([^|}]+)\|([^}]*)\}\}$', imagem, t, flags=re.M)
    h = markdown.markdown(t, extensions=['tables', 'sane_lists'])
    for k, v in blocos.items():
        h = h.replace(f'<p>{k}</p>', v)
    h = re.sub(r'<li>\s*<p>(.*?)</p>\s*</li>', r'<li>\1</li>', h, flags=re.S)
    h = re.sub(r'<h2>(.*?)</h2>', r'<h5 style="text-align: justify;"><strong>\1</strong></h5>', h)
    h = re.sub(r'<h3>(.*?)</h3>', r'<h6><strong>\1</strong></h6>', h)
    h = h.replace('<p>{{FLUXO}}</p>', '{{FLUXO}}').replace('<p>{{EXPEDIENTE}}</p>', '{{EXPEDIENTE}}')
    h = h.replace('<p>', '<p style="text-align: justify;">')
    # tabelas no padrão do livro: cabeçalho em negrito na primeira linha, células com <p>
    h = h.replace('<table>', '<table style="width: 100%;" border="1">')
    h = re.sub(r'<thead>\s*<tr>(.*?)</tr>\s*</thead>\s*<tbody>',
               lambda m: '<tbody><tr>' + re.sub(r'<th[^>]*>(.*?)</th>', r'<td><p><strong>\1</strong></p></td>', m.group(1), flags=re.S) + '</tr>',
               h, flags=re.S)
    h = re.sub(r'<td>(?!<p>)(.*?)</td>', r'<td><p>\1</p></td>', h, flags=re.S)
    h = re.sub(r'<a href="(https?://[^"]+)">', r'<a href="\1" target="_blank">', h)
    h = re.sub(r'>\n+<', '><', h).replace('\n', ' ').strip()
    return h.replace('{{EXPEDIENTE}}', expediente(exped_vals))


def main():
    imagens = json.loads(Path(sys.argv[1]).read_text()) if len(sys.argv) > 1 and Path(sys.argv[1]).exists() else {}
    saida = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('.')
    saida.mkdir(parents=True, exist_ok=True)
    pags = paginas()
    resumo = {}
    for cod, (nome, url) in pags.items():
        md = (RAIZ / f'{cod}.md').read_text(encoding='utf-8')
        h = md2ajuda(md, exped(cod), imagens, pags)
        (saida / f'{cod}.html').write_text(h, encoding='utf-8')
        resumo[cod] = {'nome': nome, 'slug': slug(nome), 'url': url, 'imagens': re.findall(r'\{\{IMG:([^|}]+)\|', md), 'bytes': len(h)}
    (saida / 'paginas.json').write_text(json.dumps(resumo, ensure_ascii=False, indent=1), encoding='utf-8')
    for cod, r in resumo.items():
        print(cod, r['slug'], len(r['imagens']), 'imagens', r['bytes'], 'bytes')


if __name__ == '__main__':
    main()

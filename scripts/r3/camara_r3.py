"""Rodada 3: converte as páginas da Câmara (Portal da Legislação, legin) em texto e ficha.
Uso: python3 -I camara_r3.py <pasta FEDERAL> <manifesto.tsv> <saida.json>
Para cada ID: ficha (epígrafe, ementa, data, situação, vide) a partir da página "Dados da Norma"
e texto integral a partir de "Publicação Original" (ou "Texto Atualizado", quando só ele existir)."""
import json, os, re, sys, unicodedata, hashlib
from bs4 import BeautifulSoup, NavigableString

BLOCO = {"p", "div", "br", "tr", "li", "h1", "h2", "h3", "h4", "h5", "h6", "table", "blockquote", "center"}
MESES = {"janeiro": 1, "fevereiro": 2, "março": 3, "marco": 3, "abril": 4, "maio": 5, "junho": 6, "julho": 7,
         "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12}

def dec(b):
    for enc in ("utf-8", "cp1252", "latin-1"):
        try:
            return b.decode(enc)
        except Exception:
            pass
    return b.decode("utf-8", "replace")

def bloco_texto(el):
    for t in el(["script", "style"]):
        t.decompose()
    for t in el.find_all(["strike", "s", "del"]):
        inner = t.get_text(" ", strip=True)
        t.replace_with(NavigableString(f" ~~{inner}~~ " if inner else " "))
    for t in el.find_all(list(BLOCO)):
        t.insert_before(NavigableString("\n")); t.insert_after(NavigableString("\n"))
    tx = el.get_text().replace("\xa0", " ")
    tx = re.sub(r"[ \t]+", " ", tx)
    tx = re.sub(r" *\n *", "\n", tx)
    tx = re.sub(r"\n{3,}", "\n\n", tx)
    return unicodedata.normalize("NFC", tx.strip())

def data_iso(s):
    m = re.search(r"(\d{1,2}) de (\w+) de (\d{4})", s, re.I)
    if not m:
        return ""
    mm = MESES.get(m.group(2).lower(), 0)
    return f"{m.group(3)}-{mm:02d}-{int(m.group(1)):02d}" if mm else m.group(3)

def ficha_norma(html):
    soup = BeautifulSoup(html, "lxml")
    c = soup.select_one("#content") or soup.body
    txt = bloco_texto(c)
    f = dict(epigrafe="", data="", ementa="", situacao_fonte="", vide=[], publicacao="")
    h1 = c.find("h1")
    if h1:
        f["epigrafe"] = re.sub(r"\s+", " ", h1.get_text(" ", strip=True))
        f["data"] = data_iso(f["epigrafe"])
    m = re.search(r"EMENTA:\s*(.+?)\n", txt)
    if m:
        f["ementa"] = m.group(1).strip()
    m = re.search(r"Situação:\s*(\S[^\n]*)", txt)
    if m:
        f["situacao_fonte"] = m.group(1).strip()
    m = re.search(r"Vide Norma\(s\):\s*(.+?)(?:\n\n|\nIndexação|\n\d+ª Legislatura)", txt, re.S)
    if m:
        f["vide"] = [v.strip() for v in re.split(r"\n", m.group(1)) if v.strip()]
    m = re.search(r"Diário Oficial da União[^\n]*", txt)
    if m:
        f["publicacao"] = m.group(0).strip()
    return f

def texto_original(html):
    soup = BeautifulSoup(html, "lxml")
    el = soup.select_one("div.textoNorma") or soup.select_one("#content") or soup.body
    return bloco_texto(el)

def main(pasta, manifesto, saida):
    man = {}
    for ln in open(manifesto, encoding="utf-8"):
        p = ln.rstrip("\n").split("\t")
        if len(p) >= 5:
            man[p[0]] = dict(bytes=p[1], sha256=p[2], ct=p[3], url=p[4], data_coleta=p[5] if len(p) > 5 else "")
    out = {}
    ids = sorted({f.split("__")[0] for f in os.listdir(pasta) if f.endswith(".html")})
    for i in ids:
        pn = os.path.join(pasta, f"{i}__camara-norma.html")
        po = os.path.join(pasta, f"{i}__camara-original.html")
        pa = os.path.join(pasta, f"{i}__camara-atualizada.html")
        r = dict(id=i)
        if os.path.exists(pn):
            r.update(ficha_norma(dec(open(pn, "rb").read())))
            r["fonte_ficha"] = man.get(os.path.basename(pn), {}).get("url", "")
        src = po if os.path.exists(po) else (pa if os.path.exists(pa) else None)
        if src:
            r["texto"] = texto_original(dec(open(src, "rb").read()))
            r["fonte_texto"] = man.get(os.path.basename(src), {}).get("url", "")
            r["arquivo_local"] = "originais_r3/FEDERAL/" + os.path.basename(src)
            r["sha256"] = man.get(os.path.basename(src), {}).get("sha256", "") or hashlib.sha256(open(src, "rb").read()).hexdigest()
            r["versao"] = "publicação original (Câmara dos Deputados)" if src == po else "texto atualizado (Câmara dos Deputados)"
            r["metodo_texto"] = "página oficial do Portal da Legislação da Câmara dos Deputados (HTML) convertida em texto" + ("; ~~tachado~~ = redação revogada ou alterada" if src == pa else "")
        out[i] = r
    json.dump(out, open(saida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for i, r in out.items():
        print(i, "|", r.get("data"), "|", (r.get("situacao_fonte") or "")[:12], "|", len(r.get("texto", "")), "|", (r.get("ementa") or "")[:70])

if __name__ == "__main__":
    main(*sys.argv[1:4])

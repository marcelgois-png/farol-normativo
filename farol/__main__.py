"""Linha de comando: python -m farol validar | gerar [--limite-textos N] [--saida DIR]"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="farol", description="Gerador do Farol Normativo UFPB")
    ap.add_argument("comando", choices=["validar", "gerar"])
    ap.add_argument("--raiz", default=".", help="pasta do repositório (padrão: atual)")
    ap.add_argument("--saida", default=None, help="pasta de saída do site (padrão: <raiz>/site)")
    ap.add_argument("--limite-textos", type=int, default=None, help="renderiza só os N primeiros textos (para testes)")
    args = ap.parse_args(argv)

    t0 = time.time()
    if args.comando == "validar":
        from .base import Base

        b = Base.carregar(args.raiz)
        print(json.dumps(b.resumo(), ensure_ascii=False, indent=1))
        for p in b.problemas[:50]:
            print("!", p)
        if len(b.problemas) > 50:
            print(f"! … e mais {len(b.problemas) - 50}")
        graves = [p for p in b.problemas if p.startswith(("ID duplicado", "aresta com", "tipo de relação", "nível desconhecido", "situação desconhecida"))]
        print(f"{len(b.problemas)} aviso(s), {len(graves)} grave(s), {time.time() - t0:.1f}s")
        return 1 if graves else 0

    from .site import Gerador

    g = Gerador(args.raiz, args.saida)
    cont = g.gerar(limite_textos=args.limite_textos)
    print(json.dumps(cont, ensure_ascii=False, indent=1))
    print(f"site em {Path(g.saida).resolve()} ({time.time() - t0:.1f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

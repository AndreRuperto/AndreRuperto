"""Monta a seção de estatísticas do README só com os cards disponíveis.

O GitHub remove atributos como `onerror` do README, então uma imagem quebrada
não pode se esconder sozinha. Este script roda no GitHub Actions e reescreve o
bloco entre <!-- STATS:START --> e <!-- STATS:END -->:

- cards gerados por gerar_cards.py entram se o arquivo existir;
- cards de serviços externos (campo "url") entram só se responderem um SVG.

Cards com o mesmo número de "linha" ficam lado a lado; a largura em % segue a
grade de 900 px de gerar_cards.py. Se nada estiver disponível, a seção some.
"""

import re
import sys
import urllib.error
import urllib.request
from itertools import groupby
from pathlib import Path

README = Path(__file__).resolve().parents[2] / "README.md"
INICIO, FIM = "<!-- STATS:START -->", "<!-- STATS:END -->"

CARDS = [
    {
        "linha": 1,
        "arquivo": "assets/stats/resumo.svg",
        "alt": "Resumo do GitHub",
        "largura": "54.5%",  # 495 / 900, com folga para o espaço entre as imagens
    },
    {
        "linha": 1,
        "arquivo": "assets/stats/linguagens.svg",
        "alt": "Linguagens mais usadas",
        "largura": "43.3%",  # 395 / 900
    },
    {
        "linha": 2,
        "arquivo": "assets/stats/atividade.svg",
        "alt": "Gráfico de contribuições dos últimos 31 dias",
        "largura": "98.6%",  # alinha com as bordas da linha 1
    },
]


def funciona(url: str) -> bool:
    req = urllib.request.Request(url, headers={"User-Agent": "readme-stats-check"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            tipo = resp.headers.get("Content-Type", "")
            corpo = resp.read(4096)
            return resp.status == 200 and "svg" in tipo and b"<svg" in corpo
    except (urllib.error.URLError, TimeoutError, OSError) as erro:
        print(f"  erro: {erro}")
        return False


def disponivel(card: dict) -> bool:
    if "arquivo" in card:
        return (README.parent / card["arquivo"]).is_file()
    return funciona(card["url"])


def img(card: dict) -> str:
    src = f'./{card["arquivo"]}' if "arquivo" in card else card["url"].replace("&", "&amp;")
    return f'<img src="{src}" width="{card["largura"]}" alt="{card["alt"]}" />'


def montar_bloco(ativos: list[dict]) -> str:
    if not ativos:
        return f"{INICIO}\n{FIM}"
    # Imagens da mesma linha ficam no mesmo parágrafo (sem linha em branco entre elas).
    linhas = ["  " + "\n  ".join(img(c) for c in grupo)
              for _, grupo in groupby(ativos, key=lambda c: c["linha"])]
    corpo = "\n\n".join(linhas)
    return (
        f"{INICIO}\n### 📊 Estatísticas\n\n<div align=\"center\">\n\n"
        f"{corpo}\n\n</div>\n\n---\n{FIM}"
    )


def main() -> int:
    ativos = []
    for card in CARDS:
        ok = disponivel(card)
        print(f"{'OK   ' if ok else 'FALHA'} {card['alt']}")
        if ok:
            ativos.append(card)

    texto = README.read_text(encoding="utf-8")
    padrao = re.compile(re.escape(INICIO) + r".*?" + re.escape(FIM), re.DOTALL)
    if not padrao.search(texto):
        print("Marcadores não encontrados no README.", file=sys.stderr)
        return 1

    novo = padrao.sub(lambda _: montar_bloco(ativos), texto)
    if novo != texto:
        README.write_text(novo, encoding="utf-8", newline="\n")
        print("README atualizado.")
    else:
        print("Nada mudou.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

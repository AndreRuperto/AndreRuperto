"""Monta a seção de estatísticas dos READMEs só com os cards disponíveis.

O GitHub remove atributos como `onerror` do README, então uma imagem quebrada
não pode se esconder sozinha. Este script roda no GitHub Actions e reescreve o
bloco entre <!-- STATS:START --> e <!-- STATS:END --> em README.md (português)
e README.en.md (inglês):

- cards gerados por gerar_cards.py entram se o arquivo existir (o README aponta
  para a cópia publicada na branch output, não para o arquivo local);
- cards de serviços externos (campo "url") entram só se responderem um SVG.

Cards com o mesmo número de "linha" ficam lado a lado; a largura em % segue a
grade de 900 px de gerar_cards.py. Se nada estiver disponível, a seção some.
"""

import os
import re
import sys
import urllib.error
import urllib.request
from itertools import groupby
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
READMES = {"README.md": "pt", "README.en.md": "en"}
TITULOS = {"pt": "Estatísticas", "en": "Statistics"}
INICIO, FIM = "<!-- STATS:START -->", "<!-- STATS:END -->"

# Os cards não ficam na main: o workflow os publica em stats/ na branch output,
# para que a atualização a cada 6 h não gere commits no histórico principal.
REPO = os.environ.get("GITHUB_REPOSITORY", "AndreRuperto/AndreRuperto")
PUBLICADO = f"https://raw.githubusercontent.com/{REPO}/output/stats"

CARDS = [
    {
        "linha": 1,
        "arquivo": "assets/stats/resumo.svg",
        "alt": {"pt": "Resumo do GitHub", "en": "GitHub summary (card in Portuguese)"},
        "largura": "54.5%",  # 495 / 900, com folga para o espaço entre as imagens
    },
    {
        "linha": 1,
        "arquivo": "assets/stats/linguagens.svg",
        "alt": {"pt": "Linguagens mais usadas", "en": "Most used languages (card in Portuguese)"},
        "largura": "43.3%",  # 395 / 900
    },
    {
        "linha": 2,
        "arquivo": "assets/stats/atividade.svg",
        "alt": {"pt": "Gráfico de contribuições dos últimos 31 dias",
                "en": "Contributions over the last 31 days (card in Portuguese)"},
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
        return (RAIZ / card["arquivo"]).is_file()
    return funciona(card["url"])


def img(card: dict, idioma: str) -> str:
    if "arquivo" in card:
        src = f'{PUBLICADO}/{Path(card["arquivo"]).name}'
    else:
        src = card["url"].replace("&", "&amp;")
    return f'<img src="{src}" width="{card["largura"]}" alt="{card["alt"][idioma]}" />'


def montar_bloco(ativos: list[dict], idioma: str) -> str:
    if not ativos:
        return f"{INICIO}\n{FIM}"
    # Imagens da mesma linha ficam no mesmo parágrafo (sem linha em branco entre elas).
    linhas = ["  " + "\n  ".join(img(c, idioma) for c in grupo)
              for _, grupo in groupby(ativos, key=lambda c: c["linha"])]
    corpo = "\n\n".join(linhas)
    return (
        f"{INICIO}\n### {TITULOS[idioma]}\n\n<div align=\"center\">\n\n"
        f"{corpo}\n\n</div>\n{FIM}"
    )


def main() -> int:
    ativos = []
    for card in CARDS:
        ok = disponivel(card)
        print(f"{'OK   ' if ok else 'FALHA'} {card['alt']['pt']}")
        if ok:
            ativos.append(card)

    padrao = re.compile(re.escape(INICIO) + r".*?" + re.escape(FIM), re.DOTALL)
    erro = 0
    for nome, idioma in READMES.items():
        arquivo = RAIZ / nome
        texto = arquivo.read_text(encoding="utf-8")
        if not padrao.search(texto):
            print(f"Marcadores não encontrados em {nome}.", file=sys.stderr)
            erro = 1
            continue
        novo = padrao.sub(lambda _: montar_bloco(ativos, idioma), texto)
        if novo != texto:
            arquivo.write_text(novo, encoding="utf-8", newline="\n")
            print(f"{nome} atualizado.")
        else:
            print(f"{nome}: nada mudou.")
    return erro


if __name__ == "__main__":
    sys.exit(main())

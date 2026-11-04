"""Testa os cards de estatísticas e reescreve a seção do README só com os que funcionam.

O GitHub remove atributos como `onerror` do README, então uma imagem quebrada
não pode se esconder sozinha. Este script roda no GitHub Actions, faz uma
requisição para cada card e monta o bloco entre os marcadores
<!-- STATS:START --> e <!-- STATS:END --> apenas com os que respondem uma
imagem SVG. Se nenhum funcionar, a seção inteira some.
"""

import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

USUARIO = "AndreRuperto"
README = Path(__file__).resolve().parents[2] / "README.md"
INICIO, FIM = "<!-- STATS:START -->", "<!-- STATS:END -->"

CARDS = [
    {
        "nome": "Gráfico de atividade",
        "url": f"https://github-readme-activity-graph.vercel.app/graph?username={USUARIO}&theme=merko",
        "html": '  <img src="{url}" alt="Gráfico de atividade do GitHub" />',
    },
    {
        "nome": "Streak",
        "url": f"https://streak-stats.demolab.com?user={USUARIO}&theme=merko",
        "html": '  <a href="https://git.io/streak-stats">\n    <img src="{url}" alt="GitHub Streak" />\n  </a>',
    },
    {
        "nome": "Stats",
        "url": (
            f"https://github-readme-stats.vercel.app/api?username={USUARIO}&show_icons=true"
            "&include_all_commits=true&count_private=true&theme=merko&rank_icon=github&border_radius=10"
        ),
        "html": '  <img src="{url}" height="150" alt="Estatísticas GitHub" />',
    },
    {
        "nome": "Top Langs",
        "url": (
            f"https://github-readme-stats.vercel.app/api/top-langs?username={USUARIO}&locale=en"
            "&hide_title=false&layout=compact&card_width=320&langs_count=5&theme=merko&border_radius=10"
        ),
        "html": '  <img src="{url}" height="150" alt="Linguagens mais usadas" />',
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


def montar_bloco(ativos: list[dict]) -> str:
    if not ativos:
        return f"{INICIO}\n{FIM}"
    imagens = "\n\n".join(c["html"].format(url=c["url"].replace("&", "&amp;")) for c in ativos)
    return (
        f"{INICIO}\n### 📊 Estatísticas\n\n<div align=\"center\">\n\n"
        f"{imagens}\n\n</div>\n\n---\n{FIM}"
    )


def main() -> int:
    ativos = []
    for card in CARDS:
        ok = funciona(card["url"])
        print(f"{'OK   ' if ok else 'FALHA'} {card['nome']}")
        if ok:
            ativos.append(card)

    texto = README.read_text(encoding="utf-8")
    padrao = re.compile(re.escape(INICIO) + r".*?" + re.escape(FIM), re.DOTALL)
    if not padrao.search(texto):
        print("Marcadores não encontrados no README.", file=sys.stderr)
        return 1

    novo = padrao.sub(lambda _: montar_bloco(ativos), texto)
    if novo != texto:
        README.write_text(novo, encoding="utf-8")
        print("README atualizado.")
    else:
        print("Nada mudou.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

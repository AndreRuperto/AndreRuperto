"""Testa os cards de estatísticas e reescreve a seção do README só com os que funcionam.

O GitHub remove atributos como `onerror` do README, então uma imagem quebrada
não pode se esconder sozinha. Este script roda no GitHub Actions e monta o
bloco entre os marcadores <!-- STATS:START --> e <!-- STATS:END --> apenas com
os cards disponíveis: os gerados localmente (gerar_cards.py) entram se o
arquivo existir, e os externos entram se responderem uma imagem SVG. Se nenhum
estiver disponível, a seção inteira some.
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
    # Gerados por gerar_cards.py dentro do próprio repositório.
    {
        "nome": "Gráfico de atividade",
        "arquivo": "assets/stats/atividade.svg",
        "html": '  <img src="./{arquivo}" alt="Gráfico de contribuições dos últimos 31 dias" />',
    },
    # Serviço externo: entra só se estiver respondendo.
    {
        "nome": "Streak",
        "url": f"https://streak-stats.demolab.com?user={USUARIO}&theme=merko",
        "html": '  <a href="https://git.io/streak-stats">\n    <img src="{url}" alt="GitHub Streak" />\n  </a>',
    },
    {
        "nome": "Stats",
        "arquivo": "assets/stats/stats.svg",
        "html": '  <img src="./{arquivo}" height="170" alt="Estatísticas do GitHub" />',
    },
    {
        "nome": "Linguagens",
        "arquivo": "assets/stats/linguagens.svg",
        "html": '  <img src="./{arquivo}" height="170" alt="Linguagens mais usadas" />',
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
    imagens = "\n\n".join(
        c["html"].format(url=c.get("url", "").replace("&", "&amp;"), arquivo=c.get("arquivo", ""))
        for c in ativos
    )
    return (
        f"{INICIO}\n### 📊 Estatísticas\n\n<div align=\"center\">\n\n"
        f"{imagens}\n\n</div>\n\n---\n{FIM}"
    )


def main() -> int:
    ativos = []
    for card in CARDS:
        if "arquivo" in card:
            ok = (README.parent / card["arquivo"]).is_file()
        else:
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

"""Gera os cards de estatísticas do perfil como SVGs dentro do próprio repositório.

Substitui as instâncias públicas do github-readme-stats e do
github-readme-activity-graph, que vivem fora do ar por limite de uso.
Usa a API GraphQL do GitHub com o token em GITHUB_TOKEN e grava em assets/stats/:

- stats.svg     → estrelas, commits do ano, PRs, issues e repositórios contribuídos
- linguagens.svg → linguagens mais usadas nos repositórios próprios
- atividade.svg  → contribuições dos últimos 31 dias

Cores no tema "merko", o mesmo do card de streak.
"""

import json
import os
import sys
import urllib.request
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

USUARIO = "AndreRuperto"
NOME = "André Ruperto"
SAIDA = Path(__file__).resolve().parents[2] / "assets" / "stats"
LINGUAGENS_IGNORADAS: set[str] = set()  # ex.: {"Jupyter Notebook"}
QTD_LINGUAGENS = 6

TEMA = {
    "fundo": "#0a0f0b",
    "borda": "#e4e2e2",
    "titulo": "#abd200",
    "texto": "#68b587",
    "icone": "#b7d364",
    "grade": "#1f2a21",
}
FONTE = "'Segoe UI', Ubuntu, 'Helvetica Neue', Sans-Serif"


# ───────────────────────────── API ─────────────────────────────

def graphql(query: str, variaveis: dict) -> dict:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("Defina GITHUB_TOKEN.")
    corpo = json.dumps({"query": query, "variables": variaveis}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=corpo,
        headers={"Authorization": f"bearer {token}", "User-Agent": "readme-cards"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        dados = json.load(resp)
    if "errors" in dados:
        sys.exit(f"Erro na API: {dados['errors']}")
    return dados["data"]


Q_USUARIO = """
query($login: String!) {
  user(login: $login) {
    pullRequests { totalCount }
    issues { totalCount }
    repositoriesContributedTo(contributionTypes: [COMMIT, PULL_REQUEST, ISSUE, PULL_REQUEST_REVIEW]) { totalCount }
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""

Q_REPOS = """
query($login: String!, $cursor: String) {
  user(login: $login) {
    repositories(first: 100, after: $cursor, ownerAffiliations: OWNER, isFork: false) {
      pageInfo { hasNextPage endCursor }
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
  }
}
"""


def buscar_repos() -> list[dict]:
    repos, cursor = [], None
    while True:
        dados = graphql(Q_REPOS, {"login": USUARIO, "cursor": cursor})["user"]["repositories"]
        repos += dados["nodes"]
        if not dados["pageInfo"]["hasNextPage"]:
            return repos
        cursor = dados["pageInfo"]["endCursor"]


# ───────────────────────────── SVG ─────────────────────────────

def moldura(largura: int, altura: int, titulo: str, conteudo: str, rotulo: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="{altura}" viewBox="0 0 {largura} {altura}" role="img" aria-label="{escape(rotulo)}">
  <title>{escape(rotulo)}</title>
  <style>
    .titulo {{ font: 600 18px {FONTE}; fill: {TEMA['titulo']}; }}
    .texto  {{ font: 600 14px {FONTE}; fill: {TEMA['texto']}; }}
    .valor  {{ font: 700 14px {FONTE}; fill: {TEMA['titulo']}; }}
    .menor  {{ font: 400 12px {FONTE}; fill: {TEMA['texto']}; }}
  </style>
  <rect x="0.5" y="0.5" rx="10" width="{largura - 1}" height="{altura - 1}" fill="{TEMA['fundo']}" stroke="{TEMA['borda']}" stroke-opacity="0.8"/>
  <text x="25" y="35" class="titulo">{escape(titulo)}</text>
{conteudo}
</svg>
"""


def fmt(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def card_stats(usuario: dict, repos: list[dict]) -> str:
    cc = usuario["contributionsCollection"]
    linhas = [
        ("Estrelas recebidas", sum(r["stargazerCount"] for r in repos)),
        (f"Commits em {date.today().year}", cc["totalCommitContributions"] + cc["restrictedContributionsCount"]),
        ("Pull requests", usuario["pullRequests"]["totalCount"]),
        ("Issues", usuario["issues"]["totalCount"]),
        ("Contribuiu em (repos)", usuario["repositoriesContributedTo"]["totalCount"]),
    ]
    partes = []
    for i, (rotulo, valor) in enumerate(linhas):
        y = 70 + i * 25
        partes.append(
            f'  <circle cx="31" cy="{y - 5}" r="4" fill="{TEMA["icone"]}"/>\n'
            f'  <text x="50" y="{y}" class="texto">{escape(rotulo)}:</text>\n'
            f'  <text x="245" y="{y}" class="valor">{fmt(valor)}</text>'
        )
    total = cc["contributionCalendar"]["totalContributions"]
    partes.append(
        f'  <circle cx="370" cy="110" r="45" fill="none" stroke="{TEMA["titulo"]}" stroke-width="6"/>\n'
        f'  <text x="370" y="116" text-anchor="middle" class="titulo">{fmt(total)}</text>\n'
        f'  <text x="370" y="178" text-anchor="middle" class="menor">contribuições no ano</text>'
    )
    return moldura(467, 195, f"Estatísticas do GitHub de {NOME}", "\n".join(partes),
                   f"Estatísticas do GitHub de {NOME}")


def card_linguagens(repos: list[dict]) -> str:
    tamanhos: dict[str, list] = {}
    for repo in repos:
        for aresta in repo["languages"]["edges"]:
            nome = aresta["node"]["name"]
            if nome in LINGUAGENS_IGNORADAS:
                continue
            item = tamanhos.setdefault(nome, [0, aresta["node"]["color"] or "#858585"])
            item[0] += aresta["size"]
    top = sorted(tamanhos.items(), key=lambda kv: kv[1][0], reverse=True)[:QTD_LINGUAGENS]
    soma = sum(v[0] for _, v in top) or 1

    largura, barra_larg = 350, 300
    partes = [f'  <mask id="barra"><rect x="25" y="55" width="{barra_larg}" height="8" rx="5" fill="white"/></mask>',
              '  <g mask="url(#barra)">']
    x = 25.0
    for nome, (tam, cor) in top:
        w = barra_larg * tam / soma
        partes.append(f'    <rect x="{x:.2f}" y="55" width="{w:.2f}" height="8" fill="{cor}"/>')
        x += w
    partes.append("  </g>")
    for i, (nome, (tam, cor)) in enumerate(top):
        col, lin = i % 2, i // 2
        cx, cy = 30 + col * 160, 88 + lin * 25
        partes.append(
            f'  <circle cx="{cx}" cy="{cy - 4}" r="5" fill="{cor}"/>\n'
            f'  <text x="{cx + 12}" y="{cy}" class="menor">{escape(nome)} {tam / soma * 100:.1f}%</text>'
        )
    altura = 88 + ((len(top) + 1) // 2) * 25
    return moldura(largura, altura, "Linguagens mais usadas", "\n".join(partes),
                   f"Linguagens mais usadas por {NOME}")


def card_atividade(usuario: dict) -> str:
    dias = [d for s in usuario["contributionsCollection"]["contributionCalendar"]["weeks"]
            for d in s["contributionDays"]]
    hoje = date.today().isoformat()
    dias = [d for d in dias if d["date"] <= hoje][-31:]
    valores = [d["contributionCount"] for d in dias]

    largura, altura = 900, 300
    x0, x1, y0, y1 = 60, largura - 30, 60, altura - 50
    maximo = max(max(valores), 1)
    passo_y = max(1, -(-maximo // 4))
    topo = passo_y * 4

    def px(i: int) -> float:
        return x0 + (x1 - x0) * i / max(len(valores) - 1, 1)

    def py(v: int) -> float:
        return y1 - (y1 - y0) * v / topo

    partes = []
    for k in range(5):
        v = passo_y * k
        partes.append(
            f'  <line x1="{x0}" x2="{x1}" y1="{py(v):.1f}" y2="{py(v):.1f}" stroke="{TEMA["grade"]}"/>\n'
            f'  <text x="{x0 - 10}" y="{py(v) + 4:.1f}" text-anchor="end" class="menor">{v}</text>'
        )
    pontos = " ".join(f"{px(i):.1f},{py(v):.1f}" for i, v in enumerate(valores))
    area = f"{px(0):.1f},{y1} {pontos} {px(len(valores) - 1):.1f},{y1}"
    partes.append(f'  <polygon points="{area}" fill="{TEMA["titulo"]}" fill-opacity="0.12"/>')
    partes.append(f'  <polyline points="{pontos}" fill="none" stroke="{TEMA["titulo"]}" stroke-width="2.5" stroke-linejoin="round"/>')
    for i, (d, v) in enumerate(zip(dias, valores)):
        partes.append(f'  <circle cx="{px(i):.1f}" cy="{py(v):.1f}" r="3.5" fill="{TEMA["icone"]}"><title>{d["date"]}: {v}</title></circle>')
        if i % 2 == 0 or i == len(dias) - 1:
            partes.append(f'  <text x="{px(i):.1f}" y="{y1 + 22}" text-anchor="middle" class="menor">{d["date"][8:]}</text>')
    partes.append(f'  <text x="{largura - 30}" y="35" text-anchor="end" class="menor">{fmt(sum(valores))} contribuições</text>')
    return moldura(largura, altura, f"Contribuições de {NOME} nos últimos 31 dias", "\n".join(partes),
                   f"Gráfico de contribuições de {NOME} nos últimos 31 dias")


def main() -> None:
    usuario = graphql(Q_USUARIO, {"login": USUARIO})["user"]
    repos = buscar_repos()
    SAIDA.mkdir(parents=True, exist_ok=True)
    arquivos = {
        "stats.svg": card_stats(usuario, repos),
        "linguagens.svg": card_linguagens(repos),
        "atividade.svg": card_atividade(usuario),
    }
    for nome, svg in arquivos.items():
        (SAIDA / nome).write_text(svg, encoding="utf-8", newline="\n")
        print(f"gerado: assets/stats/{nome}")


if __name__ == "__main__":
    main()

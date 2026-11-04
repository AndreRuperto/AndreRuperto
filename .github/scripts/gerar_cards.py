"""Gera os cards de estatísticas do perfil como SVGs dentro do próprio repositório.

Substitui os serviços públicos (github-readme-stats, activity-graph e
streak-stats), que vivem fora do ar por limite de uso. Usa a API GraphQL do
GitHub com o token em GITHUB_TOKEN e grava em assets/stats/:

- resumo.svg     → contribuições totais, commits do ano, PRs, estrelas e sequências
- linguagens.svg → linguagens mais usadas nos repositórios próprios
- atividade.svg  → contribuições dos últimos 31 dias

Os três seguem uma grade de 900 px: resumo (495) + linguagens (395) na primeira
linha, com a mesma altura, e atividade (900) ocupando a segunda.
Cores no tema "merko".
"""

import json
import os
import sys
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from xml.sax.saxutils import escape

USUARIO = "AndreRuperto"
NOME = "André Ruperto"
SAIDA = Path(__file__).resolve().parents[2] / "assets" / "stats"
LINGUAGENS_IGNORADAS: set[str] = set()  # ex.: {"Jupyter Notebook"}
QTD_LINGUAGENS = 6
NOMES_CURTOS = {"Jupyter Notebook": "Jupyter"}

# Grade: as duas colunas da primeira linha somam a largura do gráfico.
LARGURA_TOTAL = 900
LARGURA_RESUMO = 495
LARGURA_LINGUAGENS = LARGURA_TOTAL - LARGURA_RESUMO - 10
ALTURA_LINHA1 = 195

TEMA = {
    "fundo": "#0a0f0b",
    "borda": "#e4e2e2",
    "titulo": "#abd200",
    "texto": "#68b587",
    "icone": "#b7d364",
    "grade": "#1f2a21",
}
FONTE = "'Segoe UI', Ubuntu, 'Helvetica Neue', Sans-Serif"
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


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
query($login: String!, $desde: DateTime!) {
  user(login: $login) {
    createdAt
    pullRequests { totalCount }
    ano: contributionsCollection(from: $desde) {
      totalCommitContributions
      restrictedContributionsCount
    }
  }
}
"""

Q_CALENDARIO = """
query($login: String!, $de: DateTime!, $ate: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $de, to: $ate) {
      contributionCalendar { weeks { contributionDays { date contributionCount } } }
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


def buscar_calendario(criado_em: str) -> list[tuple[date, int]]:
    """Todos os dias com contribuições desde a criação da conta (a API limita a 1 ano por consulta)."""
    agora = datetime.now(timezone.utc)
    dias: dict[date, int] = {}
    for ano in range(int(criado_em[:4]), agora.year + 1):
        ate = agora.isoformat() if ano == agora.year else f"{ano}-12-31T23:59:59Z"
        dados = graphql(Q_CALENDARIO, {"login": USUARIO, "de": f"{ano}-01-01T00:00:00Z", "ate": ate})
        for semana in dados["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]:
            for d in semana["contributionDays"]:
                dias[date.fromisoformat(d["date"])] = d["contributionCount"]
    hoje = agora.date()
    return sorted((d, n) for d, n in dias.items() if d <= hoje)


def sequencias(dias: list[tuple[date, int]]) -> dict:
    """Sequência atual (pode terminar ontem, se hoje ainda não teve contribuição) e recorde."""
    recorde = (0, None, None)
    inicio, tamanho = None, 0
    for d, n in dias:
        if n > 0:
            inicio = inicio or d
            tamanho += 1
            if tamanho > recorde[0]:
                recorde = (tamanho, inicio, d)
        else:
            inicio, tamanho = None, 0

    atual, fim = 0, None
    restantes = list(dias)
    if restantes and restantes[-1][1] == 0:
        restantes.pop()  # hoje ainda sem contribuição não quebra a sequência
    for d, n in reversed(restantes):
        if n == 0:
            break
        atual += 1
        fim = fim or d
    comeco = fim - timedelta(days=atual - 1) if atual else None
    return {"atual": atual, "atual_de": comeco, "atual_ate": fim,
            "recorde": recorde[0], "recorde_de": recorde[1], "recorde_ate": recorde[2]}


# ───────────────────────────── SVG ─────────────────────────────

def moldura(largura: int, altura: int, titulo: str, conteudo: str, rotulo: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="{altura}" viewBox="0 0 {largura} {altura}" role="img" aria-label="{escape(rotulo)}">
  <title>{escape(rotulo)}</title>
  <style>
    .titulo {{ font: 600 18px {FONTE}; fill: {TEMA['titulo']}; }}
    .texto  {{ font: 600 14px {FONTE}; fill: {TEMA['texto']}; }}
    .valor  {{ font: 700 14px {FONTE}; fill: {TEMA['titulo']}; }}
    .grande {{ font: 700 28px {FONTE}; fill: {TEMA['titulo']}; }}
    .menor  {{ font: 400 12px {FONTE}; fill: {TEMA['texto']}; }}
  </style>
  <rect x="0.5" y="0.5" rx="10" width="{largura - 1}" height="{altura - 1}" fill="{TEMA['fundo']}" stroke="{TEMA['borda']}" stroke-opacity="0.8"/>
  <text x="25" y="35" class="titulo">{escape(titulo)}</text>
{conteudo}
</svg>
"""


def fmt(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def fmt_data(d: date | None) -> str:
    return f"{d.day} {MESES[d.month - 1]}" if d else "—"


def fmt_periodo(de: date | None, ate: date | None) -> str:
    if not de:
        return "—"
    if de == ate:
        return fmt_data(de)
    ano = f" {ate.year}" if ate.year != date.today().year else ""
    return f"{fmt_data(de)} – {fmt_data(ate)}{ano}"


def card_resumo(usuario: dict, repos: list[dict], dias: list[tuple[date, int]]) -> str:
    seq = sequencias(dias)
    ano = usuario["ano"]
    linhas = [
        ("Contribuições totais", fmt(sum(n for _, n in dias))),
        (f"Commits em {date.today().year}", fmt(ano["totalCommitContributions"] + ano["restrictedContributionsCount"])),
        ("Pull requests", fmt(usuario["pullRequests"]["totalCount"])),
        ("Estrelas recebidas", fmt(sum(r["stargazerCount"] for r in repos))),
        ("Recorde de sequência", f"{seq['recorde']} dias"),
    ]
    partes = []
    for i, (rotulo, valor) in enumerate(linhas):
        y = 72 + i * 25
        partes.append(
            f'  <circle cx="31" cy="{y - 5}" r="4" fill="{TEMA["icone"]}"/>\n'
            f'  <text x="45" y="{y}" class="texto">{escape(rotulo)}</text>\n'
            f'  <text x="300" y="{y}" text-anchor="end" class="valor">{escape(valor)}</text>'
        )
    cx, cy, r = 400, 100, 42
    partes.append(
        f'  <line x1="330" x2="330" y1="55" y2="175" stroke="{TEMA["grade"]}" stroke-width="2"/>\n'
        f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{TEMA["titulo"]}" stroke-width="5"/>\n'
        f'  <text x="{cx}" y="{cy + 10}" text-anchor="middle" class="grande">{seq["atual"]}</text>\n'
        f'  <text x="{cx}" y="{cy + r + 22}" text-anchor="middle" class="valor">Sequência atual</text>\n'
        f'  <text x="{cx}" y="{cy + r + 40}" text-anchor="middle" class="menor">{escape(fmt_periodo(seq["atual_de"], seq["atual_ate"]))}</text>'
    )
    return moldura(LARGURA_RESUMO, ALTURA_LINHA1, f"Resumo do GitHub de {NOME}", "\n".join(partes),
                   f"Resumo do GitHub de {NOME}")


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

    barra_larg = LARGURA_LINGUAGENS - 50
    partes = [f'  <mask id="barra"><rect x="25" y="60" width="{barra_larg}" height="8" rx="4" fill="white"/></mask>',
              '  <g mask="url(#barra)">']
    x = 25.0
    for _, (tam, cor) in top:
        w = barra_larg * tam / soma
        partes.append(f'    <rect x="{x:.2f}" y="60" width="{w:.2f}" height="8" fill="{cor}"/>')
        x += w
    partes.append("  </g>")
    coluna = barra_larg / 2
    for i, (nome, (tam, cor)) in enumerate(top):
        col, lin = i % 2, i // 2
        lx, ly = 31 + col * coluna, 105 + lin * 30
        pct = f"{tam / soma * 100:.1f}".replace(".", ",")
        partes.append(
            f'  <circle cx="{lx:.1f}" cy="{ly - 5}" r="5" fill="{cor}"/>\n'
            f'  <text x="{lx + 13:.1f}" y="{ly}" class="texto">{escape(NOMES_CURTOS.get(nome, nome))}</text>\n'
            f'  <text x="{lx + coluna - 15:.1f}" y="{ly}" text-anchor="end" class="menor">{pct}%</text>'
        )
    return moldura(LARGURA_LINGUAGENS, ALTURA_LINHA1, "Linguagens mais usadas", "\n".join(partes),
                   f"Linguagens mais usadas por {NOME}")


def card_atividade(dias_todos: list[tuple[date, int]]) -> str:
    dias = dias_todos[-31:]
    valores = [n for _, n in dias]

    largura, altura = LARGURA_TOTAL, 300
    x0, x1, y0, y1 = 60, largura - 30, 60, altura - 50
    passo_y = max(1, -(-max(max(valores), 1) // 4))
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
    for i, (d, v) in enumerate(dias):
        partes.append(f'  <circle cx="{px(i):.1f}" cy="{py(v):.1f}" r="3.5" fill="{TEMA["icone"]}"><title>{d.isoformat()}: {v}</title></circle>')
        if i % 2 == 0 or i == len(dias) - 1:
            partes.append(f'  <text x="{px(i):.1f}" y="{y1 + 22}" text-anchor="middle" class="menor">{d.day:02d}</text>')
    partes.append(f'  <text x="{largura - 30}" y="35" text-anchor="end" class="menor">{fmt(sum(valores))} contribuições</text>')
    return moldura(largura, altura, "Atividade nos últimos 31 dias", "\n".join(partes),
                   f"Gráfico de contribuições de {NOME} nos últimos 31 dias")


def main() -> None:
    usuario = graphql(Q_USUARIO, {"login": USUARIO, "desde": f"{date.today().year}-01-01T00:00:00Z"})["user"]
    dias = buscar_calendario(usuario["createdAt"])
    repos = buscar_repos()
    SAIDA.mkdir(parents=True, exist_ok=True)
    arquivos = {
        "resumo.svg": card_resumo(usuario, repos, dias),
        "linguagens.svg": card_linguagens(repos),
        "atividade.svg": card_atividade(dias),
    }
    for nome, svg in arquivos.items():
        (SAIDA / nome).write_text(svg, encoding="utf-8", newline="\n")
        print(f"gerado: assets/stats/{nome}")
    antigo = SAIDA / "stats.svg"
    if antigo.exists():
        antigo.unlink()


if __name__ == "__main__":
    main()

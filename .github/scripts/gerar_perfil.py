"""Gera as imagens fixas do topo do perfil em assets/perfil/.

O GitHub não carrega fontes externas dentro de um SVG exibido no README, então
todo texto é convertido em contornos a partir de assets/fontes/ (Sora e Fira
Code, licença OFL). Visual conforme a prancha "Portfólio · Identidade e sistema
de design": carvão, laranja Brasa, Sora nos textos e Fira Code nos dados.

Rodar à mão depois de editar os textos abaixo (não faz parte de nenhum workflow):

    pip install fonttools
    python .github/scripts/gerar_perfil.py

Cada imagem larga tem uma versão "-mobile", trocada pelo <picture> do README.
"""

from pathlib import Path
from xml.sax.saxutils import escape

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

RAIZ = Path(__file__).resolve().parents[2]
FONTES = {"sora": RAIZ / "assets/fontes/Sora.ttf", "mono": RAIZ / "assets/fontes/FiraCode.ttf"}
SAIDA = RAIZ / "assets/perfil"

CARVAO_950, CARVAO_900, CARVAO_800 = "#120F0D", "#1A1614", "#292220"
BORDA, PAPEL, APOIO = "#332C28", "#FBFAF9", "#988881"
BRASA, CORAL = "#FF7E29", "#F56A47"

W, WM = 960, 420  # largura das versões de desktop e de celular

# ───────────────────────────── Conteúdo ─────────────────────────────

FRASE = "Cientista de dados e desenvolvedor fullstack. Tiro trabalho manual do caminho."
SITE = "andreruperto.dev"

NUMEROS = [
    ("9,38", "CR no bacharelado em Ciência da Computação (UDF), com láurea acadêmica"),
    ("~3 anos", "em dados e desenvolvimento: MGI, Resende Mori Hutchison e freelas"),
    ("120 h/mês", "de trabalho manual economizadas com pipelines de dados"),
    ("30+", "módulos em um sistema fullstack interno (React, Node.js, PostgreSQL)"),
]

EXPERIENCIA = [
    ("Desenvolvedor FullStack Júnior", "Resende Mori Hutchison", "ago/2025 – out/2026"),
    ("Desenvolvedor Web Freelancer", "Autônomo", "fev/2026 – mai/2026"),
    ("Analista de Dados Júnior", "Resende Mori Hutchison", "mai/2025 – ago/2025"),
    ("Estagiário, Equipe de Dados", "MGI", "jan/2024 – mai/2025"),
]

CONTATOS = [  # (arquivo, rótulo, detalhe em mono, ícone, botão cheio?)
    ("portfolio", "Portfólio", SITE, "globo", True),
    ("linkedin", "LinkedIn", "andrerup", "linkedin", False),
    ("email", "E-mail", "contato@andreruperto.dev", "carta", False),
    ("instagram", "Instagram", "", "instagram", False),
]

ICONES = {
    "globo": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.8 3 2.8 15 0 18M12 3c-2.8 3-2.8 15 0 18"/>',
    "linkedin": '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M8 10.5V17M8 7.2v.1M12 17v-6.5M12 13.5c0-4 5-4 5 0V17"/>',
    "carta": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3.5 7l8.5 6.5L20.5 7"/>',
    "instagram": '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><path d="M17.2 6.8v.1"/>',
}

# ───────────────────────────── Texto em contornos ─────────────────────────────

_cache: dict = {}


def _fonte(nome: str, peso: int):
    if (nome, peso) not in _cache:
        f = instantiateVariableFont(TTFont(FONTES[nome]), {"wght": peso})
        _cache[(nome, peso)] = (f, f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm)
    return _cache[(nome, peso)]


def _n(v: float) -> str:
    return f"{v:.1f}".rstrip("0").rstrip(".")


def largura(texto: str, fonte="sora", tam=14, peso=400, esp=0.0) -> float:
    _, glifos, cmap, upm = _fonte(fonte, peso)
    return sum(glifos[cmap[ord(c)]].width * tam / upm + esp for c in texto) - (esp if texto else 0)


_glifos_usados: dict = {}  # (fonte, peso, glifo) → (id, contorno); esvaziado a cada svg()


def texto(t: str, x: float, y: float, fonte="sora", tam=14, peso=400, cor=PAPEL, ancora="start", esp=0.0) -> str:
    """O texto `t` em contornos; (x, y) é o início da linha de base.

    Cada glifo é desenhado uma vez em <defs> e repetido com <use>, o que deixa o
    arquivo bem menor. Com degradê (`cor="url(#…)"`) vai um <path> direto, porque
    o degradê é medido nas coordenadas da imagem, não nas do glifo.
    """
    _, glifos, cmap, upm = _fonte(fonte, peso)
    k = tam / upm
    if ancora == "end":
        x -= largura(t, fonte, tam, peso, esp)
    if cor.startswith("url("):
        caneta = SVGPathPen(glifos, ntos=_n)
        for c in t:
            g = glifos[cmap[ord(c)]]
            g.draw(TransformPen(caneta, (k, 0, 0, -k, x, y)))
            x += g.width * k + esp
        return f'<path fill="{cor}" d="{caneta.getCommands()}"/>'
    usos, avanco = [], 0.0
    for c in t:
        nome = cmap[ord(c)]
        g = glifos[nome]
        chave = (fonte, peso, nome)
        if chave not in _glifos_usados:
            caneta = SVGPathPen(glifos, ntos=lambda v: str(round(v)))
            g.draw(caneta)
            _glifos_usados[chave] = (f"g{len(_glifos_usados)}", caneta.getCommands())
        if _glifos_usados[chave][1]:
            usos.append(f'<use href="#{_glifos_usados[chave][0]}" x="{round(avanco)}"/>')
        avanco += g.width + esp / k
    return f'<g fill="{cor}" transform="translate({_n(x)} {_n(y)}) scale({k:.5f} -{k:.5f})">{"".join(usos)}</g>'


def trechos(partes: list[tuple[str, str]], x: float, y: float, **kw) -> str:
    """Vários trechos de cores diferentes na mesma linha."""
    saida = []
    opcoes = {k: v for k, v in kw.items() if k != "cor"}
    for t, cor in partes:
        saida.append(texto(t, x, y, cor=cor, **opcoes))
        x += largura(t, opcoes.get("fonte", "sora"), opcoes.get("tam", 14), opcoes.get("peso", 400), opcoes.get("esp", 0.0))
        x += opcoes.get("esp", 0.0)
    return "\n".join(saida)


def quebrar(t: str, max_larg: float, **kw) -> list[str]:
    linhas, atual = [], ""
    for palavra in t.split():
        tentativa = f"{atual} {palavra}".strip()
        if atual and largura(tentativa, **kw) > max_larg:
            linhas.append(atual)
            atual = palavra
        else:
            atual = tentativa
    return linhas + [atual]


def paragrafo(t: str, x: float, y: float, max_larg: float, entrelinha: float, cor=PAPEL, **kw) -> tuple[str, float]:
    """Texto com quebra de linha; devolve o SVG e a linha de base da última linha."""
    linhas = quebrar(t, max_larg, **kw)
    svg = "\n".join(texto(l, x, y + i * entrelinha, cor=cor, **kw) for i, l in enumerate(linhas))
    return svg, y + (len(linhas) - 1) * entrelinha


def caixa(x, y, w, h, raio, fundo, borda=BORDA) -> str:
    traco = f' stroke="{borda}"' if borda else ""
    return f'<rect x="{_n(x)}" y="{_n(y)}" width="{_n(w)}" height="{_n(h)}" rx="{raio}" fill="{fundo}"{traco}/>'


def svg(w: float, h: float, titulo: str, corpo: list[str], defs: str = "") -> str:
    w, h = round(w), round(h)
    glifos = "".join(f'<path id="{i}" d="{d}"/>' for i, d in _glifos_usados.values() if d)
    _glifos_usados.clear()
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t">\n'
        f'<title id="t">{escape(titulo)}</title>\n{defs}<defs>{glifos}</defs>\n' + "\n".join(corpo) + "\n</svg>\n"
    )


def moldura(w: float, h: float) -> str:
    return caixa(0.5, 0.5, w - 1, h - 1, 16, CARVAO_950)


# ───────────────────────────── Cabeçalho ─────────────────────────────

def _marca(x: float, base: float, tam: float) -> tuple[str, str]:
    """A marca "André." — nome no degradê Brasa → Coral, ponto em Papel."""
    larg = largura("André", "sora", tam, 800, -tam * 0.043)
    defs = (
        f'<defs><linearGradient id="brasa" gradientUnits="userSpaceOnUse" x1="{_n(x)}" y1="{_n(base - tam * 0.75)}" '
        f'x2="{_n(x + larg)}" y2="{_n(base)}"><stop stop-color="{BRASA}"/><stop offset="1" stop-color="{CORAL}"/></linearGradient></defs>\n'
    )
    nome = texto("André", x, base, "sora", tam, 800, "url(#brasa)", esp=-tam * 0.043)
    ponto = texto(".", x + larg, base, "sora", tam, 800, PAPEL)
    return defs, nome + "\n" + ponto


def _grafico(x: float, y: float, w: float) -> tuple[list[str], float]:
    """Cartão com as duas barras do modelo do PNCP; devolve o SVG e a altura."""
    h, m = 260, 24
    dentro, direita = w - 2 * m, x + w - m
    p = [
        caixa(x, y, w, h, 12, CARVAO_900),
        texto("MODELO DE CREDENCIAMENTO · PNCP", x + m, y + 32, "mono", 11, 400, APOIO, esp=1.4),
        texto("Pedidos analisados manualmente", x + m, y + 55, "sora", 15, 600),
        texto("Hoje", x + m, y + 110, "sora", 13, 400, APOIO),
        texto("1.494", direita, y + 110, "mono", 20, 600, PAPEL, "end"),
        caixa(x + m, y + 119, dentro, 14, 3, APOIO, None),
        texto("Com o modelo (estimado)", x + m, y + 164, "sora", 13, 400, APOIO),
        texto("97", direita, y + 164, "mono", 20, 600, BRASA, "end"),
        caixa(x + m, y + 173, dentro, 14, 3, CARVAO_800, None),
        caixa(x + m, y + 173, dentro * 97 / 1494, 14, 3, BRASA, None),
        texto("93,5% a menos · acurácia de 94,65%", x + m, y + 236, "mono", 12, 400, APOIO),
    ]
    return p, h


TITULO_HERO = (
    "André Ruperto, cientista de dados e desenvolvedor fullstack. Modelo de credenciamento do PNCP: "
    "pedidos analisados manualmente cairiam de 1.494 para 97 (93,5% a menos), com acurácia de 94,65%."
)


def hero() -> str:
    h = 340
    defs, marca = _marca(44, 142, 92)
    frase, _ = paragrafo(FRASE, 46, 184, 430, 26, fonte="sora", tam=18, peso=500)
    grafico, _ = _grafico(W - 44 - 380, 40, 380)
    corpo = [moldura(W, h), texto("ANDRÉ RUPERTO", 46, 52, "mono", 12, 500, APOIO, esp=1.8), marca, frase,
             texto(SITE, 46, 297, "mono", 13, 400, APOIO), *grafico]
    return svg(W, h, TITULO_HERO, corpo, defs)


def hero_mobile() -> str:
    m = 24
    defs, marca = _marca(m - 2, 122, 84)
    frase, fim = paragrafo(FRASE, m, 162, WM - 2 * m, 25, fonte="sora", tam=17, peso=500)
    grafico, alt = _grafico(m, fim + 60, WM - 2 * m)
    h = fim + 60 + alt + m
    corpo = [moldura(WM, h), texto("ANDRÉ RUPERTO", m, 40, "mono", 12, 500, APOIO, esp=1.8), marca, frase,
             texto(SITE, m, fim + 34, "mono", 13, 400, APOIO), *grafico]
    return svg(WM, h, TITULO_HERO, corpo, defs)


# ───────────────────────────── Números do "Sobre mim" ─────────────────────────────

def numeros(largura_total: float, colunas: int) -> str:
    vao, m = 12, 18
    w = (largura_total - vao * (colunas - 1)) / colunas
    opcoes = dict(fonte="sora", tam=13, peso=400)
    maior = max(len(quebrar(d, w - 2 * m, **opcoes)) for _, d in NUMEROS)
    h = 62 + maior * 19.5 + 10
    corpo = []
    for i, (valor, desc) in enumerate(NUMEROS):
        x, y = (i % colunas) * (w + vao), (i // colunas) * (h + vao)
        corpo += [caixa(x + 0.5, y + 0.5, w - 1, h - 1, 12, CARVAO_900),
                  texto(valor, x + m, y + 44, "mono", 26, 600),
                  paragrafo(desc, x + m, y + 70, w - 2 * m, 19.5, APOIO, **opcoes)[0]]
    linhas = -(-len(NUMEROS) // colunas)
    titulo = "Em números: " + "; ".join(f"{v} {d}" for v, d in NUMEROS) + "."
    return svg(largura_total, linhas * h + (linhas - 1) * vao, titulo, corpo)


# ───────────────────────────── Experiência como consulta ─────────────────────────────

CONSULTA = [
    [("SELECT", BRASA), (" cargo, onde, periodo", PAPEL)],
    [("FROM", BRASA), (" experiencia", PAPEL)],
    [("ORDER BY", BRASA), (" periodo ", PAPEL), ("DESC", BRASA), (";", PAPEL)],
]
RODAPE_CONSULTA = f"{len(EXPERIENCIA)} linhas · quase 3 anos"
TITULO_EXP = "Experiência, da mais recente para a mais antiga: " + "; ".join(
    f"{c}, {o}, {p}" for c, o, p in EXPERIENCIA) + "."


def _consulta(x: float, y: float, w: float, h: float) -> list[str]:
    p = [caixa(x, y, w, h, 12, CARVAO_900)]
    for i, linha in enumerate(CONSULTA):
        p.append(trechos(linha, x + 20, y + 34 + i * 24.5, fonte="mono", tam=14, peso=400))
    p.append(texto(RODAPE_CONSULTA, x + 20, y + h - 18, "mono", 12, 400, APOIO))
    return p


def experiencia() -> str:
    m, cab, lin = 24, 36, 46
    alt = cab + lin * len(EXPERIENCIA)
    h = alt + 2 * m
    tx, tw = m + 268 + 16, W - 2 * m - 268 - 16
    colunas = [tx + 18, tx + 18 + 250, tx + 18 + 250 + 190]
    corpo = [moldura(W, h), *_consulta(m, m, 268, alt), caixa(tx, m, tw, alt, 12, CARVAO_900),
             f'<path d="M{_n(tx)} {m + cab}.5h{_n(tw)}" stroke="{BORDA}"/>']
    for rotulo, cx in zip(("CARGO", "ONDE", "PERÍODO"), colunas):
        corpo.append(texto(rotulo, cx, m + 23, "mono", 11, 400, APOIO, esp=1.2))
    for i, (cargo, onde, periodo) in enumerate(EXPERIENCIA):
        y = m + cab + i * lin
        if i:
            corpo.append(f'<path d="M{_n(tx + 1)} {_n(y)}.5h{_n(tw - 2)}" stroke="{CARVAO_800}"/>')
        corpo += [texto(cargo, colunas[0], y + 28, "sora", 13.5, 600),
                  texto(onde, colunas[1], y + 28, "sora", 13.5, 400, APOIO),
                  texto(periodo, colunas[2], y + 28, "mono", 12, 400, APOIO)]
    return svg(W, h, TITULO_EXP, corpo)


def experiencia_mobile() -> str:
    m, lin, alt_consulta = 16, 62, 132
    tw = WM - 2 * m
    ty = m + alt_consulta + 12
    alt = lin * len(EXPERIENCIA)
    h = ty + alt + m
    corpo = [moldura(WM, h), *_consulta(m, m, tw, alt_consulta), caixa(m, ty, tw, alt, 12, CARVAO_900)]
    for i, (cargo, onde, periodo) in enumerate(EXPERIENCIA):
        y = ty + i * lin
        if i:
            corpo.append(f'<path d="M{m + 1} {_n(y)}.5h{tw - 2}" stroke="{CARVAO_800}"/>')
        corpo += [texto(cargo, m + 18, y + 26, "sora", 15, 600),
                  texto(onde, m + 18, y + 47, "sora", 13, 400, APOIO),
                  texto(periodo, m + tw - 18, y + 47, "mono", 12, 400, APOIO, "end")]
    return svg(WM, h, TITULO_EXP, corpo)


# ───────────────────────────── Botões de contato ─────────────────────────────

def contato(rotulo: str, detalhe: str, icone: str, cheio: bool) -> str:
    h, m = 44, 16
    cor, cor_det = (CARVAO_950, CARVAO_950) if cheio else (PAPEL, APOIO)
    x_rot = m + 18 + 10
    x_det = x_rot + largura(rotulo, "sora", 14, 600 if cheio else 500) + 10
    w = x_det + largura(detalhe, "mono", 12, 500 if cheio else 400) + m if detalhe else x_det - 10 + m
    fundo = caixa(0, 0, w, h, 10, BRASA, None) if cheio else caixa(0.5, 0.5, w - 1, h - 1, 10, CARVAO_950)
    corpo = [
        fundo,
        f'<g transform="translate({m} 13) scale(0.75)" fill="none" stroke="{cor_det}" stroke-width="2.4" '
        f'stroke-linecap="round" stroke-linejoin="round">{ICONES[icone]}</g>',
        texto(rotulo, x_rot, 27, "sora", 14, 600 if cheio else 500, cor),
    ]
    if detalhe:
        corpo.append(texto(detalhe, x_det, 26.5, "mono", 12, 500 if cheio else 400, cor_det))
    return svg(w, h, f"{rotulo}: {detalhe}" if detalhe else rotulo, corpo)


def main() -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    arquivos = {
        "hero.svg": hero(),
        "hero-mobile.svg": hero_mobile(),
        "numeros.svg": numeros(W, 4),
        "numeros-mobile.svg": numeros(WM, 2),
        "experiencia.svg": experiencia(),
        "experiencia-mobile.svg": experiencia_mobile(),
    }
    for nome, rotulo, detalhe, icone, cheio in CONTATOS:
        arquivos[f"contato-{nome}.svg"] = contato(rotulo, detalhe, icone, cheio)
    for nome, conteudo in arquivos.items():
        (SAIDA / nome).write_text(conteudo, encoding="utf-8", newline="\n")
        print(f"gerado: assets/perfil/{nome} ({len(conteudo) // 1024} KB)")


if __name__ == "__main__":
    main()

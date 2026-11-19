"""Gera as imagens fixas do topo do perfil em assets/perfil/.

O GitHub não carrega fontes externas dentro de um SVG exibido no README, então
todo texto é convertido em contornos a partir de assets/fontes/ (Sora e Fira
Code, licença OFL). Visual conforme a prancha "Portfólio · Identidade e sistema
de design": carvão, laranja Brasa, Sora nos textos e Fira Code nos dados.

Rodar à mão depois de editar os textos abaixo (não faz parte de nenhum workflow):

    pip install fonttools
    python .github/scripts/gerar_perfil.py

Cada imagem larga tem uma versão "-mobile", trocada pelo <picture> do README, e
tudo sai em português e em inglês (sufixo "-en", usado pelo README.en.md).
"""

import re
from itertools import product
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

SITE = "andreruperto.dev"

TEXTOS = {
    "pt": {
        "frase": "Cientista de dados e desenvolvedor fullstack. Tiro trabalho manual do caminho.",
        "titulo_hero": "André Ruperto, cientista de dados e desenvolvedor fullstack. Modelo de credenciamento do PNCP: "
                       "pedidos analisados manualmente cairiam de 1.494 para 97 (93,5% a menos), com acurácia de 94,65%.",
        "grafico": ("MODELO DE CREDENCIAMENTO · PNCP", "Pedidos analisados manualmente", "Hoje", "1.494",
                    "Com o modelo (estimado)", "93,5% a menos · acurácia de 94,65%"),
        "numeros_titulo": "Em números: ",
        "numeros": [
            ("9,38", "CR no bacharelado em Ciência da Computação (UDF), com láurea acadêmica"),
            ("~3 anos", "em dados e desenvolvimento: MGI, Resende Mori Hutchison e freelas"),
            ("120 h/mês", "de trabalho manual economizadas com pipelines de dados"),
            ("30+", "módulos em um sistema fullstack interno (React, Node.js, PostgreSQL)"),
        ],
        "experiencia_titulo": "Experiência, da mais recente para a mais antiga: ",
        "experiencia": [
            ("Desenvolvedor FullStack Júnior", "Resende Mori Hutchison", "ago/2025 – out/2026"),
            ("Desenvolvedor Web Freelancer", "Autônomo", "fev/2026 – mai/2026"),
            ("Analista de Dados Júnior", "Resende Mori Hutchison", "mai/2025 – ago/2025"),
            ("Estagiário, Equipe de Dados", "MGI", "jan/2024 – mai/2025"),
        ],
        "consulta": (" cargo, onde, periodo", " experiencia", " periodo "),
        "colunas": ("CARGO", "ONDE", "PERÍODO"),
        "rodape_consulta": "{n} linhas · quase 3 anos",
        "contatos": {"portfolio": "Portfólio", "email": "E-mail"},
        "skills_titulo": "Skills técnicas. ",
        "skills": {},
    },
    "en": {
        "frase": "Data scientist and full-stack developer. I take manual work out of the way.",
        "titulo_hero": "André Ruperto, data scientist and full-stack developer. Credentialing model for PNCP, Brazil's public "
                       "procurement portal: requests reviewed manually would drop from 1,494 to 97 (93.5% fewer), at 94.65% accuracy.",
        "grafico": ("CREDENTIALING MODEL · PNCP", "Requests reviewed manually", "Today", "1,494",
                    "With the model (estimated)", "93.5% fewer · 94.65% accuracy"),
        "numeros_titulo": "In numbers: ",
        "numeros": [
            ("9.38", "GPA out of 10 in the Computer Science bachelor's degree (UDF), with academic honors"),
            ("~3 years", "in data and development: MGI, Resende Mori Hutchison and freelance work"),
            ("120 h/month", "of manual work saved with data pipelines"),
            ("30+", "modules in an internal full-stack system (React, Node.js, PostgreSQL)"),
        ],
        "experiencia_titulo": "Experience, most recent first: ",
        "experiencia": [
            ("Junior Full-Stack Developer", "Resende Mori Hutchison", "Aug 2025 – Oct 2026"),
            ("Freelance Web Developer", "Self-employed", "Feb 2026 – May 2026"),
            ("Junior Data Analyst", "Resende Mori Hutchison", "May 2025 – Aug 2025"),
            ("Intern, Data Team", "MGI", "Jan 2024 – May 2025"),
        ],
        "consulta": (" role, company, period", " experience", " period "),
        "colunas": ("ROLE", "COMPANY", "PERIOD"),
        "rodape_consulta": "{n} rows · almost 3 years",
        "contatos": {"portfolio": "Portfolio", "email": "Email"},
        "skills_titulo": "Technical skills. ",
        "skills": {
            "Linguagens": "Languages", "Dados, Machine Learning e IA": "Data, Machine Learning & AI",
            "Engenharia de dados, BI e automação": "Data engineering, BI & automation",
            "Frontend e desktop": "Frontend & desktop", "Backend e bancos de dados": "Backend & databases",
            "Ferramentas e DevOps": "Tools & DevOps", "LLMs e RAG": "LLMs & RAG",
            "Modelagem de dados": "Data modeling", "APIs REST": "REST APIs",
        },
    },
}
L = TEXTOS["pt"]  # textos do idioma em geração; main() troca a cada idioma

CONTATOS = [  # (arquivo, rótulo padrão, detalhe em mono, ícone, botão cheio?)
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
    rotulo, titulo, hoje, valor_hoje, com_modelo, rodape = L["grafico"]
    p = [
        caixa(x, y, w, h, 12, CARVAO_900),
        texto(rotulo, x + m, y + 32, "mono", 11, 400, APOIO, esp=1.4),
        texto(titulo, x + m, y + 55, "sora", 15, 600),
        texto(hoje, x + m, y + 110, "sora", 13, 400, APOIO),
        texto(valor_hoje, direita, y + 110, "mono", 20, 600, PAPEL, "end"),
        caixa(x + m, y + 119, dentro, 14, 3, APOIO, None),
        texto(com_modelo, x + m, y + 164, "sora", 13, 400, APOIO),
        texto("97", direita, y + 164, "mono", 20, 600, BRASA, "end"),
        caixa(x + m, y + 173, dentro, 14, 3, CARVAO_800, None),
        caixa(x + m, y + 173, dentro * 97 / 1494, 14, 3, BRASA, None),
        texto(rodape, x + m, y + 236, "mono", 12, 400, APOIO),
    ]
    return p, h


def hero() -> str:
    h = 340
    defs, marca = _marca(44, 142, 92)
    frase, _ = paragrafo(L["frase"], 46, 184, 430, 26, fonte="sora", tam=18, peso=500)
    grafico, _ = _grafico(W - 44 - 380, 40, 380)
    corpo = [moldura(W, h), texto("ANDRÉ RUPERTO", 46, 52, "mono", 12, 500, APOIO, esp=1.8), marca, frase,
             texto(SITE, 46, 297, "mono", 13, 400, APOIO), *grafico]
    return svg(W, h, L["titulo_hero"], corpo, defs)


def hero_mobile() -> str:
    m = 24
    defs, marca = _marca(m - 2, 122, 84)
    frase, fim = paragrafo(L["frase"], m, 162, WM - 2 * m, 25, fonte="sora", tam=17, peso=500)
    grafico, alt = _grafico(m, fim + 60, WM - 2 * m)
    h = fim + 60 + alt + m
    corpo = [moldura(WM, h), texto("ANDRÉ RUPERTO", m, 40, "mono", 12, 500, APOIO, esp=1.8), marca, frase,
             texto(SITE, m, fim + 34, "mono", 13, 400, APOIO), *grafico]
    return svg(WM, h, L["titulo_hero"], corpo, defs)


# ───────────────────────────── Números do "Sobre mim" ─────────────────────────────

def numeros(largura_total: float, colunas: int) -> str:
    vao, m = 12, 18
    w = (largura_total - vao * (colunas - 1)) / colunas
    opcoes = dict(fonte="sora", tam=13, peso=400)
    maior = max(len(quebrar(d, w - 2 * m, **opcoes)) for _, d in L["numeros"])
    h = 62 + maior * 19.5 + 10
    corpo = []
    for i, (valor, desc) in enumerate(L["numeros"]):
        x, y = (i % colunas) * (w + vao), (i // colunas) * (h + vao)
        corpo += [caixa(x + 0.5, y + 0.5, w - 1, h - 1, 12, CARVAO_900),
                  texto(valor, x + m, y + 44, "mono", 26, 600),
                  paragrafo(desc, x + m, y + 70, w - 2 * m, 19.5, APOIO, **opcoes)[0]]
    linhas = -(-len(L["numeros"]) // colunas)
    titulo = L["numeros_titulo"] + "; ".join(f"{v} {d}" for v, d in L["numeros"]) + "."
    return svg(largura_total, linhas * h + (linhas - 1) * vao, titulo, corpo)


# ───────────────────────────── Experiência como consulta ─────────────────────────────

def _linhas_consulta() -> list:
    campos, tabela, ordem = L["consulta"]
    return [
        [("SELECT", BRASA), (campos, PAPEL)],
        [("FROM", BRASA), (tabela, PAPEL)],
        [("ORDER BY", BRASA), (ordem, PAPEL), ("DESC", BRASA), (";", PAPEL)],
    ]


def _titulo_exp() -> str:
    return L["experiencia_titulo"] + "; ".join(f"{c}, {o}, {p}" for c, o, p in L["experiencia"]) + "."


def _consulta(x: float, y: float, w: float, h: float) -> list[str]:
    p = [caixa(x, y, w, h, 12, CARVAO_900)]
    for i, linha in enumerate(_linhas_consulta()):
        p.append(trechos(linha, x + 20, y + 34 + i * 24.5, fonte="mono", tam=14, peso=400))
    p.append(texto(L["rodape_consulta"].format(n=len(L["experiencia"])), x + 20, y + h - 18, "mono", 12, 400, APOIO))
    return p


def experiencia() -> str:
    m, cab, lin = 24, 36, 46
    alt = cab + lin * len(L["experiencia"])
    h = alt + 2 * m
    tx, tw = m + 268 + 16, W - 2 * m - 268 - 16
    colunas = [tx + 18, tx + 18 + 250, tx + 18 + 250 + 190]
    corpo = [moldura(W, h), *_consulta(m, m, 268, alt), caixa(tx, m, tw, alt, 12, CARVAO_900),
             f'<path d="M{_n(tx)} {m + cab}.5h{_n(tw)}" stroke="{BORDA}"/>']
    for rotulo, cx in zip(L["colunas"], colunas):
        corpo.append(texto(rotulo, cx, m + 23, "mono", 11, 400, APOIO, esp=1.2))
    for i, (cargo, onde, periodo) in enumerate(L["experiencia"]):
        y = m + cab + i * lin
        if i:
            corpo.append(f'<path d="M{_n(tx + 1)} {_n(y)}.5h{_n(tw - 2)}" stroke="{CARVAO_800}"/>')
        corpo += [texto(cargo, colunas[0], y + 28, "sora", 13.5, 600),
                  texto(onde, colunas[1], y + 28, "sora", 13.5, 400, APOIO),
                  texto(periodo, colunas[2], y + 28, "mono", 12, 400, APOIO)]
    return svg(W, h, _titulo_exp(), corpo)


def experiencia_mobile() -> str:
    m, lin, alt_consulta = 16, 62, 132
    tw = WM - 2 * m
    ty = m + alt_consulta + 12
    alt = lin * len(L["experiencia"])
    h = ty + alt + m
    corpo = [moldura(WM, h), *_consulta(m, m, tw, alt_consulta), caixa(m, ty, tw, alt, 12, CARVAO_900)]
    for i, (cargo, onde, periodo) in enumerate(L["experiencia"]):
        y = ty + i * lin
        if i:
            corpo.append(f'<path d="M{m + 1} {_n(y)}.5h{tw - 2}" stroke="{CARVAO_800}"/>')
        corpo += [texto(cargo, m + 18, y + 26, "sora", 15, 600),
                  texto(onde, m + 18, y + 47, "sora", 13, 400, APOIO),
                  texto(periodo, m + tw - 18, y + 47, "mono", 12, 400, APOIO, "end")]
    return svg(WM, h, _titulo_exp(), corpo)


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


# ───────────────────────────── Skills ─────────────────────────────

ICONES_MARCA = RAIZ / "assets/icones"  # Simple Icons (CC0), um arquivo por tecnologia

# Ícones próprios, em traço, para o que não tem logotipo no Simple Icons.
ICONES_PROPRIOS = {
    "arvore": '<circle cx="12" cy="5" r="2"/><circle cx="6" cy="18" r="2"/><circle cx="18" cy="18" r="2"/><path d="M12 7v4M12 11l-6 5M12 11l6 5"/>',
    "raio": '<path d="M13 2L5 13h6l-1 9 8-11h-6z"/>',
    "barras": '<path d="M12 3v18M12 7h6M12 12H5M12 17h4"/>',
    "conversa": '<path d="M4 5h16v11H10l-4 4v-4H4z"/><path d="M8.5 9h7M8.5 12h4"/>',
    "lupa": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5L21 21M8 13v-2M10.5 13V8M13 13v-3.5"/>',
    "tabelas": '<rect x="3" y="4" width="8" height="6" rx="1"/><rect x="13" y="14" width="8" height="6" rx="1"/><path d="M7 10v5a2 2 0 0 0 2 2h4"/>',
    "coleta": '<rect x="3" y="3" width="18" height="11" rx="2"/><path d="M3 7h18M12 10.5V21M8.5 17.5L12 21l3.5-3.5"/>',
    "grafico_linha": '<path d="M4 4v16h16M7 15l4-5 3 3 5-7"/>',
    "grafico_barras": '<path d="M4 4v16h16M8 16v-4M12 16V8M16 16v-6"/>',
    "chaves": '<path d="M8 4c-2 0-3 1-3 3v2c0 1.5-1 3-2 3 1 0 2 1.5 2 3v2c0 2 1 3 3 3M16 4c2 0 3 1 3 3v2c0 1.5 1 3 2 3-1 0-2 1.5-2 3v2c0 2-1 3-3 3"/>',
}

SKILLS = [  # (grupo, [(nome, ícone)]) — ícone é um arquivo de assets/icones ou uma chave de ICONES_PROPRIOS
    ("Linguagens", [("Python", "python"), ("TypeScript", "typescript"), ("JavaScript", "javascript"), ("C", "c"),
                    ("C++", "cplusplus"), ("Rust", "rust"), ("HTML", "html5"), ("CSS", "css3")]),
    ("Dados, Machine Learning e IA", [
        ("pandas", "pandas"), ("NumPy", "numpy"), ("scikit-learn", "scikitlearn"), ("TensorFlow", "tensorflow"),
        ("PyTorch", "pytorch"), ("OpenCV", "opencv"), ("XGBoost", "arvore"), ("LightGBM", "raio"), ("SHAP", "barras"),
        ("Matplotlib", "grafico_linha"), ("Jupyter", "jupyter"), ("LLMs e RAG", "conversa"), ("EDA", "lupa"),
        ("Modelagem de dados", "tabelas")]),
    ("Engenharia de dados, BI e automação", [
        ("Apache Airflow", "apacheairflow"), ("Databricks", "databricks"), ("Power BI", "powerbi"), ("Qlik Sense", "qlik"),
        ("Streamlit", "streamlit"), ("Selenium", "selenium"), ("Playwright", "playwright"), ("Web scraping", "coleta"),
        ("APIs REST", "chaves"), ("GraphQL", "graphql")]),
    ("Frontend e desktop", [
        ("React", "react"), ("Vite", "vite"), ("Tailwind CSS", "tailwindcss"), ("shadcn/ui", "shadcnui"),
        ("React Router", "reactrouter"), ("TanStack Query", "reactquery"), ("Zod", "zod"), ("Recharts", "grafico_barras"),
        ("D3.js", "d3dotjs"), ("Framer Motion", "framer"), ("Three.js", "threedotjs"), ("Next.js", "nextdotjs"),
        ("Astro", "astro"), ("Electron", "electron"), ("Tauri", "tauri")]),
    ("Backend e bancos de dados", [
        ("Node.js", "nodedotjs"), ("Express", "express"), ("Bun", "bun"), ("FastAPI", "fastapi"), ("Pydantic", "pydantic"),
        ("Prisma", "prisma"), ("Drizzle ORM", "drizzle"), ("SQLAlchemy", "sqlalchemy"), ("PostgreSQL", "postgresql"),
        ("MySQL", "mysql"), ("SQLite", "sqlite"), ("Redis", "redis")]),
    ("Ferramentas e DevOps", [
        ("Git", "git"), ("GitHub", "github"), ("GitHub Actions", "githubactions"), ("Docker", "docker"),
        ("Railway", "railway"), ("Vercel", "vercel"), ("Vitest", "vitest"), ("Testing Library", "testinglibrary"),
        ("pytest", "pytest"), ("ESLint", "eslint"), ("Postman", "postman"), ("VS Code", "visualstudiocode"),
        ("Figma", "figma")]),
]


def _icone(chave: str, x: float, y: float, tam: float = 16) -> str:
    k = tam / 24
    if chave in ICONES_PROPRIOS:
        return (f'<g transform="translate({_n(x)} {_n(y)}) scale({k:.4f})" fill="none" stroke="{PAPEL}" stroke-width="2" '
                f'stroke-linecap="round" stroke-linejoin="round">{ICONES_PROPRIOS[chave]}</g>')
    fonte = (ICONES_MARCA / f"{chave}.svg").read_text(encoding="utf-8")
    d = re.search(r'<path d="([^"]+)"', fonte).group(1)
    return f'<path transform="translate({_n(x)} {_n(y)}) scale({k:.4f})" fill="{PAPEL}" d="{d}"/>'


def _cartao_skills(titulo: str, itens: list, w: float) -> tuple[list[str], float]:
    """Um cartão desenhado a partir de (0, 0); devolve as peças e a altura."""
    m, alt, vao = 18, 32, 8
    pecas, x, y = [], m, 44
    for nome, chave in itens:
        nome = L["skills"].get(nome, nome)
        larg = 10 + 16 + 7 + largura(nome, "sora", 13, 500) + 12
        if x + larg > w - m and x > m:
            x, y = m, y + alt + vao
        pecas += [caixa(x, y, larg, alt, 8, CARVAO_800, None), _icone(chave, x + 10, y + 8),
                  texto(nome, x + 33, y + 20.5, "sora", 13, 500)]
        x += larg + vao
    h = y + alt + m
    return [caixa(0.5, 0.5, w - 1, h - 1, 12, CARVAO_900),
            texto(L["skills"].get(titulo, titulo).upper(), m, 28, "mono", 11, 500, APOIO, esp=1.4), *pecas], h


def skills(largura_total: float, colunas: int) -> str:
    vao = 12
    w = (largura_total - vao * (colunas - 1)) / colunas
    cartoes = [_cartao_skills(titulo, itens, w) for titulo, itens in SKILLS]
    # testa todas as distribuições dos cartões nas colunas e fica com a mais equilibrada
    melhor = min(product(range(colunas), repeat=len(cartoes)),
                 key=lambda d: max(sum(h + vao for (_, h), c in zip(cartoes, d) if c == col) for col in range(colunas)))
    alturas, corpo = [0.0] * colunas, []
    for (pecas, h), c in zip(cartoes, melhor):
        corpo.append(f'<g transform="translate({_n(c * (w + vao))} {_n(alturas[c])})">' + "\n".join(pecas) + "</g>")
        alturas[c] += h + vao
    tr = lambda t: L["skills"].get(t, t)
    rotulo = L["skills_titulo"] + " ".join(f"{tr(t)}: {', '.join(tr(n) for n, _ in itens)}." for t, itens in SKILLS)
    return svg(largura_total, max(alturas) - vao, rotulo, corpo)


def main() -> None:
    global L
    SAIDA.mkdir(parents=True, exist_ok=True)
    for idioma, sufixo in (("pt", ""), ("en", "-en")):
        L = TEXTOS[idioma]
        arquivos = {
            "hero": hero(),
            "hero-mobile": hero_mobile(),
            "numeros": numeros(W, 4),
            "numeros-mobile": numeros(WM, 2),
            "experiencia": experiencia(),
            "experiencia-mobile": experiencia_mobile(),
            "skills": skills(W, 2),
            "skills-mobile": skills(WM, 1),
        }
        for nome, rotulo, detalhe, icone, cheio in CONTATOS:
            traduzido = L["contatos"].get(nome, rotulo)
            if idioma == "pt" or traduzido != rotulo:  # botões iguais nos dois idiomas não são duplicados
                arquivos[f"contato-{nome}"] = contato(traduzido, detalhe, icone, cheio)
        for nome, conteudo in arquivos.items():
            (SAIDA / f"{nome}{sufixo}.svg").write_text(conteudo, encoding="utf-8", newline="\n")
            print(f"gerado: assets/perfil/{nome}{sufixo}.svg ({len(conteudo) // 1024} KB)")


if __name__ == "__main__":
    main()

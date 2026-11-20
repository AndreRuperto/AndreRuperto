"""Confere os READMEs do perfil: imagens, texto alternativo, peso e links.

Uso (da raiz do repositório):

    python .github/scripts/validar_readme.py            # só o que está no repositório
    python .github/scripts/validar_readme.py --links    # também testa os links externos

Falha (código 1) quando:
- uma imagem local citada não existe;
- uma imagem está sem texto alternativo;
- uma imagem passa de LIMITE_IMAGEM ou o conjunto de um README passa de LIMITE_TOTAL;
- com --links, um link responde 404/410 ou não responde em nenhuma tentativa.

Respostas que costumam ser bloqueio a robôs (401, 403, 429, 999) viram só aviso.
"""

import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
READMES = ["README.md", "README.en.md"]
LIMITE_IMAGEM = 2 * 1024 * 1024   # bytes por imagem
LIMITE_TOTAL = 8 * 1024 * 1024    # bytes de imagens locais por README
BLOQUEIO = {401, 403, 429, 999}
TENTATIVAS = 3

IMG = re.compile(r"<img\b[^>]*>", re.I)
SOURCE = re.compile(r"<source\b[^>]*>", re.I)
ATRIBUTO = r'\b{}="([^"]*)"'
LINK = re.compile(r'href="(https?://[^"]+)"|\]\((https?://[^)\s]+)\)')

erros: list[str] = []
avisos: list[str] = []


def atributo(tag: str, nome: str) -> str | None:
    achado = re.search(ATRIBUTO.format(nome), tag)
    return achado.group(1) if achado else None


def conferir_imagens(nome: str, texto: str) -> None:
    locais: set[str] = set()
    for tag in IMG.findall(texto):
        src = atributo(tag, "src") or ""
        if not (atributo(tag, "alt") or "").strip():
            erros.append(f"{nome}: imagem sem texto alternativo: {src}")
        if not src.startswith("http"):
            locais.add(src)
    for tag in SOURCE.findall(texto):
        src = atributo(tag, "srcset") or ""
        if src and not src.startswith("http"):
            locais.add(src)

    total = 0
    for src in sorted(locais):
        arquivo = RAIZ / src
        if not arquivo.is_file():
            erros.append(f"{nome}: imagem não encontrada: {src}")
            continue
        tamanho = arquivo.stat().st_size
        total += tamanho
        if tamanho > LIMITE_IMAGEM:
            erros.append(f"{nome}: {src} tem {tamanho / 1048576:.1f} MB (limite {LIMITE_IMAGEM / 1048576:.0f} MB)")
    print(f"{nome}: {len(locais)} imagens locais, {total / 1048576:.1f} MB")
    if total > LIMITE_TOTAL:
        erros.append(f"{nome}: imagens somam {total / 1048576:.1f} MB (limite {LIMITE_TOTAL / 1048576:.0f} MB)")


def status(url: str) -> int | str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (validador de README)"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status
    except urllib.error.HTTPError as erro:
        return erro.code
    except (urllib.error.URLError, TimeoutError, OSError) as erro:
        return str(erro)


def conferir_links(links: dict[str, set[str]]) -> None:
    for url in sorted(links):
        onde = ", ".join(sorted(links[url]))
        resultado: int | str = ""
        for tentativa in range(TENTATIVAS):
            resultado = status(url)
            if isinstance(resultado, int) and resultado < 400:
                break
            if resultado in BLOQUEIO or resultado in (404, 410):
                break
            time.sleep(5 * (tentativa + 1))  # serviços gratuitos demoram a acordar
        if isinstance(resultado, int) and resultado < 400:
            print(f"  ok    {url}")
        elif resultado in BLOQUEIO:
            avisos.append(f"link não verificável ({resultado}): {url} ({onde})")
        else:
            erros.append(f"link com problema ({resultado}): {url} ({onde})")


def main() -> int:
    links: dict[str, set[str]] = {}
    for nome in READMES:
        texto = (RAIZ / nome).read_text(encoding="utf-8")
        conferir_imagens(nome, texto)
        for a, b in LINK.findall(texto):
            links.setdefault(a or b, set()).add(nome)
    if "--links" in sys.argv:
        print(f"Testando {len(links)} links...")
        conferir_links(links)

    for aviso in avisos:
        print(f"::warning::{aviso}")
    for erro in erros:
        print(f"::error::{erro}")
    print("Tudo certo." if not erros else f"{len(erros)} problema(s).")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())

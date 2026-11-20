"""Monta um carrossel em WebP animado a partir de capturas de tela (1280x720).

Cada tela ganha uma barra de legenda (contador, nome e endereço) e, na divisa, uma
barra de progresso em segmentos, um por tela, que enche enquanto a tela está parada.
A troca entre telas é um deslize lateral com aceleração suave e leve desfoque.

Uso (da raiz do repositório):

    pip install pillow
    python .github/scripts/gerar_carrossel.py saida.webp "endereco.padrao" tela1.png="Legenda 1" tela2.png="Legenda 2|outro.endereco"

O texto depois de "|" troca o endereço só daquela tela.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, B = 1280, 720, 76            # tela, altura da tela e altura da legenda
PARADA, PASSO = 3200, 200          # ms em cada tela e intervalo de avanço da barra
QUADROS_TROCA, QUALIDADE = 18, 50  # quadros por deslize e qualidade do WebP (50 pesa ~40% menos que 82, sem perda visível)
SEG_ALT, SEG_VAO = 5, 8
CARVAO, BORDA, PAPEL, APOIO, BRASA = "#120F0D", "#332C28", "#FBFAF9", "#988881", "#FF7E29"


def _fonte(arquivo: str, tam: int, peso: int):
    f = ImageFont.truetype(f"assets/fontes/{arquivo}", tam)
    f.set_variation_by_axes([peso])
    return f


def montar(saida: str, endereco: str, itens: list[tuple[str, str]]) -> None:
    sora, mono, num = _fonte("Sora.ttf", 27, 600), _fonte("FiraCode.ttf", 19, 400), _fonte("FiraCode.ttf", 19, 500)
    total = len(itens)
    telas = []
    for i, (arquivo, nome) in enumerate(itens):
        legenda, _, end_item = nome.partition("|")
        t = Image.new("RGB", (W, H + B), CARVAO)
        t.paste(Image.open(arquivo).convert("RGB").resize((W, H), Image.LANCZOS), (0, 0))
        d = ImageDraw.Draw(t)
        y = H + SEG_ALT + (B - SEG_ALT) / 2
        contador = f"{i + 1:02d}"
        d.text((28, y + 1), contador, font=num, fill=BRASA, anchor="lm")
        x = 28 + d.textlength(contador, font=num)
        d.text((x, y + 1), f"/{total:02d}", font=num, fill=APOIO, anchor="lm")
        d.text((x + d.textlength(f"/{total:02d}", font=num) + 22, y), legenda, font=sora, fill=PAPEL, anchor="lm")
        d.text((W - 28, y + 1), end_item or endereco, font=mono, fill=APOIO, anchor="rm")
        telas.append(t)
    H2 = H + B

    def progresso(img, atual, fracao):
        """Segmentos na divisa: os anteriores cheios, o atual enchendo, os próximos apagados."""
        d = ImageDraw.Draw(img)
        d.rectangle([0, H, W, H + SEG_ALT - 1], fill=CARVAO)
        larg = (W - SEG_VAO * (total - 1)) / total
        for s in range(total):
            x0 = round(s * (larg + SEG_VAO)); x1 = round(x0 + larg) - 1
            d.rectangle([x0, H, x1, H + SEG_ALT - 1], fill=BORDA)
            cheio = 1 if s < atual else fracao if s == atual else 0
            if cheio > 0:
                d.rectangle([x0, H, round(x0 + (x1 - x0) * cheio), H + SEG_ALT - 1], fill=BRASA)
        return img

    quadros, tempos = [], []
    for i, t in enumerate(telas):
        passos = PARADA // PASSO
        for p in range(passos):
            quadros.append(progresso(t.copy(), i, (p + 1) / passos)); tempos.append(PASSO)
        prox = telas[(i + 1) % total]
        for k in range(1, QUADROS_TROCA):
            e0 = k / QUADROS_TROCA
            e = e0 * e0 * e0 * (e0 * (6 * e0 - 15) + 10)  # acelera e freia suavemente
            dx = round(W * e)
            f = Image.new("RGB", (W, H2))
            f.paste(t, (-dx, 0)); f.paste(prox, (W - dx, 0))
            # desfoque horizontal proporcional à velocidade: o deslize parece contínuo e comprime melhor
            v = 30 * e0 * e0 * (1 - e0) * (1 - e0) * W / QUADROS_TROCA
            r = max(1, round(v / 4))
            f = f.resize((W // 2, H2 // 2), Image.BILINEAR).filter(ImageFilter.BoxBlur((r / 2, 0))).resize((W, H2), Image.BILINEAR)
            quadros.append(progresso(f, i if i + 1 < total else -1, 1)); tempos.append(33)
    quadros[0].save(saida, save_all=True, append_images=quadros[1:], duration=tempos, loop=0,
                    quality=QUALIDADE, method=4, minimize_size=True)
    print(saida, total, "telas", len(quadros), "quadros", os.path.getsize(saida) // 1024, "KB")


if __name__ == "__main__":
    montar(sys.argv[1], sys.argv[2], [tuple(a.split("=", 1)) for a in sys.argv[3:]])

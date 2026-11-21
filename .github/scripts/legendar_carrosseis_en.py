"""Atualiza apenas a barra de legenda dos WebP animados para a versão inglesa.

As capturas do site (parte superior) permanecem originais, inclusive textos de UI
em português. A barra de progresso de 5px no topo da legenda é preservada.
Entrada: carrosséis já publicados no repositório; saída: arquivos *-en.webp.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
W, H, B = 1280, 720, 76
DARK, PAPER, MUTED, ORANGE = "#120F0D", "#FBFAF9", "#988881", "#FF7E29"
CAROUSELS = {
    "assets/projetos/turnos.webp": (
        "1e2turnos.up.railway.app",
        ["First-round results", "Presidential election", "State cartogram",
         "Governor results", "Congress in 2027", "Interactive map", "Between the rounds"],
    ),
    "assets/projetos/databola.webp": (
        "databola.up.railway.app",
        ["Choose your team", "Team dashboard", "Results and form"],
    ),
    "assets/projetos/carta.webp": (
        "melhores-restaurantes.up.railway.app",
        ["Cover", "Explore the guide", "Map of 100 restaurants",
         "Restaurants in Brazil", "Filterable restaurant list", "Restaurant profile"],
    ),
    "assets/projetos/cronomapa.webp": (
        "cronomapa.up.railway.app",
        ["World map: year 100", "World map: year 1500", "World map: year 1900",
         "World map: year 2026", "Notable figures: 1600", "Ruler profile"],
    ),
    "assets/perfil/projetos.webp": (
        "andreruperto.dev",
        ["Genetics homepage", "Risk calculator", "Chromosomal conditions"],
    ),
}


def font(name: str, size: int, weight: int):
    f = ImageFont.truetype(str(ROOT / "assets" / "fontes" / name), size)
    if hasattr(f, "set_variation_by_axes"):
        f.set_variation_by_axes([weight])
    return f


def render(original: Path, domain: str, labels: list[str]) -> None:
    sora, mono, number = font("Sora.ttf", 27, 600), font("FiraCode.ttf", 19, 400), font("FiraCode.ttf", 19, 500)
    with Image.open(original) as animation:
        if animation.size != (W, H + B):
            raise ValueError(f"{original}: tamanho inesperado {animation.size}, esperado {(W, H + B)}")
        frame_count = animation.n_frames
        if frame_count % len(labels):
            raise ValueError(f"{original}: {frame_count} quadros nao dividem {len(labels)} telas")
        frames_per_slide = frame_count // len(labels)
        frames, durations = [], []
        for i in range(frame_count):
            animation.seek(i)
            duration = animation.info.get("duration", 200) or 200
            frame = animation.convert("RGB")
            # Conserva a foto e a barra segmentada original; substitui so a legenda.
            draw = ImageDraw.Draw(frame)
            draw.rectangle((0, H + 5, W - 1, H + B - 1), fill=DARK)
            slide_index = min(i // frames_per_slide, len(labels) - 1)
            progress = i % frames_per_slide
            # Na segunda metade do deslize, a legenda ja mostra a tela seguinte.
            if progress >= frames_per_slide - 8:
                slide_index = (slide_index + 1) % len(labels)
            count = f"{slide_index + 1:02d}"
            y = H + 5 + (B - 5) / 2
            draw.text((28, y + 1), count, font=number, fill=ORANGE, anchor="lm")
            x = 28 + draw.textlength(count, font=number)
            draw.text((x, y + 1), f"/{len(labels):02d}", font=number, fill=MUTED, anchor="lm")
            x += draw.textlength(f"/{len(labels):02d}", font=number) + 22
            draw.text((x, y), labels[slide_index], font=sora, fill=PAPER, anchor="lm")
            draw.text((W - 28, y + 1), domain, font=mono, fill=MUTED, anchor="rm")
            frames.append(frame)
            durations.append(duration)

    output = original.with_name(original.stem + "-en.webp")
    frames[0].save(output, save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, quality=48, method=4, minimize_size=True)
    if output.stat().st_size > 2_000_000:
        raise ValueError(f"{output}: {output.stat().st_size} bytes (max 2 MB)")
    print(f"{output.relative_to(ROOT)}: {len(labels)} telas, {frame_count} quadros, {output.stat().st_size} bytes")


if __name__ == "__main__":
    for source, (domain, labels) in CAROUSELS.items():
        render(ROOT / source, domain, labels)

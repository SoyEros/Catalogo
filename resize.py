from pathlib import Path
from PIL import Image, ImageOps

# --- Configuración ---
SRC_DIR = Path("img")             # carpeta de origen con tus imágenes
DST_DIR = Path("img_resized")     # carpeta de salida
TARGET_SIZE = (600, 600)          # ancho, alto final (cuadrado recomendado)
MODE = "cover"                    # "cover" (recorte centrado) | "pad" (bordes) | "stretch"
PAD_COLOR_HEX = "#E0BBE4"         # violeta pastel (si usás "pad")

# ----------------------

def hex_to_rgb(hex_color: str):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def resize_cover(im: Image.Image, size):
    # Recorta centrado al tamaño exacto, sin deformar
    return ImageOps.fit(im, size, method=Image.LANCZOS, centering=(0.5, 0.5))

def resize_pad(im: Image.Image, size, bg_rgb=(255, 255, 255)):
    # Ajusta dentro del cuadro y agrega bordes del color elegido
    thumb = ImageOps.contain(im, size, method=Image.LANCZOS)
    has_alpha = thumb.mode in ("RGBA", "LA")
    bg_mode = "RGBA" if has_alpha else "RGB"
    bg = Image.new(bg_mode, size, bg_rgb + ((0,) if bg_mode == "RGBA" else ()))
    x = (size[0] - thumb.width) // 2
    y = (size[1] - thumb.height) // 2
    bg.paste(thumb, (x, y), thumb if has_alpha else None)
    return bg

def save_image(img: Image.Image, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    ext = out_path.suffix.lower()
    params = {}
    if ext in (".jpg", ".jpeg"):
        # Para JPG: conviene asegurarse de RGB y comprimir bien
        img = img.convert("RGB")
        params.update(dict(quality=90, optimize=True, progressive=True, subsampling=0))
    elif ext == ".png":
        params.update(dict(optimize=True, compress_level=9))
    img.save(out_path, **params)

def main():
    bg_rgb = hex_to_rgb(PAD_COLOR_HEX)
    DST_DIR.mkdir(exist_ok=True)
    count = 0

    for p in SRC_DIR.glob("*.*"):
        if p.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp"):
            continue

        with Image.open(p) as im:
            # Respeta orientación EXIF (fotos de celular)
            im = ImageOps.exif_transpose(im)

            if MODE == "cover":
                out = resize_cover(im, TARGET_SIZE)
            elif MODE == "pad":
                out = resize_pad(im, TARGET_SIZE, bg_rgb=bg_rgb)
            else:  # "stretch" (deforma para encajar exacto)
                out = im.resize(TARGET_SIZE, Image.LANCZOS)

            out_path = DST_DIR / p.name  # mantiene el nombre/extension
            save_image(out, out_path)
            count += 1
            print(f"✓ {p.name} → {out_path.relative_to(Path.cwd()) if out_path.is_absolute() else out_path}")

    print(f"\nListo. Imágenes procesadas: {count}. Salida en: {DST_DIR}")

if __name__ == "__main__":
    main()


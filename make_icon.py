from pathlib import Path
from PIL import Image
import numpy as np

BASE_DIR = Path(__file__).parent
src = BASE_DIR / "note.png"
dst = BASE_DIR / "icon.ico"

if src.exists():
    img = Image.open(src).convert("RGBA")
    data = np.array(img)

    r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]

    # Se houver fundo branco, torna transparente
    white_mask = (r > 235) & (g > 235) & (b > 235)
    data[white_mask, 3] = 0

    img_clean = Image.fromarray(data)

    bbox = img_clean.getbbox()
    if bbox:
        img_clean = img_clean.crop(bbox)

    target = 512
    img_clean.thumbnail((target, target), Image.LANCZOS)
    canvas = Image.new("RGBA", (target, target), (0, 0, 0, 0))
    offset = ((target - img_clean.width) // 2, (target - img_clean.height) // 2)
    canvas.paste(img_clean, offset)

    sizes = [(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)]
    canvas.save(dst, format="ICO", sizes=sizes)
    print(f"Ícone convertido dinamicamente com sucesso: {dst}")
else:
    print(f"Aviso: Imagem {src} não encontrada.")

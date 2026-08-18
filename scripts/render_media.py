#!/usr/bin/env python3
"""Genera los renders de `docs/media/` para el README y la documentación.

Usa FreeCAD GUI bajo un display virtual (Xvfb) para renderizar las 4 piezas
del preset 1.5" TC64 con material metálico (modo Shaded, sin aristas). No
requiere monitor físico ni interacción: corre headless.

Dependencias:
  - FreeCAD (Flatpak: org.freecad.FreeCAD)
  - Xvfb
  - Python PIL (para el recorte transparente)
  - El repo clonado con `tripta_clamps_3d` importable (vía PYTHONPATH)

Uso:
  ./scripts/render_media.py

Genera en `docs/media/`:
  - hero.png            (las 4 piezas juntas, para el banner del README)
  - render_all_wide.png (las 4 piezas separadas, ancho)
  - render_ferrula.png  render_gasket.png  render_spool.png  render_endcap.png
"""
import subprocess, sys, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA = os.path.join(REPO, "docs", "media")
os.makedirs(MEDIA, exist_ok=True)

_PRESET = '1.5" · TC64'
_PROPS_BLOCK = f'''
_PRESET = preset_por_nombre({_PRESET!r})
_PROPS = {{
    "TubeID": _PRESET["tube_id"], "TubeOD": _PRESET["tube_od"],
    "FerruleOD": _PRESET["ferrule_od"], "BeadDistance": _PRESET["bead_distance"],
    "BeadRadius": 1.5, "SpoolLength": 100.0,
    "TubeHeight": _PRESET["tube_height_larga"], "FerrHeight": 2.0,
    "GasketThickness": _PRESET["gasket_thickness"],
}}'''

PAIRS_SCRIPT = f'''#!/usr/bin/env python3
"""Renderiza 2 pares de piezas en alta resolución (4 piezas en total)."""
import sys, os, time
sys.path.insert(0, {REPO!r})
import FreeCAD as App
import FreeCADGui as Gui
from tripta_clamps_3d.feature import TriptaClamps3DFeature, TriptaClamps3DViewProvider
from tripta_clamps_3d.presets import preset_por_nombre
{_PROPS_BLOCK}
OUT = {MEDIA!r}
TIPOS_CONF = [
    ("P1", [("ferrula", -90), ("gasket", 90)]),
    ("P2", [("spool", -120), ("endcap", 120)]),
]
for docname, items in TIPOS_CONF:
    doc = App.newDocument(docname)
    for tipo, px in items:
        obj = doc.addObject("Part::FeaturePython", f"TF_{{tipo}}")
        TriptaClamps3DFeature(obj)
        if obj.ViewObject is not None:
            TriptaClamps3DViewProvider(obj.ViewObject)
            try:
                obj.ViewObject.ShapeColor = (0.55, 0.57, 0.60, 1.0)
                obj.ViewObject.DiffuseColor = [(0.55, 0.57, 0.60, 1.0)]
            except Exception:
                pass
        obj.PieceType = tipo
        for prop, val in _PROPS.items():
            setattr(obj, prop, val)
        obj.Placement = App.Placement(App.Vector(px, 0, 0), App.Rotation())
        doc.recompute()
    doc.recompute()
    view = Gui.ActiveDocument.ActiveView
    view.viewIsometric(); view.fitAll(); time.sleep(0.7)
    view.saveImage(f"{{OUT}}/pair_{{docname}}.png", 2400, 1200, "#2b2b2b")
    App.closeDocument(docname)
os._exit(0)
'''

def run_xvfb(script_path, screen="2600x1400x24", timeout=120):
    """Corre un script de FreeCAD GUI bajo Xvfb."""
    cmd = [
        "xvfb-run", "-a", "-s", f"-screen 0 {screen}",
        "flatpak", "run",
        "--env=QT_QPA_PLATFORM=xcb",
        f"--env=PYTHONPATH={REPO}",
        "org.freecad.FreeCAD", script_path,
    ]
    subprocess.run(cmd, timeout=timeout, check=False,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def split_pairs():
    """Recorta cada pieza individual de los PNGs de pares (fondo transparente)."""
    from PIL import Image
    def split(path, out_names):
        im = Image.open(path).convert("RGB")
        w, h = im.size; px = im.load()
        def is_body(c): return c[0] > 90 or c[1] > 90 or c[2] > 90
        col = {}
        for x in range(0, w, 2):
            col[x] = sum(1 for y in range(0, h, 2) if is_body(px[x, y])) > 1
        runs, in_run = [], False
        for x in sorted(col):
            if col[x] and not in_run: st, in_run = x, True
            elif not col[x] and in_run: runs.append((st, x)); in_run = False
        if in_run: runs.append((st, max(col)))
        for i, (x0, x1) in enumerate(runs):
            if i >= len(out_names): break
            xa, xb = max(0, x0-25), min(w, x1+25)
            ys = [y for y in range(0, h) for xx in range(xa, xb, 2) if is_body(px[xx, y])]
            if not ys: continue
            ya, yb = max(0, min(ys)-15), min(h, max(ys)+15)
            crop = im.crop((xa, ya, xb, yb)).convert("RGBA")
            data = crop.getdata()
            crop.putdata([(c[0], c[1], c[2], 255) if (c[0] > 90 or c[1] > 90 or c[2] > 90)
                          else (0, 0, 0, 0) for c in data])
            crop.save(os.path.join(MEDIA, f"{out_names[i]}.png"))
    split(os.path.join(MEDIA, "pair_P1.png"), ["render_ferrula", "render_gasket"])
    split(os.path.join(MEDIA, "pair_P2.png"), ["render_spool", "render_endcap"])


def make_hero():
    """Compone el banner con las 4 piezas sobre fondo degradado oscuro."""
    from PIL import Image, ImageDraw
    pieces = ["render_ferrula", "render_gasket", "render_spool", "render_endcap"]
    labels = ["Férula", "Gasket", "Spool", "End cap"]
    ims = [Image.open(os.path.join(MEDIA, f"{p}.png")).convert("RGBA") for p in pieces]
    H = 420
    scaled = [im.resize((int(im.size[0]*H/im.size[1]), H), Image.LANCZOS) for im in ims]
    gap, pad = 70, 60
    W = pad*2 + sum(im.size[0] for im in scaled) + gap*(len(scaled)-1)
    H_img = H + 90
    canvas = Image.new("RGBA", (W, H_img), (0, 0, 0, 255))
    for y in range(H_img):
        v = int(35 + 10*(y/H_img))
        for x in range(0, W, 4):
            for xx in range(min(4, W-x)):
                canvas.putpixel((x+xx, y), (v, v, v, 255))
    x = pad
    for im, lab in zip(scaled, labels):
        y0 = (H - im.size[1]) // 2 + 10
        canvas.alpha_composite(im, (x, y0))
        d = ImageDraw.Draw(canvas)
        lw = d.textlength(lab)
        d.text((x + (im.size[0]-lw)/2, H+20), lab, fill=(200, 200, 200, 255))
        x += im.size[0] + gap
    canvas.convert("RGB").save(os.path.join(MEDIA, "hero.png"))


def main():
    tmp = os.path.join(REPO, "scripts", "_pairs_render_tmp.py")
    with open(tmp, "w") as f:
        f.write(PAIRS_SCRIPT)
    try:
        print("Renderizando pares bajo Xvfb (FreeCAD GUI, puede tardar)...")
        run_xvfb(tmp)
        print("Recortando piezas individuales...")
        split_pairs()
        print("Componiendo hero.png...")
        make_hero()
        print("Listo. Renders en docs/media/")
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


if __name__ == "__main__":
    main()

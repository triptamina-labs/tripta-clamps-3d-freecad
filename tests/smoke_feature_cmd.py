#!/usr/bin/env python3
"""Smoke test para TriptaClamps3DFeature — ejecutar con freecadcmd.

Crea las 4 piezas (ferrula, gasket, spool, endcap) como
Part::FeaturePython, las reconstruye y verifica geometría válida.

Uso:
    PYTHONPATH=/ruta/al/repo freecadcmd -c "exec(open('tests/smoke_feature_cmd.py').read())"
"""

import sys
import os

# Asegurar que el repo está en el path
# Cuando se ejecuta con exec(open(...).read()), __file__ no existe.
# Usamos el PYTHONPATH que ya debería contener el repo,
# o buscamos tripta_clamps_3d/ en el cwd.
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(
    __file__ if '__file__' in dir() else os.path.join(os.getcwd(), 'tests', 'smoke_feature_cmd.py')
)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import FreeCAD as App
import Part

from tripta_clamps_3d.feature import TriptaClamps3DFeature, TriptaClamps3DViewProvider
from tripta_clamps_3d.presets import preset_por_nombre

# ── Preset 1.5" TC64 ────────────────────────────────────────

_PRESET = preset_por_nombre('1.5" · TC64')
assert _PRESET is not None, "No se encontró preset 1.5\" · TC64"

# Mapeo de propiedades: preset snake_case → Feature camelCase
_PROP_MAP = {
    "TubeID": _PRESET["tube_id"],
    "TubeOD": _PRESET["tube_od"],
    "FerruleOD": _PRESET["ferrule_od"],
    "BeadDistance": _PRESET["bead_distance"],
    "BeadRadius": 1.5,
    "SpoolLength": 100.0,
    "TubeHeight": _PRESET["tube_height_larga"],
    "FerrHeight": 2.0,
    "GasketThickness": _PRESET["gasket_thickness"],
}

TIPOS = ["ferrula", "gasket", "spool", "endcap"]

# ── Crear documento ──────────────────────────────────────────

doc = App.newDocument("Smoke")

ok_count = 0
fail_count = 0

for tipo in TIPOS:
    obj_name = f"TF_{tipo}"
    obj = doc.addObject("Part::FeaturePython", obj_name)

    # Asignar proxy
    proxy = TriptaClamps3DFeature(obj)

    # Asignar view provider (sólo en modo GUI — ViewObject es None en freecadcmd)
    if obj.ViewObject is not None:
        vp = TriptaClamps3DViewProvider(obj.ViewObject)

    # Setear propiedades
    obj.PieceType = tipo
    for prop, val in _PROP_MAP.items():
        setattr(obj, prop, val)

    # Recompute
    doc.recompute()

    # Verificar
    shape = obj.Shape
    vol_ok = False
    valid_ok = False
    diag_ok = False
    bb = None

    if shape is not None and not shape.isNull():
        valid_ok = shape.isValid()
        vol_ok = shape.Volume > 0.0
        bb = shape.BoundBox
        diag = (
            (bb.XLength ** 2 + bb.YLength ** 2 + bb.ZLength ** 2) ** 0.5
        )
        diag_ok = diag > 1.0  # > 1mm

    all_ok = valid_ok and vol_ok and diag_ok

    status = "✅" if all_ok else "❌"
    vol_str = f"{shape.Volume:.1f}" if shape and not shape.isNull() else "N/A"
    diag_str = f"{diag:.1f}" if bb else "N/A"

    print(
        f"  {status} {tipo:10s}  valid={valid_ok}  vol={vol_str}  diag={diag_str}"
    )

    if all_ok:
        ok_count += 1
    else:
        fail_count += 1

# ── Resumen ──────────────────────────────────────────────────

summary = []
summary.append(f"Resultado: {ok_count}/{len(TIPOS)} piezas válidas")
if fail_count > 0:
    summary.append(f"FALLARON {fail_count} pieza(s)")
    print("\n".join(summary))
    # Write summary to file for verification
    with open("/home/tripta/smoke_result.txt", "w") as f:
        f.write("FAIL\n")
        f.write("\n".join(summary) + "\n")
    sys.exit(1)
else:
    summary.append("Todas las piezas OK ✅")
    print("\n".join(summary))
    with open("/home/tripta/smoke_result.txt", "w") as f:
        f.write("PASS\n")
        f.write("\n".join(summary) + "\n")
    sys.exit(0)

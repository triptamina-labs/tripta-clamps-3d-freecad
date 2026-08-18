#!/usr/bin/env python3
"""Genera /tmp/tc64_gui.FCStd con las 4 piezas tri-clamp (preset 1.5\" TC64) + placements + render."""
import sys, os
sys.path.insert(0, "/home/tripta/repos/tripta-clamps-3d-freecad")

import FreeCAD as App
import Part
from tripta_clamps_3d.feature import TriptaClamps3DFeature, TriptaClamps3DViewProvider
from tripta_clamps_3d.presets import preset_por_nombre

_PRESET = preset_por_nombre('1.5" · TC64')
_PROPS = {
    "TubeID": _PRESET["tube_id"], "TubeOD": _PRESET["tube_od"],
    "FerruleOD": _PRESET["ferrule_od"], "BeadDistance": _PRESET["bead_distance"],
    "BeadRadius": 1.5, "SpoolLength": 100.0,
    "TubeHeight": _PRESET["tube_height_larga"], "FerrHeight": 2.0,
    "GasketThickness": _PRESET["gasket_thickness"],
}
TIPOS = ["ferrula", "gasket", "spool", "endcap"]
POS = ["(-120,80,0)", "(-40,80,0)", "(40,80,0)", "(120,80,0)"]

doc = App.newDocument("TC64_Verif")
for tipo, pos in zip(TIPOS, POS):
    obj = doc.addObject("Part::FeaturePython", f"TF_{tipo}")
    TriptaClamps3DFeature(obj)
    ob = obj.ViewObject
    if ob is not None:
        TriptaClamps3DViewProvider(ob)
    obj.PieceType = tipo
    for prop, val in _PROPS.items():
        setattr(obj, prop, val)
    obj.Placement = App.Placement(App.Vector(eval(pos)), App.Rotation())
    doc.recompute()
doc.recompute()

fpath = "/home/tripta/repos/tripta-clamps-3d-freecad/tc64_gui.FCStd"
doc.saveAs(fpath)
print("SAVED", fpath)
# report
for tipo in TIPOS:
    o = doc.getObject(f"TF_{tipo}")
    s = o.Shape
    print(tipo, "valid=", s.isValid(), "vol=", round(s.Volume,1),
          "bb=", [round(s.BoundBox.XLength,1), round(s.BoundBox.YLength,1), round(s.BoundBox.ZLength,1)])

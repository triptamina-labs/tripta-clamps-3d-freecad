"""TriptaFittingsFeature — Part::FeaturePython paramétrico para tri-clamp.

Se registra en FreeCAD como ``Part::FeaturePython`` con propiedades
editables en la Task Panel / Property View.  ``execute()`` reconstruye
el sólido de revolución cada vez que cambia una dimensión.
"""

from __future__ import annotations

from tripta_fittings.builder import build_solid


class TriptaFittingsFeature:
    """Proxy Python para Part::FeaturePython con piezas tri-clamp."""

    def __init__(self, fp):
        self.Type = "TriptaFittingsFeature"
        fp.Proxy = self

        # ── Propiedades ──────────────────────────────────────
        import FreeCAD as App  # noqa: F811 — import dentro de __init__

        fp.addProperty(
            "App::PropertyEnumeration",
            "PieceType",
            "TriptaFittings",
            "Tipo de pieza",
        ).PieceType = ["ferrula", "gasket", "spool", "endcap"]

        fp.addProperty("App::PropertyFloat", "TubeID", "TriptaFittings", "Diámetro interno del tubo")
        fp.addProperty("App::PropertyFloat", "TubeOD", "TriptaFittings", "Diámetro externo del tubo")
        fp.addProperty("App::PropertyFloat", "FerruleOD", "TriptaFittings", "Diámetro externo del ferrule")
        fp.addProperty("App::PropertyFloat", "BeadDistance", "TriptaFittings", "Distancia entre beads")
        fp.addProperty("App::PropertyFloat", "BeadRadius", "TriptaFittings", "Radio del bead")
        fp.addProperty("App::PropertyFloat", "SpoolLength", "TriptaFittings", "Longitud del spool")
        fp.addProperty("App::PropertyFloat", "TubeHeight", "TriptaFittings", "Altura del tubo")
        fp.addProperty("App::PropertyFloat", "FerrHeight", "TriptaFittings", "Altura del ferrule")
        fp.addProperty("App::PropertyFloat", "GasketThickness", "TriptaFittings", "Espesor del gasket")

    def execute(self, fp):
        """Construye el sólido de revolución y lo asigna a fp.Shape."""
        params = {
            "tubeID": fp.TubeID,
            "tubeOD": fp.TubeOD,
            "ferruleOD": fp.FerruleOD,
            "beadDistance": fp.BeadDistance,
            "beadRadius": fp.BeadRadius,
            "spoolLength": fp.SpoolLength,
            "tubeHeight": fp.TubeHeight,
            "ferrHeight": fp.FerrHeight,
            "gasketThickness": fp.GasketThickness,
        }
        fp.Shape = build_solid(fp.PieceType, params)

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state


class TriptaFittingsViewProvider:
    """ViewProvider mínimo — funcional sin GUI (freecadcmd)."""

    def __init__(self, vobj):
        vobj.Proxy = self

    def getIcon(self):
        return None

    def attach(self, vobj):
        pass

    def detach(self, vobj):
        pass

    def updateData(self, fp, prop):
        pass

    def onChanged(self, vobj, prop):
        pass

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        pass

"""Tripta Fittings — hook de inicialización GUI del addon FreeCAD.

Este módulo se ejecuta solo cuando FreeCAD arranca en modo gráfico.
Registra el workbench ``TriptaFittingsWorkbench`` en FreeCADGui.

Los imports de FreeCAD/FreeCADGui/PySide están protegidos dentro de
bloques try/except para no romper el arranque si falta alguna dependencia.
"""

from __future__ import annotations

import os
import sys

# Asegurar que la raíz del addon esté en sys.path
_addon_dir = os.path.dirname(os.path.abspath(__file__))
if _addon_dir not in sys.path:
    sys.path.insert(0, _addon_dir)


def Initialize():
    """Función llamada por FreeCADGui para inicializar el workbench."""
    try:
        import FreeCADGui  # noqa: F401
    except ImportError:
        return

    try:
        from tripta_fittings.workbench import TriptaFittingsWorkbench
        FreeCADGui.addWorkbench(TriptaFittingsWorkbench)
    except Exception as exc:
        print(f"[Tripta Fittings] Error al registrar workbench: {exc}")


# Requerido por FreeCAD — lista de comandos que provee este workbench
Commands = ["TriptaCreatePiece", "TriptaOpenPanel"]


def GetClassName():
    return "Gui::PythonWorkbench"

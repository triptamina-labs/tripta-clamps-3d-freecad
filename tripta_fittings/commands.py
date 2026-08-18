"""FreeCAD commands for the Tripta Fittings workbench.

This module defines two commands registered in FreeCADGui:

* ``TriptaCreatePiece`` — Creates a new parametric tri-clamp piece in
  the active document (or a new document if none is open).  Does **not**
  open the panel.

* ``TriptaOpenPanel`` — Opens (or brings to front) the TriptaFittingsPanel
  dock widget.

Registration
------------
``register_commands()`` must be called after FreeCADGui is available
(e.g. from ``TriptaFittingsWorkbench.Initialize`` or
``InitGui.Initialize``).  It is wrapped in ``try/except`` so that
headless environments (``freecadcmd``, pytest) never break.

How to open the panel
---------------------
From the FreeCAD GUI menu: *Tripta Fittings → TriptaOpenPanel*.
Or programmatically::

    from tripta_fittings.panel import open_panel
    open_panel()
"""
from __future__ import annotations

from typing import Any


# ── TriptaCreatePiece command ──────────────────────────────────────

class _TriptaCreatePieceCmd:
    """FreeCAD command: create a parametric tri-clamp piece."""

    def IsActive(self) -> bool:
        """Always active (creates a new piece if needed)."""
        return True

    def Activated(self) -> None:
        """Create a new TriptaFittingsFeature in the active document."""
        try:
            import FreeCAD as App
            import FreeCADGui as _Gui
        except ImportError:
            return

        doc = App.ActiveDocument
        if doc is None:
            doc = App.newDocument("TriptaFittings")

        from tripta_fittings.feature import (
            TriptaFittingsFeature,
            TriptaFittingsViewProvider,
        )

        obj = doc.addObject("Part::FeaturePython", "TF_Piece")
        TriptaFittingsFeature(obj)
        TriptaFittingsViewProvider(obj.ViewObject)
        doc.recompute()

        # Select the new object
        try:
            _Gui.Selection.clearSelection()
            _Gui.Selection.addSelection(doc.Name, obj.Name)
        except Exception:
            pass

    def GetCommands(self) -> tuple:
        return ("TriptaCreatePiece",)

    def GetToolTip(self) -> str:
        return "Crear una pieza tri-clamp paramétrica (férula/gasket/spool/endcap)."

    def GetMenuText(self) -> str:
        return "Crear pieza"

    def GetIcon(self) -> str:
        return ""


# ── TriptaOpenPanel command ────────────────────────────────────────

class _TriptaOpenPanelCmd:
    """FreeCAD command: open the Tripta Fittings control panel."""

    def IsActive(self) -> bool:
        return True

    def Activated(self) -> None:
        try:
            from tripta_fittings.panel import open_panel
            open_panel()
        except Exception as exc:
            print(f"[Tripta Fittings] Error opening panel: {exc}")

    def GetCommands(self) -> tuple:
        return ("TriptaOpenPanel",)

    def GetToolTip(self) -> str:
        return "Abrir el panel de control de Tripta Fittings."

    def GetMenuText(self) -> str:
        return "Abrir panel"

    def GetIcon(self) -> str:
        return ""


# ── Registration ───────────────────────────────────────────────────

def register_commands() -> None:
    """Register ``TriptaCreatePiece`` and ``TriptaOpenPanel`` in FreeCADGui.

    This function is safe to call multiple times — duplicate registrations
    are silently ignored by FreeCAD.

    Must be called after ``FreeCADGui`` is available (e.g. from
    ``TriptaFittingsWorkbench.Initialize`` or ``InitGui.Initialize``).
    Wrapped in ``try/except`` so headless ``freecadcmd`` never breaks.
    """
    try:
        import FreeCADGui  # noqa: F401 — guard
    except ImportError:
        return  # headless — nothing to do

    try:
        FreeCADGui.addCommand("TriptaCreatePiece", _TriptaCreatePieceCmd())
    except Exception:
        pass

    try:
        FreeCADGui.addCommand("TriptaOpenPanel", _TriptaOpenPanelCmd())
    except Exception:
        pass

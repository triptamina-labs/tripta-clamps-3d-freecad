"""FreeCAD commands for the Tripta Clamps 3D workbench.

This module defines two commands registered in FreeCADGui:

* ``TriptaClamps3DCreatePiece`` — Creates a new parametric tri-clamp piece in
  the active document (or a new document if none is open).  Does **not**
  open the panel.

* ``TriptaClamps3DOpenPanel`` — Opens (or brings to front) the TriptaClamps3DPanel
  dock widget.

Registration
------------
``register_commands()`` must be called after FreeCADGui is available
(e.g. from ``TriptaClamps3DWorkbench.Initialize`` or
``InitGui.Initialize``).  It is wrapped in ``try/except`` so that
headless environments (``freecadcmd``, pytest) never break.

How to open the panel
---------------------
From the FreeCAD GUI menu: *Tripta Clamps 3D → TriptaClamps3DOpenPanel*.
Or programmatically::

    from tripta_clamps_3d.panel import open_panel
    open_panel()
"""
from __future__ import annotations

from typing import Any


# ── TriptaClamps3DCreatePiece command ──────────────────────────────────────

class _TriptaClamps3DCreatePieceCmd:
    """FreeCAD command: create a parametric tri-clamp piece."""

    def IsActive(self) -> bool:
        """Always active (creates a new piece if needed)."""
        return True

    def Activated(self) -> None:
        """Create a new TriptaClamps3DFeature in the active document."""
        try:
            import FreeCAD as App
            import FreeCADGui as _Gui
        except ImportError:
            return

        doc = App.ActiveDocument
        if doc is None:
            doc = App.newDocument("TriptaClamps3D")

        from tripta_clamps_3d.feature import (
            TriptaClamps3DFeature,
            TriptaClamps3DViewProvider,
        )

        obj = doc.addObject("Part::FeaturePython", "TF_Piece")
        TriptaClamps3DFeature(obj)
        TriptaClamps3DViewProvider(obj.ViewObject)
        doc.recompute()

        # Select the new object
        try:
            _Gui.Selection.clearSelection()
            _Gui.Selection.addSelection(doc.Name, obj.Name)
        except Exception:
            pass

    def GetCommands(self) -> tuple:
        return ("TriptaClamps3DCreatePiece",)

    def GetToolTip(self) -> str:
        return "Crear una pieza tri-clamp paramétrica (férula/gasket/spool/endcap)."

    def GetMenuText(self) -> str:
        return "Crear pieza"

    def GetIcon(self) -> str:
        return ""


# ── TriptaClamps3DOpenPanel command ────────────────────────────────────────

class _TriptaClamps3DOpenPanelCmd:
    """FreeCAD command: open the Tripta Clamps 3D control panel."""

    def IsActive(self) -> bool:
        return True

    def Activated(self) -> None:
        try:
            from tripta_clamps_3d.panel import open_panel
            open_panel()
        except Exception as exc:
            print(f"[Tripta Clamps 3D] Error opening panel: {exc}")

    def GetCommands(self) -> tuple:
        return ("TriptaClamps3DOpenPanel",)

    def GetToolTip(self) -> str:
        return "Abrir el panel de control de Tripta Clamps 3D."

    def GetMenuText(self) -> str:
        return "Abrir panel"

    def GetIcon(self) -> str:
        return ""


# ── Registration ───────────────────────────────────────────────────

def register_commands() -> None:
    """Register ``TriptaClamps3DCreatePiece`` and ``TriptaClamps3DOpenPanel`` in FreeCADGui.

    This function is safe to call multiple times — duplicate registrations
    are silently ignored by FreeCAD.

    Must be called after ``FreeCADGui`` is available (e.g. from
    ``TriptaClamps3DWorkbench.Initialize`` or ``InitGui.Initialize``).
    Wrapped in ``try/except`` so headless ``freecadcmd`` never breaks.
    """
    try:
        import FreeCADGui  # noqa: F401 — guard
    except ImportError:
        return  # headless — nothing to do

    try:
        FreeCADGui.addCommand("TriptaClamps3DCreatePiece", _TriptaClamps3DCreatePieceCmd())
    except Exception:
        pass

    try:
        FreeCADGui.addCommand("TriptaClamps3DOpenPanel", _TriptaClamps3DOpenPanelCmd())
    except Exception:
        pass

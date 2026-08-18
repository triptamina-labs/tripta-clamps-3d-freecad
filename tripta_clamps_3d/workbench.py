"""Tripta Clamps 3D — workbench para FreeCAD.

Define la clase ``TriptaClamps3DWorkbench`` que FreeCAD registra como
un workbench en el menú de trabajo.

Los imports de FreeCAD, FreeCADGui y PySide/Qt están protegidos dentro
de los métodos para que este módulo pueda importarse con pytest sin
la entorno de FreeCAD.
"""

from __future__ import annotations

import os
from typing import Any


class TriptaClamps3DWorkbench:
    """Workbench paramétrico para piezas tri-clamp.

    Proporciona acceso a comandos de creación y edición de piezas:
    ``TriptaClamps3DCreatePiece`` y ``TriptaClamps3DOpenPanel``.

    Los comandos se implementarán en la ola 3 de desarrollo.
    """

    # ── Metadatos ────────────────────────────────────────────────────
    MenuText = "Tripta Clamps 3D"
    ToolTip = (
        "Workbench paramétrico de piezas tri-clamp: "
        "férula, gasket, spool y endcap. "
        "Portado de TriptaClamps3D-Web."
    )

    # Icono del workbench.
    # NOTA: Si se desea un icono personalizado, colocar un archivo PNG en
    # tripta_clamps_3d/icon.png (recomendado 96×96 px) y descomentar la
    # línea de __icon_path. Por ahora se usa un QIcon vacío o el icono
    # de Part como fallback.
    _icon_path: str = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "icon.png"
    )

    def __init__(self) -> None:
        """Inicializa el workbench."""
        self.__class__._loaded = True

    # ── Métodos requeridos por FreeCAD ───────────────────────────────

    def Initialize(self) -> None:
        """Registra los comandos en FreeCAD (solo GUI)."""
        try:
            import FreeCADGui  # noqa: F401
        except ImportError:
            return

        # Registrar comandos en FreeCADGui (TriptaClamps3DCreatePiece, TriptaClamps3DOpenPanel)
        try:
            from tripta_clamps_3d.commands import register_commands
            register_commands()
        except ImportError:
            pass  # commands module not yet available; commands still listed

        self.appendMenu(
            self.MenuText,
            [
                "TriptaClamps3DCreatePiece",
                "TriptaClamps3DOpenPanel",
            ],
        )

    def Activated(self) -> None:
        """Se ejecuta cuando el usuario selecciona este workbench."""
        pass

    def Deactivated(self) -> None:
        """Se ejecuta cuando el usuario deja este workbench."""
        pass

    def ContextMenu(self, obj: Any) -> None:
        """Menú contextual (sin acciones por ahora)."""
        pass

    def GetClassName(self) -> str:
        """Nombre de la clase C++ subyacente."""
        return "Gui::PythonWorkbench"

    def GetIcon(self) -> str:
        """Devuelve la ruta al icono del workbench.

        Si no existe un icono personalizado, devuelve un QIcon vacío.
        """
        try:
            import FreeCADGui  # noqa: F401
            from PySide import Qt
        except ImportError:
            return ""

        if os.path.isfile(self._icon_path):
            return self._icon_path
        # Fallback: usar icono vacío
        return ""

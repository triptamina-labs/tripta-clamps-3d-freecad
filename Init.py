"""Tripta Clamps 3D — hook de inicialización del addon FreeCAD.

Este módulo se ejecuta al iniciar FreeCAD para registrar el workbench
"Tripta Clamps 3D". No realiza ninguna acción especial durante el import
general; el registro real ocurre en InitGui.py (solo en modo gráfico).

Puede importarse sin FreeCAD (para pruebas con pytest) siempre que no
se invoquen funciones que dependan de FreeCAD internamente.
"""

from __future__ import annotations

import sys
import os

# Asegurar que la raíz del addon esté en sys.path para imports internos.
try:
    _addon_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # Ejecutado vía exec() — __file__ no está definido.
    # Intentar obtener la ruta desde el contexto de FreeCAD o usar cwd.
    _addon_dir = os.getcwd()

if _addon_dir not in sys.path:
    sys.path.insert(0, _addon_dir)

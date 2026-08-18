"""TriptaClamps3DPanel — Panel de control acoplable para piezas tri-clamp.

Diseño: QDockWidget registrado en FreeCADGui.getMainWindow() con
``Qt.RightDockWidgetArea``.  Esta es la opción más robusta para FreeCAD
moderno porque el dock se integra con el sistema de docks nativo del
menú *View > Panels* y sobrevive a minimize/restore.

Cómo se abre el panel
---------------------
El panel se abre mediante el comando ``TriptaClamps3DOpenPanel`` (register_commands)
o desde el menú *Tripta Clamps 3D > TriptaClamps3DOpenPanel* del workbench.
Internamente crea (o trae al frente) un QDockWidget singleton.

Cómo se añaden los comandos
---------------------------
``register_commands()`` (en commands.py) registra ``TriptaClamps3DCreatePiece``
y ``TriptaClamps3DOpenPanel`` en FreeCADGui.  Se llama desde
``TriptaClamps3DWorkbench.Initialize`` y desde ``InitGui.Initialize``.

Headless / pytest
-----------------
Los imports de FreeCAD/FreeCADGui/PySide están protegidos dentro de
``try/except`` a nivel módulo para que ``freecadcmd`` y ``pytest`` no
rompan.  La función ``preset_to_props_map`` funciona sin GUI y es
directamente testeable.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

# ── Protected GUI imports ──────────────────────────────────────────
# We only pull FreeCADGui / PySide when the full GUI is available.
# ``freeecadcmd`` and ``pytest`` will skip these gracefully.
_FreeCADGui: Any = None
_QtWidgets: Any = None
_QtCore: Any = None
_has_gui: bool = False

try:
    import FreeCADGui as _FreeCADGui  # noqa: F401 — guard
    from PySide import QtWidgets as _QtWidgets  # noqa: F401
    from PySide import QtCore as _QtCore  # noqa: F401
    _has_gui = True
except ImportError:
    pass


# ── Preset → feature property mapping ─────────────────────────────

def preset_to_props_map(preset: Dict[str, Any]) -> Dict[str, float]:
    """Map an ASME preset dict to TriptaClamps3DFeature property names.

    The mapping follows the convention specified in the task:

    * ``tube_id``          → ``TubeID``
    * ``tube_od``          → ``TubeOD``
    * ``ferrule_od``       → ``FerruleOD``
    * ``bead_distance``    → ``BeadDistance``
    * ``tube_height_larga``→ ``TubeHeight``
    * ``gasket_thickness`` → ``GasketThickness``
    * ``BeadRadius``       → ``1.5`` (fixed default)
    * ``SpoolLength``      → ``100.0`` (fixed default)
    * ``FerrHeight``       → ``2.0`` (fixed default)

    Parameters
    ----------
    preset : dict
        A preset dictionary from ``tripta_clamps_3d.presets.PRESETS``
        (obtained via ``preset_por_nombre()``).

    Returns
    -------
    dict
        Mapping with TriptaClamps3DFeature property names as keys and
        float values suitable for direct assignment.
    """
    if preset is None:
        return {}
    return {
        "TubeID": float(preset.get("tube_id", 0.0)),
        "TubeOD": float(preset.get("tube_od", 0.0)),
        "FerruleOD": float(preset.get("ferrule_od", 0.0)),
        "BeadDistance": float(preset.get("bead_distance", 0.0)),
        "BeadRadius": 1.5,
        "SpoolLength": 100.0,
        "TubeHeight": float(preset.get("tube_height_larga", 0.0)),
        "FerrHeight": 2.0,
        "GasketThickness": float(preset.get("gasket_thickness", 0.0)),
    }


# ── Field visibility per piece type ───────────────────────────────
# Keys = TriptaClamps3D property names; True = visible for that piece type.
_FIELDS_BY_TYPE: Dict[str, Dict[str, bool]] = {
    "ferrula": {
        "TubeID": True,
        "TubeOD": True,
        "FerruleOD": True,
        "BeadDistance": True,
        "BeadRadius": True,
        "TubeHeight": True,
        "FerrHeight": True,
        "SpoolLength": False,
        "GasketThickness": False,
    },
    "gasket": {
        "TubeID": True,
        "TubeOD": False,
        "FerruleOD": True,
        "BeadDistance": True,
        "BeadRadius": True,
        "TubeHeight": False,
        "FerrHeight": False,
        "SpoolLength": False,
        "GasketThickness": True,
    },
    "spool": {k: True for k in [
        "TubeID", "TubeOD", "FerruleOD", "BeadDistance", "BeadRadius",
        "TubeHeight", "FerrHeight", "SpoolLength", "GasketThickness",
    ]},
    "endcap": {
        "TubeID": False,
        "TubeOD": False,
        "FerruleOD": True,
        "BeadDistance": True,
        "BeadRadius": True,
        "TubeHeight": False,
        "FerrHeight": False,
        "SpoolLength": False,
        "GasketThickness": False,
    },
}

# Friendly labels for piece type combo
_PIECE_TYPE_LABELS: Dict[str, str] = {
    "ferrula": "Férula",
    "gasket": "Gasket",
    "spool": "Spool",
    "endcap": "Endcap",
}

# Friendly labels for spinboxes
_SPINBOX_LABELS: Dict[str, str] = {
    "TubeID": "Tube ID (mm)",
    "TubeOD": "Tube OD (mm)",
    "FerruleOD": "Ferrule OD (mm)",
    "BeadDistance": "Bead Distance (mm)",
    "BeadRadius": "Bead Radius (mm)",
    "TubeHeight": "Tube Height (mm)",
    "FerrHeight": "Ferrule Height (mm)",
    "SpoolLength": "Spool Length (mm)",
    "GasketThickness": "Gasket Thickness (mm)",
}

# Spinbox ranges: (min, max, decimals, step)
_SPINBOX_RANGES: Dict[str, tuple] = {
    "TubeID":          (0.0, 500.0, 2, 0.1),
    "TubeOD":          (0.0, 500.0, 2, 0.1),
    "FerruleOD":       (0.0, 600.0, 2, 0.1),
    "BeadDistance":    (0.0, 600.0, 2, 0.1),
    "BeadRadius":      (0.0, 50.0, 2, 0.1),
    "TubeHeight":      (0.0, 200.0, 2, 0.1),
    "FerrHeight":      (0.0, 100.0, 2, 0.1),
    "SpoolLength":     (0.0, 2000.0, 2, 0.1),
    "GasketThickness": (0.0, 20.0, 2, 0.1),
}

# All property names in display order
_PROP_NAMES: list[str] = [
    "TubeID", "TubeOD", "FerruleOD", "BeadDistance", "BeadRadius",
    "TubeHeight", "FerrHeight", "SpoolLength", "GasketThickness",
]


# ── TriptaClamps3DPanel (QDockWidget) ─────────────────────────────

# Module-level singleton reference so only one dock exists at a time.
_panel_instance: Optional["TriptaClamps3DPanel"] = None


def _get_main_window() -> Any:
    """Return FreeCAD's main window (or None)."""
    try:
        return _FreeCADGui.getMainWindow()
    except Exception:
        return None


class TriptaClamps3DPanel:
    """Dockable control panel for Tripta Clamps 3D.

    Constructed as a QDockWidget and added to the FreeCAD main window.
    All Qt / FreeCAD imports are done lazily inside the constructor so
    that the class can be *imported* (but not instantiated) without GUI.
    """

    def __init__(self) -> None:
        # Lazy Qt imports — only when GUI is present
        if not _has_gui:
            raise RuntimeError(
                "TriptaClamps3DPanel requires FreeCAD GUI (PySide/Qt). "
                "Cannot instantiate in headless mode."
            )

        self._dock: Any = _QtWidgets.QDockWidget("Tripta Clamps 3D")
        self._dock.setObjectName("TriptaClamps3DPanel")
        self._dock.setAllowedAreas(
            _QtCore.Qt.RightDockWidgetArea | _QtCore.Qt.LeftDockWidgetArea
        )

        self._widget: Any = _QtWidgets.QWidget()
        self._dock.setWidget(self._widget)

        # Current working object (TF_* FeaturePython or None)
        self._work_obj: Any = None

        self._block_signals: bool = False  # prevent recursive updates

        self._build_ui()
        self._connect_signals()
        self._connect_selection_observer()

        # Apply initial visibility for default type
        self._on_piece_type_changed(0)

    # ── UI construction ────────────────────────────────────────────

    def _build_ui(self) -> None:
        layout = _QtWidgets.QVBoxLayout(self._widget)

        # --- Piece type combo ---
        layout.addWidget(_QtWidgets.QLabel("Tipo de pieza:"))
        self._combo_type = _QtWidgets.QComboBox()
        for key in ["ferrula", "gasket", "spool", "endcap"]:
            self._combo_type.addItem(_PIECE_TYPE_LABELS[key], key)
        layout.addWidget(self._combo_type)

        # --- Preset combo ---
        layout.addWidget(_QtWidgets.QLabel("Preset ASME:"))
        self._combo_preset = _QtWidgets.QComboBox()
        self._combo_preset.addItem("Custom", None)
        try:
            from tripta_clamps_3d.presets import PRESETS
            for p in PRESETS:
                self._combo_preset.addItem(p["preset"], p)
        except ImportError:
            pass
        layout.addWidget(self._combo_preset)

        # --- Spinboxes ---
        self._spinboxes: Dict[str, Any] = {}
        for name in _PROP_NAMES:
            lbl_text = _SPINBOX_LABELS.get(name, name)
            row_layout = _QtWidgets.QHBoxLayout()
            label = _QtWidgets.QLabel(lbl_text)
            row_layout.addWidget(label)
            sb = _QtWidgets.QDoubleSpinBox()
            mn, mx, dec, step = _SPINBOX_RANGES.get(name, (0.0, 1000.0, 2, 0.1))
            sb.setRange(mn, mx)
            sb.setDecimals(dec)
            sb.setSingleStep(step)
            sb.setSuffix(" mm")
            sb.setProperty("propName", name)
            self._spinboxes[name] = sb
            row_layout.addWidget(sb)
            layout.addLayout(row_layout)

        # --- Buttons ---
        btn_layout = _QtWidgets.QHBoxLayout()
        self._btn_create = _QtWidgets.QPushButton("Crear pieza")
        btn_layout.addWidget(self._btn_create)
        self._btn_apply = _QtWidgets.QPushButton("Aplicar preset")
        btn_layout.addWidget(self._btn_apply)
        layout.addLayout(btn_layout)

        layout.addStretch()

    # ── Signal connections ─────────────────────────────────────────

    def _connect_signals(self) -> None:
        self._combo_type.currentIndexChanged.connect(
            self._on_piece_type_changed
        )
        self._combo_preset.currentIndexChanged.connect(
            self._on_preset_changed
        )
        self._btn_create.clicked.connect(self._on_create_piece)
        self._btn_apply.clicked.connect(self._on_apply_preset)

        # Each spinbox → auto-apply to work object
        for name, sb in self._spinboxes.items():
            sb.valueChanged.connect(self._on_spinbox_changed)

    def _connect_selection_observer(self) -> None:
        """Subscribe to FreeCAD selection changes to load TF_* objects."""
        try:
            import FreeCADGui as _Gui
            observer = _SelectionObserver(self)
            _Gui.Selection.addObserver(observer)
            self._observer = observer  # prevent GC
        except Exception:
            self._observer = None

    # ── Callbacks ──────────────────────────────────────────────────

    def _on_piece_type_changed(self, index: int) -> None:
        """Show/hide spinboxes depending on selected piece type."""
        if self._block_signals:
            return
        key = self._combo_type.itemData(index)
        if key is None:
            return
        visibility = _FIELDS_BY_TYPE.get(key, {})
        for name, sb in self._spinboxes.items():
            sb.setVisible(visibility.get(name, True))
        # Update work object's PieceType if it exists
        if self._work_obj is not None:
            self._set_work_obj_piece_type(key)

    def _on_preset_changed(self, index: int) -> None:
        """Apply preset values to spinboxes (except for 'Custom')."""
        if self._block_signals:
            return
        preset_data = self._combo_preset.itemData(index)
        if preset_data is None:
            return  # 'Custom' selected — don't touch spinboxes
        props = preset_to_props_map(preset_data)
        self._block_signals = True
        try:
            for name, sb in self._spinboxes.items():
                if name in props:
                    sb.setValue(props[name])
        finally:
            self._block_signals = False
        # Refresh the work object if one is selected
        if self._work_obj is not None:
            self._apply_props_to_work_obj()

    def _on_spinbox_changed(self, value: float) -> None:
        """Propagate spinbox value to the work object."""
        if self._block_signals:
            return
        if self._work_obj is None:
            return
        sb = self.sender()
        if sb is None:
            return
        prop_name = sb.property("propName")
        if prop_name and hasattr(self._work_obj, str(prop_name)):
            setattr(self._work_obj, str(prop_name), value)
            try:
                import FreeCAD as App
                App.ActiveDocument.recompute()
            except Exception:
                pass

    def _on_create_piece(self) -> None:
        """Create a new TriptaClamps3DFeature (or update existing)."""
        try:
            import FreeCAD as App
            import FreeCADGui as _Gui
        except ImportError:
            return

        if self._work_obj is not None:
            # Update existing object
            self._apply_props_to_work_obj()
            return

        # Create new object
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

        # Apply current panel values
        props = self._get_panel_props()
        for k, v in props.items():
            if hasattr(obj, k):
                setattr(obj, k, v)

        # Set piece type
        pt = self._combo_type.currentData()
        if pt:
            obj.PieceType = pt

        doc.recompute()

        # Select the new object
        try:
            _Gui.Selection.clearSelection()
            _Gui.Selection.addSelection(doc.Name, obj.Name)
        except Exception:
            pass

        # Set as work object
        self._set_work_obj(obj)

    def _on_apply_preset(self) -> None:
        """Button callback: apply current preset to spinboxes + work object."""
        idx = self._combo_preset.currentIndex()
        self._on_preset_changed(idx)

    # ── Work object management ─────────────────────────────────────

    def _set_work_obj(self, obj: Any) -> None:
        """Set the active TriptaClamps3D object and load its props."""
        self._work_obj = obj
        if obj is None:
            return
        # Load properties into spinboxes
        self._block_signals = True
        try:
            # Sync piece type combo
            pt = getattr(obj, "PieceType", "ferrula")
            for i in range(self._combo_type.count()):
                if self._combo_type.itemData(i) == pt:
                    self._combo_type.setCurrentIndex(i)
                    break
            # Sync spinboxes
            for name, sb in self._spinboxes.items():
                val = getattr(obj, name, 0.0)
                sb.setValue(float(val))
        finally:
            self._block_signals = False
        # Update visibility
        self._on_piece_type_changed(self._combo_type.currentIndex())

    def _set_work_obj_piece_type(self, pt: str) -> None:
        """Set PieceType on the work object and recompute."""
        if self._work_obj is None:
            return
        try:
            self._work_obj.PieceType = pt
            import FreeCAD as App
            App.ActiveDocument.recompute()
        except Exception:
            pass

    def _apply_props_to_work_obj(self) -> None:
        """Push all visible spinbox values into the work object."""
        if self._work_obj is None:
            return
        props = self._get_panel_props()
        for k, v in props.items():
            if hasattr(self._work_obj, k):
                setattr(self._work_obj, k, v)
        try:
            import FreeCAD as App
            App.ActiveDocument.recompute()
        except Exception:
            pass

    def _get_panel_props(self) -> Dict[str, float]:
        """Read current spinbox values into a dict."""
        return {
            name: sb.value()
            for name, sb in self._spinboxes.items()
        }

    # ── Public API ─────────────────────────────────────────────────

    def show(self) -> None:
        """Show the dock widget, creating it in the main window if needed."""
        mw = _get_main_window()
        if mw is None:
            return
        mw.addDockWidget(_QtCore.Qt.RightDockWidgetArea, self._dock)
        self._dock.show()

    def close(self) -> None:
        """Hide and remove the dock widget."""
        self._dock.hide()

    def widget(self) -> Any:
        """Return the inner QWidget (not the dock)."""
        return self._widget

    def dock_widget(self) -> Any:
        """Return the QDockWidget itself."""
        return self._dock

    def load_object(self, obj: Any) -> None:
        """Load a TriptaClamps3D object into the panel.

        Called by the selection observer when the user selects a TF_* object.
        """
        if obj is not None and getattr(obj, "Proxy", None) is not None:
            tp = getattr(obj.Proxy, "Type", None)
            if tp == "TriptaClamps3DFeature":
                self._set_work_obj(obj)
                return
        # Not a TF_* — keep the current work object


# ── Selection observer ─────────────────────────────────────────────

class _SelectionObserver:
    """Minimal FreeCAD selection observer to sync the panel."""

    def __init__(self, panel: TriptaClamps3DPanel) -> None:
        self._panel = panel

    def addSelection(self, doc_name: str, obj_name: str, *args: Any) -> None:
        """Called when an object is selected in FreeCAD."""
        try:
            import FreeCAD as App
            doc = App.getDocument(doc_name)
            if doc is None:
                return
            obj = doc.getObject(obj_name)
            self._panel.load_object(obj)
        except Exception:
            pass

    def removeSelection(self, doc_name: str, obj_name: str, *args: Any) -> None:
        """Called when an object is deselected."""
        pass

    def setSelection(self, doc_name: str, obj_names: list) -> None:
        """Called when the entire selection is replaced."""
        if obj_names:
            self.addSelection(doc_name, obj_names[0])

    def clearSelection(self, doc_name: str) -> None:
        """Called when selection is cleared."""
        pass


# ── Singleton accessor ─────────────────────────────────────────────

def get_panel() -> Optional[TriptaClamps3DPanel]:
    """Return (and lazily create) the singleton TriptaClamps3DPanel.

    Returns ``None`` when the GUI is not available.
    """
    global _panel_instance
    if not _has_gui:
        return None
    if _panel_instance is None:
        _panel_instance = TriptaClamps3DPanel()
    return _panel_instance


def open_panel() -> None:
    """Create (if needed) and show the dock panel.

    Called by the ``TriptaClamps3DOpenPanel`` command.
    """
    panel = get_panel()
    if panel is not None:
        panel.show()

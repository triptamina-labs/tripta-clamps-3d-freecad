"""Tests puros de geometry.py — conversión de perfiles a segmentos.

Usa los params del preset 1.5" TC64 con bead_radius=1.5.
Verifica continuidad, número de segmentos, propiedades de arcos
(start/end/mid/radio) y la dirección correcta del mid-point.
"""

from __future__ import annotations

import math
import pytest

from tripta_clamps_3d.constraints import BEAD_RADIUS_DEFAULT
from tripta_clamps_3d.geometry import (
    ArcSegment,
    Line,
    Point,
    profile_to_segments,
)
from tripta_clamps_3d.presets import preset_por_nombre
from tripta_clamps_3d.profile_cmds import Arc, MoveTo, LineTo, obtener_perfil

# ── Params del preset 1.5" TC64 ─────────────────────────────

_PRESET = preset_por_nombre('1.5" · TC64')
_PARAMS_BASE = {
    "tubeID": _PRESET["tube_id"],
    "tubeOD": _PRESET["tube_od"],
    "ferruleOD": _PRESET["ferrule_od"],
    "beadDistance": _PRESET["bead_distance"],
    "beadRadius": BEAD_RADIUS_DEFAULT,
    "spoolLength": 100.0,
    "tubeHeight": _PRESET["tube_height_larga"],
    "ferrHeight": 2.0,
    "gasketThickness": _PRESET["gasket_thickness"],
}


# ── Helper ───────────────────────────────────────────────────


def _cmds(tipo: str):
    return obtener_perfil(tipo, _PARAMS_BASE)


def _segments(tipo: str) -> list:
    """Obtiene perfiles y los convierte a segmentos."""
    return profile_to_segments(_cmds(tipo))


# ── Continuidad del wire ─────────────────────────────────────


@pytest.mark.parametrize("tipo", ["ferrula", "gasket", "spool", "endcap"])
def test_wire_continuity(tipo):
    """El punto final de cada segmento debe coincidir con el inicial del siguiente."""
    segs = _segments(tipo)
    assert len(segs) >= 2
    EPS = 1e-9
    for i in range(len(segs) - 1):
        end = segs[i].end if isinstance(segs[i], ArcSegment) else segs[i].p2
        start = segs[i + 1].start if isinstance(segs[i + 1], ArcSegment) else segs[i + 1].p1
        assert abs(end.x - start.x) < EPS, f"Segmento {i}→{i+1}: x discontinuo"
        assert abs(end.y - start.y) < EPS, f"Segmento {i}→{i+1}: y discontinuo"


# ── Nº de segmentos = Nº de comandos menos MoveTo ───────────


@pytest.mark.parametrize("tipo", ["ferrula", "gasket", "spool", "endcap"])
def test_segment_count_matches_commands(tipo):
    """Nº de segmentos = Nº de comandos - 1 (un solo MoveTo al inicio)."""
    cmds = _cmds(tipo)
    segs = _segments(tipo)
    assert len(segs) == len(cmds) - 1, (
        f"{tipo}: esperado {len(cmds)-1} segmentos, obtenido {len(segs)}"
    )


# ── Propiedades de arcos ─────────────────────────────────────


@pytest.mark.parametrize("tipo", ["ferrula", "gasket", "spool", "endcap"])
def test_arc_properties(tipo):
    """Cada ArcSegment tiene start/end correctos y radio == r."""
    cmds = _cmds(tipo)
    segs = _segments(tipo)
    # Filtrar arcos por tipo (Arc vs ArcSegment)
    arc_cmds = [c for c in cmds if isinstance(c, Arc)]
    arc_segs = [s for s in segs if isinstance(s, ArcSegment)]
    assert len(arc_cmds) == len(arc_segs), f"{tipo}: distinto nº de arcos"

    for cmd, seg in zip(arc_cmds, arc_segs):
        # start/end del cmd
        expected_sx = cmd.cx + cmd.r * math.cos(cmd.a0)
        expected_sy = cmd.cy + cmd.r * math.sin(cmd.a0)
        expected_ex = cmd.cx + cmd.r * math.cos(cmd.a1)
        expected_ey = cmd.cy + cmd.r * math.sin(cmd.a1)
        assert abs(seg.start.x - expected_sx) < 1e-9
        assert abs(seg.start.y - expected_sy) < 1e-9
        assert abs(seg.end.x - expected_ex) < 1e-9
        assert abs(seg.end.y - expected_ey) < 1e-9
        # Radio del mid-point respecto al center
        dx = seg.mid.x - seg.center.x
        dy = seg.mid.y - seg.center.y
        r_mid = math.sqrt(dx * dx + dy * dy)
        assert abs(r_mid - cmd.r) < 1e-9, (
            f"{tipo} arc: radio mid={r_mid}, esperado {cmd.r}"
        )


# ── Caso gasket: bead superior mid-point ─────────────────────


def test_gasket_bead_superior_mid():
    """El primer arco del gasket (bead superior) tiene mid.y = em + bR."""
    p = _PARAMS_BASE
    em = p["gasketThickness"] / 2
    bR = p["beadRadius"]
    segs = _segments("gasket")
    arc_segs = [s for s in segs if isinstance(s, ArcSegment)]
    assert len(arc_segs) == 2
    # Primer arco = bead superior
    arc_sup = arc_segs[0]
    assert abs(arc_sup.mid.y - (em + bR)) < 1e-9, (
        f"Gasket bead superior mid.y={arc_sup.mid.y}, esperado {em + bR}"
    )


# ── Caso spool: bead superior mid-point ──────────────────────


def test_spool_bead_superior_mid():
    """El segundo arco del spool (bead superior) tiene mid.y = totalH - bR."""
    p = _PARAMS_BASE
    bR = p["beadRadius"]
    tH = p["tubeHeight"]
    sL = p["spoolLength"]
    totalH = 2 * tH + sL
    segs = _segments("spool")
    arc_segs = [s for s in segs if isinstance(s, ArcSegment)]
    assert len(arc_segs) == 2
    # Segundo arco = bead superior
    arc_sup = arc_segs[1]
    assert abs(arc_sup.mid.y - (totalH - bR)) < 1e-9, (
        f"Spool bead superior mid.y={arc_sup.mid.y}, esperado {totalH - bR}"
    )


# ── Caso spool: bead inferior mid-point ──────────────────────


def test_spool_bead_inferior_mid():
    """El primer arco del spool (bead inferior) tiene mid.y = bR."""
    p = _PARAMS_BASE
    bR = p["beadRadius"]
    segs = _segments("spool")
    arc_segs = [s for s in segs if isinstance(s, ArcSegment)]
    assert len(arc_segs) == 2
    arc_inf = arc_segs[0]
    assert abs(arc_inf.mid.y - bR) < 1e-9, (
        f"Spool bead inferior mid.y={arc_inf.mid.y}, esperado {bR}"
    )


# ── Caso gasket: bead inferior mid-point ─────────────────────


def test_gasket_bead_inferior_mid():
    """El segundo arco del gasket (bead inferior) tiene mid.y = -em - bR."""
    p = _PARAMS_BASE
    em = p["gasketThickness"] / 2
    bR = p["beadRadius"]
    segs = _segments("gasket")
    arc_segs = [s for s in segs if isinstance(s, ArcSegment)]
    assert len(arc_segs) == 2
    arc_inf = arc_segs[1]
    assert abs(arc_inf.mid.y - (-em - bR)) < 1e-9, (
        f"Gasket bead inferior mid.y={arc_inf.mid.y}, esperado {-em - bR}"
    )


# ── Discontinuidad detectada ─────────────────────────────────


def test_discontinuity_raises():
    """Un LineTo sin MoveTo previo lanza ValueError."""
    with pytest.raises(ValueError, match="sin punto inicial"):
        profile_to_segments([LineTo(1.0, 2.0)])

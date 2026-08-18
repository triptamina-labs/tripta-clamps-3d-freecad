"""Conversión de comandos de perfil a segmentos geométricos 2-D.

Módulo **puro** (sin dependencias de FreeCAD).  Toma la lista de
``ProfileCmd`` producida por ``obtener_perfil`` y devuelve una lista de
``Line | ArcSegment`` con todas las coordenadas ya resueltas.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Union

from tripta_clamps_3d.profile_cmds import MoveTo, LineTo, Arc, ProfileCmd


# ── Segmentos geométricos ────────────────────────────────────


@dataclass(frozen=True, slots=True)
class Point:
    """Punto 2-D."""
    x: float
    y: float


@dataclass(frozen=True, slots=True)
class Line:
    """Segmento recto entre dos puntos."""
    p1: Point
    p2: Point


@dataclass(frozen=True, slots=True)
class ArcSegment:
    """Segmento de arco con start/end/mid calculados."""
    center: Point
    start: Point
    end: Point
    mid: Point
    ccw: bool


Segment = Union[Line, ArcSegment]


# ── Funciones auxiliares ─────────────────────────────────────


def _point(cmd: MoveTo | LineTo) -> Point:
    """Extrae el punto de un MoveTo o LineTo."""
    return Point(cmd.x, cmd.y)


def _arc_start(cmd: Arc) -> Point:
    """Punto inicial del arco: S = (cx + r*cos(a0), cy + r*sin(a0))."""
    return Point(
        cmd.cx + cmd.r * math.cos(cmd.a0),
        cmd.cy + cmd.r * math.sin(cmd.a0),
    )


def _arc_end(cmd: Arc) -> Point:
    """Punto final del arco: E = (cx + r*cos(a1), cy + r*sin(a1))."""
    return Point(
        cmd.cx + cmd.r * math.cos(cmd.a1),
        cmd.cy + cmd.r * math.sin(cmd.a1),
    )


def _arc_mid(cmd: Arc) -> Point:
    """Punto medio del arco según la dirección de recorrido.

    Si ccw=True  → recorre de a0 a a1 en ángulo creciente (CCW).
    Si ccw=False → recorre de a0 a a1 en ángulo decreciente (CW).

    Fórmula:
      - CCW: delta = (a1 - a0) mod 2π  →  mid = a0 + delta/2
      - CW:  delta = (a0 - a1) mod 2π  →  mid = a0 - delta/2
    """
    two_pi = 2.0 * math.pi
    if cmd.ccw:
        delta = (cmd.a1 - cmd.a0) % two_pi
        if delta == 0:
            delta = two_pi  # círculo completo (degenerado)
        mid_angle = cmd.a0 + delta / 2.0
    else:
        delta = (cmd.a0 - cmd.a1) % two_pi
        if delta == 0:
            delta = two_pi
        mid_angle = cmd.a0 - delta / 2.0
    return Point(
        cmd.cx + cmd.r * math.cos(mid_angle),
        cmd.cy + cmd.r * math.sin(mid_angle),
    )


# ── Función principal ────────────────────────────────────────


def profile_to_segments(cmds: list[ProfileCmd]) -> list[Segment]:
    """Convierte comandos de perfil en segmentos geométricos 2-D.

    Raises:
        ValueError: Si hay discontinuidad entre comandos consecutivos
                    (el punto final de uno ≠ punto inicial del siguiente).
    """
    if not cmds:
        return []

    segments: list[Segment] = []
    prev_end: Point | None = None

    for cmd in cmds:
        if isinstance(cmd, MoveTo):
            p = _point(cmd)
            prev_end = p  # MoveTo no genera segmento

        elif isinstance(cmd, LineTo):
            p = _point(cmd)
            if prev_end is not None and (prev_end.x != p.x or prev_end.y != p.y):
                pass  # OK — línea
            # Si prev_end is None, es el primer comando → MoveTo + LineTo
            if prev_end is None:
                raise ValueError(
                    f"LineTo({cmd.x}, {cmd.y}) sin punto inicial previo"
                )
            segments.append(Line(p1=prev_end, p2=p))
            prev_end = p

        elif isinstance(cmd, Arc):
            start = _arc_start(cmd)
            end = _arc_end(cmd)
            mid = _arc_mid(cmd)
            # Validar que start es el punto donde estámos
            if prev_end is not None:
                dx = abs(prev_end.x - start.x)
                dy = abs(prev_end.y - start.y)
                if dx > 1e-9 or dy > 1e-9:
                    raise ValueError(
                        f"Arc discontinuidad: esperado ({prev_end.x}, {prev_end.y}), "
                        f"obtenido start ({start.x}, {start.y})"
                    )
            segments.append(
                ArcSegment(center=Point(cmd.cx, cmd.cy), start=start, end=end, mid=mid, ccw=cmd.ccw)
            )
            prev_end = end

        else:
            raise TypeError(f"Comando desconocido: {type(cmd)}")

    return segments

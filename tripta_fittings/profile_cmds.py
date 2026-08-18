"""Generadores de perfiles 2-D para piezas tri-clamp.

Puerto 1:1 desde ``profileDescriptor.ts`` del proyecto web.
Cálculos numéricos idénticos (mismas fórmulas, mismo orden de operaciones).
Sin dependencias externas — solo stdlib.

Tipos de comando de perfil
--------------------------
- ``MoveTo(x, y)`` — levanta el lápiz y se posiciona.
- ``LineTo(x, y)`` — traza una línea recta.
- ``Arc(cx, cy, r, a0, a1, ccw)`` — arco centrado, ángulos en radianes.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Union


# ── Comandos de perfil (dataclasses inmutables, 1:1 con TS) ──


@dataclass(frozen=True, slots=True)
class MoveTo:
    """MoveTo — equivalente TS: ``{type:'moveTo', x, y}``."""

    x: float
    y: float


@dataclass(frozen=True, slots=True)
class LineTo:
    """LineTo — equivalente TS: ``{type:'lineTo', x, y}``."""

    x: float
    y: float


@dataclass(frozen=True, slots=True)
class Arc:
    """Arc — equivalente TS: ``{type:'arc', cx, cy, r, a0, a1, ccw}``."""

    cx: float
    cy: float
    r: float
    a0: float
    a1: float
    ccw: bool


ProfileCmd = Union[MoveTo, LineTo, Arc]


# ── Generadores de perfil ──────────────────────────────────


def perfil_ferula(params: dict) -> list[ProfileCmd]:
    """Ferrule: sección de tubo con brida cónica y ranura de bead.

    Equivalente TS: ``perfilFerula()`` en ``profileDescriptor.ts:100``.
    """
    rID = params["tubeID"] / 2
    rOD = params["tubeOD"] / 2
    rF = params["ferruleOD"] / 2
    rbD = params["beadDistance"] / 2
    bR = params["beadRadius"]
    tH = params["tubeHeight"]
    fH = params["ferrHeight"]

    anguloRad = 20 * (math.pi / 180)
    distX = rF - rOD
    subidaY = distX * math.tan(anguloRad)
    puntoXY = fH + subidaY

    return [
        MoveTo(rID, tH),
        LineTo(rOD, tH),
        LineTo(rOD, puntoXY),
        LineTo(rF, fH),
        LineTo(rF, 0),
        LineTo(rbD + bR, 0),
        Arc(rbD, 0, bR, 0, math.pi, True),
        LineTo(rID, 0),
        LineTo(rID, tH),
    ]


def perfil_gasket(params: dict) -> list[ProfileCmd]:
    """Gasket: doble bead con espesor central.

    Equivalente TS: ``perfilGasket()`` en ``profileDescriptor.ts:132``.
    """
    rID = params["tubeID"] / 2
    rF = params["ferruleOD"] / 2
    rbD = params["beadDistance"] / 2
    bR = params["beadRadius"]
    em = params["gasketThickness"] / 2

    return [
        MoveTo(rID, em),
        LineTo(rbD - bR, em),
        Arc(rbD, em, bR, math.pi, 0, False),
        LineTo(rF, em),
        LineTo(rF, -em),
        LineTo(rbD + bR, -em),
        Arc(rbD, -em, bR, 0, math.pi, False),
        LineTo(rID, -em),
        LineTo(rID, em),
    ]


# ── Constantes end-cap (idénticas al TS) ──────────────────

ENDCAP_STEP_MM: float = 2.0
ENDCAP_MAX_HEIGHT_MM: float = 5.0
ENDCAP_TAPER_FROM_HORIZONTAL_DEG: float = 20.0


def perfil_endcap(params: dict) -> list[ProfileCmd]:
    """End-cap: cara interna plana con borde cónico y bead.

    Equivalente TS: ``perfilEndCap()`` en ``profileDescriptor.ts:164``.
    """
    rF = params["ferruleOD"] / 2
    rbD = params["beadDistance"] / 2
    bR = params["beadRadius"]
    stepH = ENDCAP_STEP_MM
    maxH = ENDCAP_MAX_HEIGHT_MM
    taperRad = ((180 - ENDCAP_TAPER_FROM_HORIZONTAL_DEG) * math.pi) / 180
    rise = maxH - stepH
    sinT = math.sin(taperRad)
    xTop = rF + (math.cos(taperRad) * rise) / sinT if sinT > 1e-6 else rF

    return [
        MoveTo(0, 0),
        LineTo(rbD - bR, 0),
        Arc(rbD, 0, bR, math.pi, 0, False),
        LineTo(rF, 0),
        LineTo(rF, stepH),
        LineTo(xTop, maxH),
        LineTo(0, maxH),
        LineTo(0, 0),
    ]


def perfil_spool(params: dict) -> list[ProfileCmd]:
    """Spool: sección de tubo con brida de ferrule en cada extremo.

    Equivalente TS: ``perfilSpool()`` en ``profileDescriptor.ts:192``.
    """
    rID = params["tubeID"] / 2
    rOD = params["tubeOD"] / 2
    rF = params["ferruleOD"] / 2
    rbD = params["beadDistance"] / 2
    bR = params["beadRadius"]
    tH = params["tubeHeight"]
    fH = params["ferrHeight"]
    sL = params["spoolLength"]

    anguloRad = 20 * (math.pi / 180)
    distX = rF - rOD
    subidaY = distX * math.tan(anguloRad)
    puntoXY = fH + subidaY
    totalH = 2 * tH + sL
    topPuntoXY = totalH - (fH + subidaY)
    topFH = totalH - fH

    return [
        MoveTo(rID, tH),
        LineTo(rID, 0),
        LineTo(rbD - bR, 0),
        Arc(rbD, 0, bR, math.pi, 0, False),
        LineTo(rF, 0),
        LineTo(rF, fH),
        LineTo(rOD, puntoXY),
        LineTo(rOD, tH),
        LineTo(rOD, tH + sL),
        LineTo(rOD, topPuntoXY),
        LineTo(rF, topFH),
        LineTo(rF, totalH),
        LineTo(rbD + bR, totalH),
        Arc(rbD, totalH, bR, 0, math.pi, False),
        LineTo(rID, totalH),
        LineTo(rID, tH),
    ]


# ── Dispatcher ──────────────────────────────────────────────


def obtener_perfil(tipo: str, params: dict) -> list[ProfileCmd]:
    """Devuelve el descriptor de perfil adecuado para ``tipo``.

    Equivalente TS: ``obtenerPerfil()`` en ``profileDescriptor.ts:236``.
    Fallback a ferrula para tipos desconocidos.
    """
    if tipo == "gasket":
        return perfil_gasket(params)
    elif tipo == "spool":
        return perfil_spool(params)
    elif tipo == "endcap":
        return perfil_endcap(params)
    else:
        return perfil_ferula(params)

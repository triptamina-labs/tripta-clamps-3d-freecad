"""triptya_fittings constraints module — constraints de dimensiones puro.

Port de src/core/constraints.ts y src/core/constants.ts.
"""

from __future__ import annotations

from typing import Any

# ── Constantes (de constants.ts) ───────────────────────────────────
# CONSTRAINT_EPSILON ≡ 0.2  (evita colisiones en límites de ferula/endcap)
CONSTRAINT_EPSILON: float = 0.2

# CONSTRAINT_MIN_GAP ≡ 0.5  (hueco mínimo entre límites de beadDistance en gasket)
CONSTRAINT_MIN_GAP: float = 0.5

# BEAD_RADIUS_DEFAULT ≡ 1.5  (radio por defecto del bead profile)
BEAD_RADIUS_DEFAULT: float = 1.5


def validate_and_clamp_dimensions(
    tipo: str,
    dims: dict[str, Any],
    bead_radius: float,
) -> dict[str, Any]:
    """Valida y clampa dimensiones según restricciones geométricas del tipo.

    Función pura: retorna una **nueva copia** del dict sin mutar la entrada.
    Misma lógica que `validateAndClampDimensions()` en constraints.ts.

    Args:
        tipo: Tipo de pieza ('gasket', 'endcap', 'ferrula', 'spool').
              'ferrula' y 'spool' comparten la rama default.
        dims: Dict con claves numéricas:
              tubeID, tubeOD, ferruleOD, beadDistance, spoolLength.
        bead_radius: Radio del bead (mm).

    Returns:
        Nuevo dict con las dimensiones clamped.
    """
    bR = bead_radius
    d: dict[str, Any] = dict(dims)  # copia superficial — no muta la entrada

    if tipo == "gasket":
        # ferruleOD debe ser al menos tubeID + 5
        if d["ferruleOD"] < d["tubeID"] + 5:
            d["ferruleOD"] = d["tubeID"] + 5

        min_bd = d["tubeID"] + bR * 2 + CONSTRAINT_MIN_GAP
        max_bd = d["ferruleOD"] - bR * 2 - CONSTRAINT_MIN_GAP
        if d["beadDistance"] < min_bd:
            d["beadDistance"] = min_bd
        if d["beadDistance"] > max_bd:
            d["beadDistance"] = max_bd

    elif tipo == "endcap":
        rF = d["ferruleOD"] / 2
        rbD = d["beadDistance"] / 2

        if rbD - bR < CONSTRAINT_EPSILON:
            rbD = bR + CONSTRAINT_EPSILON
            d["beadDistance"] = 2 * rbD
        if rbD + bR > rF - CONSTRAINT_EPSILON:
            rbD = rF - bR - CONSTRAINT_EPSILON
            d["beadDistance"] = 2 * rbD
        if rbD - bR < CONSTRAINT_EPSILON:
            rbD = bR + CONSTRAINT_EPSILON
            d["beadDistance"] = 2 * rbD
            rF = rbD + bR + CONSTRAINT_EPSILON
            d["ferruleOD"] = 2 * rF

    else:
        # default: ferrule / spool
        if d["tubeOD"] <= d["tubeID"] + 1:
            d["tubeOD"] = d["tubeID"] + 1
        if d["ferruleOD"] <= d["tubeOD"] + 2:
            d["ferruleOD"] = d["tubeOD"] + 2
        if d["beadDistance"] - bR * 2 <= d["tubeOD"]:
            d["beadDistance"] = d["tubeOD"] + bR * 2 + CONSTRAINT_EPSILON
        if d["beadDistance"] + bR * 2 >= d["ferruleOD"]:
            d["beadDistance"] = d["ferruleOD"] - bR * 2 - CONSTRAINT_EPSILON

    return d

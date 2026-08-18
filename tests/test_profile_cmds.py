"""Tests portados 1:1 de profileDescriptor.test.ts (vitest → pytest).

Parámetros de entrada idénticos a los del test TS.
Solo se testean generadores de perfiles y obtener_perfil (sin Three.js).
"""

from __future__ import annotations

import pytest

from tripta_clamps_3d.profile_cmds import (
    Arc,
    LineTo,
    MoveTo,
    obtener_perfil,
    perfil_endcap,
    perfil_ferula,
    perfil_gasket,
    perfil_spool,
)

# ── Parámetros exactos del test TS ──────────────────────────

FERRULE_PARAMS: dict = {
    "tubeID": 34.8,
    "tubeOD": 38.1,
    "ferruleOD": 63.9,
    "beadDistance": 50.7,
    "beadRadius": 1.5,
    "tubeHeight": 28.6,
    "ferrHeight": 2.0,
}

GASKET_PARAMS: dict = {
    "tubeID": 34.8,
    "ferruleOD": 63.9,
    "beadDistance": 50.7,
    "beadRadius": 1.5,
    "gasketThickness": 2.25,
}

ENDCAP_PARAMS: dict = {
    "ferruleOD": 63.9,
    "beadDistance": 50.7,
    "beadRadius": 1.5,
}

SPOOL_PARAMS: dict = {
    "tubeID": 34.8,
    "tubeOD": 38.1,
    "ferruleOD": 63.9,
    "beadDistance": 50.7,
    "spoolLength": 50,
    "beadRadius": 1.5,
    "tubeHeight": 28.6,
    "ferrHeight": 2.0,
}


# ── perfilFerula ────────────────────────────────────────────


class TestPerfilFerula:
    def test_returns_9_commands(self) -> None:
        cmds = perfil_ferula(FERRULE_PARAMS)
        assert len(cmds) == 9

    def test_first_command_is_moveTo_with_correct_coordinates(self) -> None:
        cmds = perfil_ferula(FERRULE_PARAMS)
        first = cmds[0]
        assert isinstance(first, MoveTo)
        assert first.x == FERRULE_PARAMS["tubeID"] / 2
        assert first.y == FERRULE_PARAMS["tubeHeight"]

    def test_last_command_closes_profile(self) -> None:
        cmds = perfil_ferula(FERRULE_PARAMS)
        last = cmds[-1]
        assert isinstance(last, LineTo)
        assert last.x == FERRULE_PARAMS["tubeID"] / 2
        assert last.y == FERRULE_PARAMS["tubeHeight"]

    def test_contains_one_arc_for_bead(self) -> None:
        cmds = perfil_ferula(FERRULE_PARAMS)
        arcs = [c for c in cmds if isinstance(c, Arc)]
        assert len(arcs) == 1
        assert arcs[0].cx == FERRULE_PARAMS["beadDistance"] / 2
        assert arcs[0].cy == 0


# ── perfilGasket ────────────────────────────────────────────


class TestPerfilGasket:
    def test_returns_9_commands(self) -> None:
        cmds = perfil_gasket(GASKET_PARAMS)
        assert len(cmds) == 9

    def test_first_command_is_moveTo_at_center(self) -> None:
        cmds = perfil_gasket(GASKET_PARAMS)
        first = cmds[0]
        assert isinstance(first, MoveTo)
        assert first.x == GASKET_PARAMS["tubeID"] / 2
        assert first.y == GASKET_PARAMS["gasketThickness"] / 2

    def test_is_symmetric_about_y0(self) -> None:
        cmds = perfil_gasket(GASKET_PARAMS)
        em = GASKET_PARAMS["gasketThickness"] / 2
        first = cmds[0]
        assert isinstance(first, MoveTo)
        assert first.y == em
        last = cmds[-1]
        assert isinstance(last, LineTo)
        assert last.y == em
        neg_y = [c for c in cmds if isinstance(c, LineTo) and c.y == -em]
        assert len(neg_y) > 0

    def test_contains_two_arcs_for_double_bead(self) -> None:
        cmds = perfil_gasket(GASKET_PARAMS)
        arcs = [c for c in cmds if isinstance(c, Arc)]
        assert len(arcs) == 2


# ── perfilEndCap ────────────────────────────────────────────


class TestPerfilEndCap:
    def test_returns_8_commands(self) -> None:
        cmds = perfil_endcap(ENDCAP_PARAMS)
        assert len(cmds) == 8

    def test_first_command_is_moveTo_at_origin(self) -> None:
        cmds = perfil_endcap(ENDCAP_PARAMS)
        first = cmds[0]
        assert isinstance(first, MoveTo)
        assert first.x == 0
        assert first.y == 0

    def test_last_command_closes_at_origin(self) -> None:
        cmds = perfil_endcap(ENDCAP_PARAMS)
        last = cmds[-1]
        assert isinstance(last, LineTo)
        assert last.x == 0
        assert last.y == 0

    def test_contains_exactly_one_arc(self) -> None:
        cmds = perfil_endcap(ENDCAP_PARAMS)
        arcs = [c for c in cmds if isinstance(c, Arc)]
        assert len(arcs) == 1


# ── perfilSpool ─────────────────────────────────────────────


class TestPerfilSpool:
    def test_returns_16_commands(self) -> None:
        cmds = perfil_spool(SPOOL_PARAMS)
        assert len(cmds) == 16

    def test_first_command_is_moveTo_at_start(self) -> None:
        cmds = perfil_spool(SPOOL_PARAMS)
        first = cmds[0]
        assert isinstance(first, MoveTo)
        assert first.x == SPOOL_PARAMS["tubeID"] / 2
        assert first.y == SPOOL_PARAMS["tubeHeight"]

    def test_last_command_returns_to_start(self) -> None:
        cmds = perfil_spool(SPOOL_PARAMS)
        last = cmds[-1]
        assert isinstance(last, LineTo)
        assert last.x == SPOOL_PARAMS["tubeID"] / 2
        assert last.y == SPOOL_PARAMS["tubeHeight"]

    def test_contains_two_arcs(self) -> None:
        cmds = perfil_spool(SPOOL_PARAMS)
        arcs = [c for c in cmds if isinstance(c, Arc)]
        assert len(arcs) == 2

    def test_bottom_bead_arc_at_y0(self) -> None:
        cmds = perfil_spool(SPOOL_PARAMS)
        arcs = [c for c in cmds if isinstance(c, Arc)]
        assert arcs[0].cy == 0

    def test_top_bead_arc_at_total_height(self) -> None:
        cmds = perfil_spool(SPOOL_PARAMS)
        arcs = [c for c in cmds if isinstance(c, Arc)]
        total_h = 2 * SPOOL_PARAMS["tubeHeight"] + SPOOL_PARAMS["spoolLength"]
        assert arcs[1].cy == total_h


# ── obtenerPerfil ───────────────────────────────────────────


class TestObtenerPerfil:
    def test_dispatches_gasket(self) -> None:
        cmds = obtener_perfil("gasket", GASKET_PARAMS)
        assert len(cmds) == 9
        assert isinstance(cmds[0], MoveTo)

    def test_dispatches_spool(self) -> None:
        cmds = obtener_perfil("spool", SPOOL_PARAMS)
        assert len(cmds) == 16

    def test_dispatches_endcap(self) -> None:
        cmds = obtener_perfil("endcap", ENDCAP_PARAMS)
        assert len(cmds) == 8

    def test_dispatches_ferrula(self) -> None:
        cmds = obtener_perfil("ferrula", FERRULE_PARAMS)
        assert len(cmds) == 9

    def test_defaults_to_ferrula_for_unknown(self) -> None:
        cmds = obtener_perfil("unknown_type", FERRULE_PARAMS)
        assert len(cmds) == 9

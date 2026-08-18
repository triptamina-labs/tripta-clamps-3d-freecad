"""Tests portados de constraints.test.ts y constants.test.ts (T2)."""
from tripta_fittings.constraints import (
    CONSTRAINT_EPSILON,
    CONSTRAINT_MIN_GAP,
    BEAD_RADIUS_DEFAULT,
    validate_and_clamp_dimensions,
)

DEFAULT_BEAD_RADIUS = BEAD_RADIUS_DEFAULT  # 1.5

BASE_DIMS = {
    "tubeID": 34.8,
    "tubeOD": 38.1,
    "ferruleOD": 63.9,
    "beadDistance": 50.7,
    "spoolLength": 50,
}


# ── constants.test.ts ──────────────────────────────────────────────
class TestConstants:
    def test_epsilon(self):
        assert CONSTRAINT_EPSILON == 0.2

    def test_min_gap(self):
        assert CONSTRAINT_MIN_GAP == 0.5

    def test_bead_radius_default(self):
        assert BEAD_RADIUS_DEFAULT == 1.5


# ── constraints.test.ts ────────────────────────────────────────────
class TestGasket:
    def test_does_not_modify_valid(self):
        result = validate_and_clamp_dimensions("gasket", BASE_DIMS, DEFAULT_BEAD_RADIUS)
        assert result["tubeID"] == 34.8
        assert result["ferruleOD"] == 63.9
        assert result["beadDistance"] == 50.7

    def test_clamps_ferrule_od_below_tube_id_plus_5(self):
        dims = {**BASE_DIMS, "ferruleOD": 35}
        result = validate_and_clamp_dimensions("gasket", dims, DEFAULT_BEAD_RADIUS)
        assert result["ferruleOD"] == dims["tubeID"] + 5

    def test_clamps_bead_distance_below_minimum(self):
        dims = {**BASE_DIMS, "beadDistance": 10}
        result = validate_and_clamp_dimensions("gasket", dims, DEFAULT_BEAD_RADIUS)
        min_bd = dims["tubeID"] + DEFAULT_BEAD_RADIUS * 2 + CONSTRAINT_MIN_GAP
        assert result["beadDistance"] == min_bd

    def test_clamps_bead_distance_above_maximum(self):
        dims = {**BASE_DIMS, "beadDistance": 200}
        result = validate_and_clamp_dimensions("gasket", dims, DEFAULT_BEAD_RADIUS)
        max_bd = dims["ferruleOD"] - DEFAULT_BEAD_RADIUS * 2 - CONSTRAINT_MIN_GAP
        assert result["beadDistance"] == max_bd


class TestEndcap:
    def test_clamps_when_boundary_violated(self):
        dims = {"tubeID": 10, "tubeOD": 12, "ferruleOD": 10, "beadDistance": 12, "spoolLength": 0}
        result = validate_and_clamp_dimensions("endcap", dims, DEFAULT_BEAD_RADIUS)
        assert result["beadDistance"] < 12

    def test_does_not_modify_valid(self):
        dims = {"tubeID": 30, "tubeOD": 35, "ferruleOD": 63.9, "beadDistance": 50.7, "spoolLength": 0}
        result = validate_and_clamp_dimensions("endcap", dims, DEFAULT_BEAD_RADIUS)
        assert result["beadDistance"] == 50.7


class TestFerrulaSpool:
    def test_clamps_tube_od_and_ferrule_od_when_too_close(self):
        dims = {"tubeID": 30, "tubeOD": 30.5, "ferruleOD": 31, "beadDistance": 50, "spoolLength": 0}
        result = validate_and_clamp_dimensions("ferrula", dims, DEFAULT_BEAD_RADIUS)
        assert result["tubeOD"] == dims["tubeID"] + 1
        assert result["ferruleOD"] == dims["tubeID"] + 1 + 2

    def test_clamps_bead_distance_into_feasible_range(self):
        dims = {"tubeID": 30, "tubeOD": 35, "ferruleOD": 60, "beadDistance": 10, "spoolLength": 0}
        result = validate_and_clamp_dimensions("ferrula", dims, DEFAULT_BEAD_RADIUS)
        assert result["beadDistance"] > 10

    def test_preserves_spool_length(self):
        dims = {"tubeID": 30, "tubeOD": 35, "ferruleOD": 60, "beadDistance": 50, "spoolLength": 123}
        result = validate_and_clamp_dimensions("spool", dims, DEFAULT_BEAD_RADIUS)
        assert result["spoolLength"] == 123

    def test_returns_new_object_does_not_mutate_input(self):
        original = {**BASE_DIMS}
        result = validate_and_clamp_dimensions("ferrula", original, DEFAULT_BEAD_RADIUS)
        assert result is not original
        assert original["tubeID"] == 34.8

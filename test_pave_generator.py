from brain.pave_generator import PaveGenerator


def test_staggered_plan():
    generator = PaveGenerator()
    plan = generator.create_pave_plan(
        area_width=10.0,
        area_length=20.0,
        stone_size=1.2,
        gap=0.08,
        edge_margin=0.3,
        layout="staggered",
    )

    assert plan["status"] == "planned"
    assert plan["layout"] == "staggered"
    assert round(plan["center_distance"], 2) == 1.28
    assert plan["row_count"] == 15
    assert plan["stones_per_full_row"] == 7
    assert plan["stones_per_short_row"] == 6
    assert plan["estimated_stone_count"] == 98


def test_straight_plan():
    generator = PaveGenerator()
    plan = generator.create_pave_plan(
        area_width=5.0,
        area_length=5.0,
        stone_size=1.0,
        gap=0.1,
        edge_margin=0.25,
        layout="straight",
    )

    assert plan["status"] == "planned"
    assert plan["row_count"] == 4
    assert plan["stones_per_full_row"] == 4
    assert plan["estimated_stone_count"] == 16


def test_area_too_small():
    generator = PaveGenerator()
    plan = generator.create_pave_plan(
        area_width=1.0,
        area_length=1.0,
        stone_size=1.2,
        edge_margin=0.1,
    )

    assert plan["status"] == "area_too_small"
    assert plan["estimated_stone_count"] == 0


def test_unsupported_layout():
    generator = PaveGenerator()
    plan = generator.create_pave_plan(
        area_width=10.0,
        area_length=10.0,
        layout="honeycomb",
    )

    assert plan["status"] == "unsupported_layout"
    assert plan["estimated_stone_count"] == 0


def test_invalid_dimensions_raise_value_error():
    generator = PaveGenerator()

    try:
        generator.create_pave_plan(area_width=0, area_length=10)
    except ValueError as exc:
        assert "area_width" in str(exc)
    else:
        raise AssertionError("Expected ValueError for zero area_width")


if __name__ == "__main__":
    test_staggered_plan()
    test_straight_plan()
    test_area_too_small()
    test_unsupported_layout()
    test_invalid_dimensions_raise_value_error()
    print("Pavé Generator V1 tests passed")

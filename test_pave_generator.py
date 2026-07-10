from brain.pave_generator import PaveGenerator


def print_pave_plan(title, plan):
    print(title)
    print("-" * len(title))
    for key, value in plan.items():
        print(f"{key}: {value}")
    print()


if __name__ == "__main__":
    generator = PaveGenerator()

    rectangular_staggered_plan = generator.create_pave_plan(
        length=20.0,
        width_start=5.0,
        width_end=5.0,
        stone_size=1.2,
        gap=0.08,
        edge_margin=0.45,
        layout="staggered",
    )
    tapered_staggered_plan = generator.create_pave_plan(
        length=20.0,
        width_start=3.0,
        width_end=7.0,
        stone_size=1.2,
        gap=0.08,
        edge_margin=0.45,
        layout="staggered",
    )
    rectangular_grid_plan = generator.create_pave_plan(
        length=20.0,
        width_start=5.0,
        width_end=5.0,
        stone_size=1.2,
        gap=0.08,
        edge_margin=0.45,
        layout="grid",
    )

    print_pave_plan("Case 1: Rectangular Staggered Pavé Plan", rectangular_staggered_plan)
    print_pave_plan("Case 2: Tapered Staggered Pavé Plan", tapered_staggered_plan)
    print_pave_plan("Case 3: Rectangular Grid Pavé Plan", rectangular_grid_plan)

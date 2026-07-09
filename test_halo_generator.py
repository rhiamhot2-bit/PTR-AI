from brain.halo_generator import HaloGenerator


def print_halo_plan(title, plan):
    print(title)
    print("-" * len(title))
    for key, value in plan.items():
        print(f"{key}: {value}")
    print()


if __name__ == "__main__":
    generator = HaloGenerator()

    round_plan = generator.create_halo_plan(
        center_shape="Round",
        center_size=6.0,
        stone_size=1.2,
    )
    oval_plan = generator.create_halo_plan(
        center_shape="Oval",
        center_size="8x10",
        stone_size=1.2,
    )

    print_halo_plan("Round 6.0 Halo Plan", round_plan)
    print_halo_plan("Oval 8x10 Halo Plan", oval_plan)

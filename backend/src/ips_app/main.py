import argparse
import asyncio


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ips_app entrypoint")
    parser.add_argument("mode", choices=["main", "seeder"], nargs="?", default="main")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if args.mode == "seeder":
        from ips_app.composition.seeder.launcher import main as seeder_main
        asyncio.run(seeder_main())
    else:
        raise NotImplementedError("The main app composition is not implemented yet.")


if __name__ == "__main__":
    main()

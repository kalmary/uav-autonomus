"""Validate configuration before a planning runtime is connected."""

import argparse
from dataclasses import asdict, replace
import json
from pathlib import Path

from .config import PlannerConfig, load_config


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, help="Path to a planner YAML file")
    parser.add_argument(
        "--preplan",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Enable initial planning when geometry is available; overrides YAML",
    )
    args = parser.parse_args()
    try:
        config = load_config(args.config) if args.config else PlannerConfig()
        if args.preplan is not None:
            config = replace(config, preplan=args.preplan)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(asdict(config), indent=2))


if __name__ == "__main__":
    main()

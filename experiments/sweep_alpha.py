from __future__ import annotations

import argparse
import os

from uav_aoi.config import load_config
from uav_aoi.metrics import compute_metrics
from uav_aoi.viz import plot_pareto
from main import do_sweep_alpha, make_parser


def main():
    parser = make_parser()
    args = parser.parse_args()
    if args.cmd != "sweep-alpha":
        parser.error("Use subcommand sweep-alpha")
    do_sweep_alpha(args)


if __name__ == "__main__":
    main()



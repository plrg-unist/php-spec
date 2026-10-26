#!/usr/bin/env python3
"""Compare the two frozen fresh-Iterator sources with a measured CLI budget."""
import argparse
from pathlib import Path
import sys

import config_aggregate_fresh_iterator_sources as sources


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    names = ('fresh-return-normal-sole-data', 'fresh-return-key-exception-sole-data')
    sources.family.CASES = {name: sources.family.CASES[name] for name in names}
    sources.family.MODEL_TIMEOUTS = {name: 90 for name in names}
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(sources.family.ROOT)): sources.family.sha(__file__)})
    sys.argv = [sys.argv[0], '--phase', 'model', '--output', str(args.output)]
    sources.family.main()


if __name__ == '__main__':
    main()

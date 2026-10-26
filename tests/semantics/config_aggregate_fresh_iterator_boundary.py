#!/usr/bin/env python3
"""Keep the frozen Aggregate invalid-key case explicitly Unsupported."""
import argparse
from pathlib import Path
import sys

import config_aggregate_fresh_iterator_sources as sources


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    name = 'fresh-return-invalid-key-boundary'
    sources.family.CASES = {name: sources.family.CASES[name]}
    sources.family.MODEL_TIMEOUTS = {name: 90}
    sources.family.UNSUPPORTED = {name: (
        'CONFIG Iterator unpack key outside integer domain',
        b'B|G|R|V0|C0|H|K0|H|N0|V1|C1|H|K1|H|')}
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(sources.family.ROOT)): sources.family.sha(__file__)})
    sys.argv = [sys.argv[0], '--phase', 'model', '--case', name, '--output', str(args.output)]
    sources.family.main()


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Native-pinned destructor declaration priority and compiled-global order."""
import argparse
from pathlib import Path

import shutdown_review

shutdown_review.CASES = Path(__file__).with_name('destructor_cases.json')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--match', default='')
    parser.add_argument('--native-report', type=Path, action='append', default=[])
    args = parser.parse_args()
    raise SystemExit(0 if shutdown_review.run(args.match, [], '', False,
                                            args.native_report) else 1)

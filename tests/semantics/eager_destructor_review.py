#!/usr/bin/env python3
"""Independent original-source tuples for ordinary eager destructor dispatch."""
import argparse
from pathlib import Path

import shutdown_review

shutdown_review.CASES = Path(__file__).with_name('eager_destructor_review_cases.json')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--match', default='')
    parser.add_argument('--native-only', action='store_true')
    parser.add_argument('--start-at')
    parser.add_argument('--exclude-match', action='append', default=[])
    parser.add_argument('--native-report', type=Path, action='append', default=[])
    args = parser.parse_args()
    passed = shutdown_review.run(args.match, args.exclude_match, args.start_at,
                                 args.native_only, args.native_report)
    raise SystemExit(0 if passed else 1)

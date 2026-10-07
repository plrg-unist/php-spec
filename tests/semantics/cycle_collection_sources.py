#!/usr/bin/env python3
"""Original explicit cycle-collection sources on the pinned local profile."""
import argparse
from pathlib import Path
import shutdown_review as runner
runner.CASES=Path(__file__).with_name('cycle_collection_cases.json')
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--match',default='')
    parser.add_argument('--native-only',action='store_true')
    parser.add_argument('--start-at')
    parser.add_argument('--exclude-match',action='append',default=[])
    parser.add_argument('--native-report',type=Path,action='append',default=[])
    args=parser.parse_args()
    raise SystemExit(0 if runner.run(args.match,args.exclude_match,args.start_at,args.native_only,args.native_report) else 1)

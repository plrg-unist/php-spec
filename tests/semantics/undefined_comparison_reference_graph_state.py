#!/usr/bin/env python3
"""Check successive singleton unwrapping and live reference-graph ownership."""
import argparse
import json
from pathlib import Path

from undefined_comparison_reference_graph_cases import CASES
from undefined_comparison_reference_graph_protocol import PREFIX, checks, budget_setup
from undefined_spaceship_state import ROOT, run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    selected = {name+'-'+group:CASES[name] for name in (
        'reference-graph-captured-shared-branches','reference-graph-live-held-payload')
        for group in ('state','budget')}
    if args.case is not None:
        assert len(args.case)==len(set(args.case)) and set(args.case)<=selected.keys()
        selected={name:source for name,source in selected.items() if name in args.case}
    assert not args.output.exists(),args.output
    try:
        run(selected,checks,PREFIX,args.output,
            extra_inputs=[*sorted((ROOT/'tests/semantics').glob('undefined_comparison_reference_graph*.py')),
                          ROOT/'tests/semantics/undefined_comparison_object_reference_array_review_protocol.py'])
    finally:
        path=args.output/'report.json'
        if path.exists():
            report=json.loads(path.read_text())
            for record in report['records']:
                if record['id'].endswith('-budget'):
                    record['main_premises']=record['premises']
                    record['scoped_setup_premises']=len(budget_setup(
                        record['id'].startswith('reference-graph-captured-shared-branches-')))
                    record['premises']+=record['scoped_setup_premises']
            path.write_text(json.dumps(report,indent=2)+'\n')

#!/usr/bin/env python3
"""Source/native comparisons for acyclic array graphs with descendant ALIAS cells."""
from pathlib import Path

import global_constant_sources as family
from undefined_comparison_reference_graph_cases import CASES

family.CASES = CASES
family.UNSUPPORTED = {
    'reference-graph-two-cell-cycle-resume-boundary': ('spaceship warning changed opposing scalar', b'B|H|'),
    'reference-graph-internal-payload-resume-boundary': ('spaceship warning changed opposing scalar', b'B|H|'),
}
family.BASELINE = ('error-handler ingress requires a producer continuation', b'')
family.MODEL_TIMEOUTS = {name: 90 for name in (
    'reference-graph-captured-shared-branches', 'reference-graph-live-held-payload',
    'reference-graph-empty-descendant-le-ge', 'reference-graph-captured-ge-throw')}
base_fingerprint = family.fingerprint


def fingerprint():
    return dict(base_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__),
        'tests/semantics/undefined_comparison_reference_graph_cases.py':
            family.sha(family.ROOT / 'tests/semantics/undefined_comparison_reference_graph_cases.py')})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()

#!/usr/bin/env python3
"""Source/native comparisons for recursive DIRECT array DAGs."""
from pathlib import Path

import global_constant_sources as family
from undefined_comparison_direct_array_graph_cases import CASES

family.CASES = CASES
family.UNSUPPORTED = {
    'direct-graph-child-alias-ingress-boundary': ('error-handler ingress requires a producer continuation', b'B|'),
    'direct-graph-flat-alias-resume-boundary': ('spaceship warning changed opposing scalar', b'B|H|'),
}
family.BASELINE = ('error-handler ingress requires a producer continuation', b'')
family.MODEL_TIMEOUTS = {
    'direct-graph-captured-depth-four': 90,
    'direct-graph-live-root-alias': 90,
    'direct-graph-empty-dag-predicates': 90,
    'direct-graph-captured-greater-throw': 90,
}
base_fingerprint = family.fingerprint


def fingerprint():
    return dict(base_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__),
        'tests/semantics/undefined_comparison_direct_array_graph_cases.py':
            family.sha(family.ROOT / 'tests/semantics/undefined_comparison_direct_array_graph_cases.py')})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()

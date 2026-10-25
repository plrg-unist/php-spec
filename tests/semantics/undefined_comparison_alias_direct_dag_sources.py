#!/usr/bin/env python3
"""Source/native comparisons for ALIAS-held recursive DIRECT DAGs."""
from pathlib import Path

import global_constant_sources as family
from undefined_comparison_alias_direct_dag_cases import CASES

family.CASES = CASES
family.UNSUPPORTED = {
    'alias-dag-child-reference-ingress-boundary': ('error-handler ingress requires a producer continuation', b'B|'),
    'alias-dag-internal-child-resume-boundary': ('spaceship warning changed opposing scalar', b'B|H|'),
}
family.BASELINE = ('error-handler ingress requires a producer continuation', b'')
family.MODEL_TIMEOUTS = {
    'alias-dag-captured-singleton': 90,
    'alias-dag-live-held-snapshot': 90,
    'alias-dag-empty-child-predicates': 90,
    'alias-dag-captured-greater-throw': 90,
}
base_fingerprint = family.fingerprint


def fingerprint():
    return dict(base_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__),
        'tests/semantics/undefined_comparison_alias_direct_dag_cases.py':
            family.sha(family.ROOT / 'tests/semantics/undefined_comparison_alias_direct_dag_cases.py')})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()

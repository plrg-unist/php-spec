#!/usr/bin/env python3
"""Differential sources for mixed declared-layout reinserted-key clones."""
from pathlib import Path
import json
import sys

import global_constant_sources as family
from throwable_mixed_reinsert_clone_cases import CASES, EXPECTED

family.CASES = CASES
family.UNSUPPORTED = {}
family.BASELINE = ('cached ordinary property-table cloning', b'B|2:2:7|')
family.MODEL_TIMEOUTS = {name: 240 for name in CASES}
base_fingerprint = family.fingerprint


def fingerprint():
    return dict(base_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__),
        'tests/semantics/throwable_mixed_reinsert_clone_cases.py':
            family.sha(family.ROOT / 'tests/semantics/throwable_mixed_reinsert_clone_cases.py')})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
    if sys.argv[sys.argv.index('--phase') + 1] == 'native':
        out = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
        report = json.loads((out / 'native-report.json').read_bytes())
        for row in report['records']:
            assert row['process']['exit'] == 0
            assert row['stdout'] == family.b64(EXPECTED[row['id']])
            assert row['stderr'] == family.b64(b'')

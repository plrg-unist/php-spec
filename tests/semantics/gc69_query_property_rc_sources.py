#!/usr/bin/env python3
"""Unmatched Parent RC protects its actual ordinary property graph."""
from pathlib import Path
import global_constant_sources as family
ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc69_query_property_rc.php'
family.CASES = {'owning-property-graph': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'owning-property-graph': 360}
family.BASELINE = ('is_callable output rebound to owning value or new type source', b'B|O|')
original_fingerprint = family.fingerprint
def fingerprint():
    return dict(original_fingerprint(), **{str(path.relative_to(ROOT)):family.sha(path) for path in [SOURCE,Path(__file__)]})
family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()

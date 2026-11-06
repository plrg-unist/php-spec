#!/usr/bin/env python3
"""Residual Parent RC retains shared Child fields through GC and shutdown."""
from pathlib import Path
import global_constant_sources as family
ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc69_peer_shared_property_rc.php'
family.CASES = {'shared-fields-child-before-parent': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'shared-fields-child-before-parent': 360}
original_fingerprint = family.fingerprint
def fingerprint():
    return dict(original_fingerprint(), **{str(path.relative_to(ROOT)):family.sha(path) for path in [SOURCE,Path(__file__)]})
family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()

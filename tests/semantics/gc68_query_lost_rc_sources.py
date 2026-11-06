#!/usr/bin/env python3
"""Raw query NAME overwrite retains unmatched native RC until shutdown."""
from pathlib import Path
import global_constant_sources as family
ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc68_query_lost_rc.php'
family.CASES = {'owning-name-overwrite': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'owning-name-overwrite': 360}
original_fingerprint = family.fingerprint
def fingerprint():
    return dict(original_fingerprint(), **{str(path.relative_to(ROOT)):family.sha(path) for path in [SOURCE,Path(__file__)]})
family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()

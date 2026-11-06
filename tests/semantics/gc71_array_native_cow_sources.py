#!/usr/bin/env python3
"""Raw NAME loss leaves native array RC that forces a real CV COW copy."""
from pathlib import Path
import global_constant_sources as family
ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc71_array_native_cow.php'
family.CASES = {'retained-array-native-cow': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'retained-array-native-cow': 360}
family.BASELINE = ('is_callable output rebound to owning value or new type source', b'B|O|')
original_fingerprint = family.fingerprint
def fingerprint():
    return dict(original_fingerprint(), **{str(path.relative_to(ROOT)):family.sha(path) for path in [SOURCE,Path(__file__)]})
family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()

#!/usr/bin/env python3
"""Independent request-string array publication and shared default consumer."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'request-string-array-copy': br'''<?php
$prefix = 'request';
define('ReviewCarrierSeed22', $prefix . '-text');
echo 'B|';
const ReviewCarrierArray22 = [ReviewCarrierSeed22];
$copy = ReviewCarrierArray22;
$copy[0] = 'changed';
echo ReviewCarrierArray22[0], '|', $copy[0], '|', ReviewCarrierSeed22;
''',
    'shared-default-string': br'''<?php
function readCarrierDefault22($value = 'default') { return $value; }
echo 'B|', readCarrierDefault22();
''',
}
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()

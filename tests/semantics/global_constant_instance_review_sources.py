#!/usr/bin/env python3
"""Independent shared-instance and property-reference query observation."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'aliased-instance-and-retained-property-reference': br'''<?php
class GlobalQueryReference24 { public $value = 4; }
const GlobalOriginalReference24 = new GlobalQueryReference24();
const GlobalAliasReference24 = GlobalOriginalReference24;
echo 'B|';
$first = constant(name: 'GlobalAliasReference24');
$reference =& $first->value;
unset($first);
$reference = 7;
$peer = constant('GlobalOriginalReference24');
echo $peer === GlobalAliasReference24 ? 'I' : 'D';
echo '|', $peer->value, '|', GlobalOriginalReference24->value;
unset($peer);
$again = constant('GlobalAliasReference24');
$again->value = 11;
echo '|', $reference, '|', $again === GlobalOriginalReference24 ? 'I' : 'D';
unset($again, $reference);
$last = constant('GlobalOriginalReference24');
echo '|', $last->value, '|', GlobalAliasReference24->value;
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

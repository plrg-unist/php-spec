#!/usr/bin/env python3
"""Independent caller bucket references versus stored constant object leaves."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'referenced-bucket-replacement-retains-constant-object': br'''<?php
class GlobalArrayRefItem26 { public int $value = 3; }
const GlobalReferencedArray26 = [NAN, [new GlobalArrayRefItem26(), []]];
echo 'B|';
$copy = constant(name: 'GlobalReferencedArray26');
$peer = constant('GlobalReferencedArray26');
echo $copy === $peer ? 'I' : 'D';
$original = $copy[1][0];
$slot =& $copy[1][0];
$original->value = 7;
echo '|', $slot === $original ? 'I' : 'D';
echo '|', $peer[1][0]->value, '|', GlobalReferencedArray26[1][0]->value;
$slot = new GlobalArrayRefItem26();
$slot->value = 11;
echo '|', $copy[1][0]->value, '|', $peer[1][0]->value, '|', GlobalReferencedArray26[1][0]->value;
$during = constant('GlobalReferencedArray26');
echo '|', $during === $peer ? 'I' : 'D';
echo '|', $during[1][0] === $original ? 'I' : 'D';
echo '|', $copy[1][0] === $original ? 'D' : 'R';
unset($slot, $copy, $peer, $during);
$again = constant('GlobalReferencedArray26');
echo '|', $again[1][0] === $original ? 'I' : 'D', '|', $again[1][0]->value;
unset($original, $again);
$last = constant('GlobalReferencedArray26');
echo '|', $last[1][0]->value, '|', $last === GlobalReferencedArray26 ? 'I' : 'D';
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

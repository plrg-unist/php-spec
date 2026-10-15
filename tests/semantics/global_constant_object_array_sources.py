#!/usr/bin/env python3
"""Native-first queries of arrays with already-certified object leaves."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'instance-leaf-and-nested-cow': br'''<?php
class GlobalArrayItem26 { public int $value = 3; }
const GlobalInstanceArray26 = [NAN, [new GlobalArrayItem26(), []]];
echo 'B|';
$first = constant(name: 'GlobalInstanceArray26');
$peer = constant('GlobalInstanceArray26');
echo $first === $peer ? 'I' : 'D';
$item = $first[1][0];
$item->value = 9;
$first[1][] = 'tail';
echo '|', $peer[1][0]->value, '|', GlobalInstanceArray26[1][0]->value, '|', $first[1][2];
echo '|', isset($peer[1][2]) ? 'D' : 'P', '|', isset(GlobalInstanceArray26[1][2]) ? 'D' : 'C';
$during = constant('GlobalInstanceArray26');
echo '|', $during === $peer ? 'I' : 'D';
unset($item, $first, $peer, $during);
$again = constant('GlobalInstanceArray26');
echo '|', $again[1][0]->value, '|', isset($again[1][2]) ? 'D' : 'A';
echo '|', $again === GlobalInstanceArray26 ? 'I' : 'D';
''',
    'closure-leaf-static-sharing-and-cow': br'''<?php
const GlobalClosureArray26 = [NAN, [static function () {
    static $counter = 0;
    return ++$counter;
}]];
echo 'B|';
$call = 'constant';
$first = $call(name: 'GlobalClosureArray26');
$peer = constant('GlobalClosureArray26');
echo $first === $peer ? 'I' : 'D';
$f = $first[1][0];
$g = $peer[1][0];
$first[1][] = 'tail';
$during = constant('GlobalClosureArray26');
echo '|', $during === $peer ? 'I' : 'D';
echo '|', $f(), '|', $g(), '|', $first[1][1];
unset($f, $g, $first, $peer, $during);
$again = constant('GlobalClosureArray26');
$h = $again[1][0];
$direct = GlobalClosureArray26[1][0];
echo '|', $h(), '|', $direct(), '|', $h === $direct ? 'I' : 'D';
echo '|', isset($again[1][1]) ? 'D' : 'A', '|', $again === GlobalClosureArray26 ? 'I' : 'D';
''',
}
family.BASELINE = ('global constant value query', b'B|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()

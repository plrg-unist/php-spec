#!/usr/bin/env python3
"""Independent inherited static-method callable query observation."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'inherited-method-callable-scope-and-identity': br'''<?php
class GlobalMethodBase25 {
    public static function scope() { return __CLASS__ . ':' . static::class; }
}
class GlobalMethodChild25 extends GlobalMethodBase25 {}
const GlobalMethodClosure25 = GlobalMethodChild25::scope(...);
echo 'B|';
$first = constant(name: 'GlobalMethodClosure25');
$peer = GlobalMethodClosure25;
echo $first === $peer ? 'I' : 'D';
echo '|', $first();
unset($first, $peer);
$again = constant('GlobalMethodClosure25');
echo '|', $again(), '|', $again === GlobalMethodClosure25 ? 'I' : 'D';
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

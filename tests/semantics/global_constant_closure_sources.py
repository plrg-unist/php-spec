#!/usr/bin/env python3
"""Native-first queries of already-published certified Closures."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'closure-identity-and-shared-statics': br'''<?php
const GlobalClosure25 = static function () {
    static $counter = 0;
    return ++$counter;
};
echo 'B|';
$first = constant(name: 'GlobalClosure25');
$peer = constant('GlobalClosure25');
$direct = GlobalClosure25;
echo $first === $peer && $first === $direct ? 'I' : 'D';
echo '|', $first(), '|', $peer(), '|', $direct();
unset($first, $peer, $direct);
$again = constant('GlobalClosure25');
echo '|', $again(), '|', $again === GlobalClosure25 ? 'I' : 'D';
''',
    'function-callable-alias-and-named-dynamic-query': br'''<?php
function globalQueryTarget25() { return 'fcc'; }
const GlobalFunction25 = globalQueryTarget25(...);
const GlobalAlias25 = GlobalFunction25;
echo 'B|';
$call = 'constant';
$name = 'GlobalAlias25';
$first = $call(name: $name);
$peer = constant('GlobalFunction25');
echo $first === $peer && $first === GlobalAlias25 ? 'I' : 'D';
echo '|', $first(), '|', $peer();
unset($first, $peer);
$again = constant('GlobalAlias25');
echo '|', $again(), '|', $again === GlobalFunction25 ? 'I' : 'D';
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

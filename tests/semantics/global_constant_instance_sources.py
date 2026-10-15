#!/usr/bin/env python3
"""Native-first queries of already-published certified user instances."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'plain-instance-identity-and-mutation': br'''<?php
class GlobalQueryPlain24 { public int $value = 3; }
const GlobalPlain24 = new GlobalQueryPlain24();
echo 'B|';
$first = constant(name: 'GlobalPlain24');
$peer = constant('GlobalPlain24');
echo $first === $peer ? 'I' : 'D';
$first->value = 9;
echo '|', $peer->value, '|', GlobalPlain24->value;
unset($first, $peer);
$again = constant('GlobalPlain24');
echo '|', $again->value, '|', $again === GlobalPlain24 ? 'I' : 'D';
''',
    'completed-constructor-and-named-dynamic-query': br'''<?php
class GlobalQueryBuilt24 {
    public int $value = 0;
    public function __construct() { echo 'C|'; $this->value = 5; }
}
const GlobalBuilt24 = new GlobalQueryBuilt24();
echo 'B|';
$call = 'constant';
$name = 'GlobalBuilt24';
$first = $call(name: $name);
$peer = GlobalBuilt24;
echo $first === $peer ? 'I' : 'D';
$first->value = 12;
unset($first, $peer);
$again = constant('GlobalBuilt24');
echo '|', $again->value, '|', GlobalBuilt24->value;
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

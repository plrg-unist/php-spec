#!/usr/bin/env python3
"""Native-first global array constant queries and ordinary copy-on-write."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'literal-tree-sharing': br'''<?php
const GlobalTree23 = ['n' => NAN, 'child' => [1], 'empty' => []];
echo 'B|';
$first = constant(name: 'GlobalTree23');
$peer = constant('GlobalTree23');
echo $first === $peer ? 'I' : 'D';
$first['child'][0] = 9;
$first['empty'][] = 4;
$first['n'] = 0;
$again = constant('GlobalTree23');
echo '|', $first['child'][0], '|', $peer['child'][0], '|', $again['child'][0];
echo '|', $first['empty'][0], '|', $again['empty'] === [] ? 'E' : 'BAD';
echo '|', $peer === $again ? 'I' : 'D';
''',
    'defined-request-tree': br'''<?php
$seed = 'request';
$source = ['n' => NAN, 'child' => [$seed . '-value']];
define('DefinedTree23', $source);
$source['child'][0] = 'source';
echo 'B|';
$call = 'constant';
$name = 'DefinedTree23';
$first = $call(name: $name);
$peer = constant('DefinedTree23');
echo $first === $peer ? 'I' : 'D';
$first['child'][0] = 'changed';
$first['child'][] = 'tail';
$again = constant('DefinedTree23');
echo '|', $first['child'][0], '|', $first['child'][1];
echo '|', $peer['child'][0], '|', $again['child'][0], '|', $source['child'][0];
''',
    'immutable-and-mutable-empty-roots': br'''<?php
const FixedEmpty23 = [];
$source = [7];
unset($source[0]);
define('MutableEmpty23', $source);
echo 'B|';
$fixed = constant('FixedEmpty23');
$mutable = constant('MutableEmpty23');
$fixed[] = 1;
$mutable[] = 2;
$again = constant('MutableEmpty23');
echo $fixed[0], '|', $mutable[0], '|', $again === [] ? 'E' : 'BAD';
echo '|', FixedEmpty23 === [] ? 'E' : 'BAD';
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

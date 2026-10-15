#!/usr/bin/env python3
"""Native-first nested zero-argument stdClass constant-AST births."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'nested-distinct-births-cow': br'''<?php
echo 'B|';
const V61_TREE = [NAN, [new stdClass(), new stdClass(), []]];
$first = constant('V61_TREE');
$peer = V61_TREE;
$left = $first[1][0];
$right = $first[1][1];
$left->value = 17;
$right->value = 23;
echo $left !== $right ? 'D' : 'BAD', '|', $left->value, '|', $right->value;
$left->value = 31;
$right->value = 37;
$first[1][] = 'tail';
echo '|', $peer[1][0]->value, '|', $peer[1][1]->value, '|', $first[1][3], '|', isset($peer[1][3]) ? 'BAD' : 'kept';
$during = constant('V61_TREE');
echo '|', $during === $peer ? 'I' : 'BAD';
unset($left, $right, $first, $peer, $during);
$again = constant('V61_TREE');
$a = $again[1][0];
$b = $again[1][1];
echo '|', $a !== $b ? 'D' : 'BAD', '|', $a->value, '|', $b->value, '|A|';
''',
    'eval-duplicate-nested-births': br'''<?php
echo 'B|';
function v61notice($level, $message, $file, $line) {
    $held = constant('V61_EVAL');
    $leaf = $held[1][0];
    $leaf->value = 41;
    echo 'H:', $level, '|';
    return true;
}
$code = 'const V61_EVAL = [NAN, [new stdClass(), new stdClass(), []]];';
eval($code);
$old = constant('V61_EVAL');
$left = $old[1][0];
$right = $old[1][1];
$left->value = 17;
$right->value = 23;
set_error_handler('v61notice');
eval($code);
restore_error_handler();
$kept = constant('V61_EVAL');
echo $kept === $old ? 'I' : 'BAD', '|', $left !== $right ? 'D' : 'BAD', '|', $left->value, '|', $right->value, '|A|';
''',
}
family.BASELINE = ('global constant internal or Throwable initializer', b'B|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()

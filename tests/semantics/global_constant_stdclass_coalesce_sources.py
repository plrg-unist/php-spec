#!/usr/bin/env python3
"""Native-first newborn stdClass leaves selected through null coalescing."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'nonnull-and-nested-null-fallback': br'''<?php
echo 'B|';
const V62_NULL = null;
const V62_TREE = [NAN, [
    (new stdClass()) ?? new stdClass(),
    V62_NULL ?? (V62_NULL ?? new stdClass()),
    []
]];
$copy = constant('V62_TREE');
$peer = V62_TREE;
$left = $copy[1][0];
$right = $copy[1][1];
$left->value = 17;
$right->value = 23;
echo $left !== $right ? 'D' : 'BAD', '|', $left->value, '|', $right->value;
$left->value = 31;
$right->value = 37;
$copy[1][] = 'tail';
echo '|', $peer[1][0]->value, '|', $peer[1][1]->value, '|', $copy[1][3], '|', isset($peer[1][3]) ? 'BAD' : 'kept';
$during = constant('V62_TREE');
echo '|', $during === $peer ? 'I' : 'BAD';
unset($left, $right, $copy, $peer, $during);
$again = constant('V62_TREE');
$a = $again[1][0];
$b = $again[1][1];
echo '|', $a !== $b ? 'D' : 'BAD', '|', $a->value, '|', $b->value, '|A|';
''',
    'eval-nested-coalescing-selected-query': br'''<?php
echo 'B|';
$code = 'const V62_EVAL_NULL = null; const V62_EVAL_TREE = [NAN, [(V62_EVAL_NULL ?? new stdClass()) ?? new stdClass(), V62_EVAL_NULL ?? new stdClass(), []]];';
eval($code);
$query = 'constant';
$copy = $query(name: 'V62_EVAL_TREE');
$peer = $query(name: 'V62_EVAL_TREE');
$left = $copy[1][0];
$right = $copy[1][1];
$left->value = 17;
$right->value = 23;
echo $left !== $right ? 'D' : 'BAD', '|', $left->value, '|', $right->value;
$left->value = 31;
$right->value = 37;
$copy[1][] = 'tail';
echo '|', $peer[1][0]->value, '|', $peer[1][1]->value, '|', $copy[1][3], '|', isset($peer[1][3]) ? 'BAD' : 'kept';
$during = $query(name: 'V62_EVAL_TREE');
echo '|', $during === $peer ? 'I' : 'BAD';
unset($left, $right, $copy, $peer, $during);
$again = $query(name: 'V62_EVAL_TREE');
$a = $again[1][0];
$b = $again[1][1];
echo '|', $a !== $b ? 'D' : 'BAD', '|', $a->value, '|', $b->value, '|A|';
''',
}
family.BASELINE = ('global constant object transfer', b'B|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()

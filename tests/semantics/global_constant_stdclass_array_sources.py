#!/usr/bin/env python3
"""Native-first certified stdClass aliases in global constant array trees."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'literal-alias-nested-cow': br'''<?php
echo 'B|';
const V60_LEAF = new stdClass();
const V60_TREE = [NAN, [V60_LEAF, []]];
$leaf = V60_LEAF;
$leaf->value = 17;
$first = constant(name: 'V60_TREE');
$peer = V60_TREE;
echo $first === $peer ? 'I' : 'BAD';
$item = $first[1][0];
echo '|', $item === $leaf ? 'same' : 'BAD', '|', $item->value;
$item->value = 31;
$first[1][] = 'tail';
echo '|', $peer[1][0]->value, '|', $first[1][2], '|', isset($peer[1][2]) ? 'BAD' : 'kept';
$during = constant('V60_TREE');
echo '|', $during === $peer ? 'I' : 'BAD';
unset($item, $first, $peer, $during);
$again = constant('V60_TREE');
$held = $again[1][0];
echo '|', $held === $leaf ? 'same' : 'BAD', '|', $held->value, '|', isset($again[1][2]) ? 'BAD' : 'kept', '|A|';
''',
    'eval-alias-selected-query': br'''<?php
echo 'B|';
eval('const V60_EVAL_LEAF = new stdClass(); const V60_EVAL_TREE = [NAN, [V60_EVAL_LEAF, []]];');
$leaf = V60_EVAL_LEAF;
$leaf->value = 23;
$lookup = 'constant';
$first = $lookup(name: 'V60_EVAL_TREE');
$item = $first[1][0];
echo $item === $leaf ? 'same' : 'BAD', '|', $item->value;
$item->value = 37;
$first[1][] = 'tail';
$peer = $lookup('V60_EVAL_TREE');
echo '|', $peer[1][0]->value, '|', isset($peer[1][2]) ? 'BAD' : 'kept';
unset($item, $first, $peer);
$again = $lookup('V60_EVAL_TREE');
$held = $again[1][0];
echo '|', $held === $leaf ? 'same' : 'BAD', '|', $held->value, '|A|';
''',
}
family.BASELINE = ('invalid declaration publication history', b'B|')
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()

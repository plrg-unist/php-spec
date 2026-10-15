#!/usr/bin/env python3
"""Independent whole-array donation and real copied stdClass bucket references."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'donated-array-bucket-reference-replacement': br'''<?php
echo 'B|';
const V60_REVIEW_LEAF = new stdClass();
const V60_REVIEW_TREE = [NAN, [V60_REVIEW_LEAF, []]];
const V60_REVIEW_ALIAS = V60_REVIEW_TREE;
$leaf = V60_REVIEW_LEAF;
$leaf->value = 3;
$copy = constant(name: 'V60_REVIEW_ALIAS');
$peer = constant('V60_REVIEW_TREE');
echo $copy === $peer ? 'I' : 'BAD';
$receipt = $copy[1][0];
$slot =& $copy[1][0];
$receipt->value = 7;
echo '|', $slot === $receipt ? 'same' : 'BAD';
echo '|', $peer[1][0]->value, '|', V60_REVIEW_TREE[1][0]->value, '|', $leaf->value;
$slot = 41;
echo '|', $copy[1][0], '|', $peer[1][0]->value, '|', V60_REVIEW_TREE[1][0]->value, '|', $leaf->value;
$during = constant('V60_REVIEW_ALIAS');
echo '|', $during === $peer ? 'I' : 'BAD';
echo '|', $during[1][0] === $receipt ? 'same' : 'BAD';
echo '|', $copy[1][0] === $receipt ? 'BAD' : 'replaced';
unset($slot, $copy, $peer, $during);
$again = constant('V60_REVIEW_ALIAS');
echo '|', $again[1][0] === $receipt ? 'same' : 'BAD', '|', $again[1][0]->value;
unset($receipt, $again, $leaf);
$last = constant('V60_REVIEW_TREE');
echo '|', $last[1][0]->value, '|', $last === V60_REVIEW_TREE ? 'I' : 'BAD', '|A|';
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

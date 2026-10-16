#!/usr/bin/env python3
"""Independent repeated object edges, reference snapshots and queried array COW."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-reference-snapshot-and-bucket-cow': br'''<?php
const V66_REVIEW_LEFT = new stdClass();
const V66_REVIEW_RIGHT = new stdClass();
$left = V66_REVIEW_LEFT;
$right = V66_REVIEW_RIGHT;
$left->value = 7;
$right->value = 19;
unset($left, $right);
$cell = V66_REVIEW_LEFT;
$input = ['head' => &$cell, 'nested' => ['again' => &$cell]];
$api = 'define';
echo 'B|';
echo $api(value: $input, constant_name: 'V66_REVIEW_TREE') ? 'T|' : 'BAD|';
$cell = V66_REVIEW_RIGHT;
$tree = constant('V66_REVIEW_TREE');
echo $tree['head'] === V66_REVIEW_LEFT && $tree['nested']['again'] === V66_REVIEW_LEFT ? 'L|' : 'BAD|';
echo $input['head'] === V66_REVIEW_RIGHT && $input['nested']['again'] === V66_REVIEW_RIGHT ? 'R|' : 'BAD|';
$leaf = $tree['nested']['again'];
$leaf->value = 31;
unset($leaf);
$bucket =& $tree['nested']['again'];
$bucket = V66_REVIEW_RIGHT;
unset($bucket);
$tree['nested'][] = 'tail';
$again = constant('V66_REVIEW_TREE');
echo $again['nested']['again'] === V66_REVIEW_LEFT ? 'L|' : 'BAD|';
echo $tree['nested']['again'] === V66_REVIEW_RIGHT ? 'R|' : 'BAD|';
echo V66_REVIEW_LEFT->value, '|', V66_REVIEW_RIGHT->value, '|';
echo $tree['nested'][0], '|', isset($again['nested'][0]) ? 'BAD|' : 'kept|';
unset($tree, $again, $input, $cell, $api);
echo 'A|';
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

#!/usr/bin/env python3
"""Independent selected stdClass births after true and false constant facts."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-branches-after-prior-facts': br'''<?php
echo 'B|';
const V61_REVIEW_TRUE = true;
const V61_REVIEW_FALSE = false;
const V61_REVIEW_TREE = [NAN, [
    V61_REVIEW_TRUE ? new stdClass() : new stdClass(),
    V61_REVIEW_FALSE ? new stdClass() : new stdClass(),
    []
]];
$copy = constant('V61_REVIEW_TREE');
$left = $copy[1][0];
$right = $copy[1][1];
$left->value = 17;
$right->value = 23;
echo $left !== $right ? 'distinct' : 'BAD', '|', $left->value, ':', $right->value;
$left->value = 31;
$right->value = 37;
$copy[1][] = 'tail';
$again = constant('V61_REVIEW_TREE');
echo '|', $again[1][0]->value, ':', $again[1][1]->value;
echo '|', $copy[1][3], '|', isset($again[1][3]) ? 'BAD' : 'kept';
echo '|', $again[1][0] === $left ? 'same' : 'BAD', ':', $again[1][1] === $right ? 'same' : 'BAD';
unset($left, $right, $copy, $again);
$last = constant('V61_REVIEW_TREE');
echo '|', $last[1][0]->value, ':', $last[1][1]->value, '|A|';
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

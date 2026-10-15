#!/usr/bin/env python3
"""Independent named stdClass argument value release and duplicate cutoff."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'named-value-destructors-and-duplicate-cutoff': br'''<?php
class V63ReviewFirst {
    public function __destruct() { echo 'first|'; }
}
class V63ReviewSecond {
    public function __destruct() { echo 'second|'; }
}
echo 'B|';
const V63_REVIEW_GOOD = new stdClass(first: new V63ReviewFirst(), spare: new V63ReviewSecond());
echo 'ready|';
$good = constant('V63_REVIEW_GOOD');
$good->value = 41;
echo V63_REVIEW_GOOD->value, '|';
try {
    eval('const V63_REVIEW_BAD = new stdClass(keep: new V63ReviewFirst(), keep: new V63ReviewSecond(), late: new V63ReviewFirst());');
} catch (Error $e) {
    echo $e->getMessage(), '|';
}
echo defined('V63_REVIEW_BAD') ? 'BAD|' : 'absent|';
$again = constant('V63_REVIEW_GOOD');
echo $again === $good ? 'same|' : 'BAD|';
unset($good, $again, $e);
$last = constant('V63_REVIEW_GOOD');
echo $last->value, '|A|';
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

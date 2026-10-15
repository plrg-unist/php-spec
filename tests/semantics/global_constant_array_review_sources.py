#!/usr/bin/env python3
"""Independent global array query reference and append-history check."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'empty-child-reference-and-append-history': br'''<?php
const ReviewArray23 = ['empty' => [], 'nested' => [10]];
echo 'B|';
$view = constant('ReviewArray23');
$peer = constant(name: 'ReviewArray23');
$empty =& $view['empty'];
$empty[] = 7;
unset($view['nested'][0]);
$view['nested'][] = 9;
echo $view['empty'][0], '|', isset($peer['empty'][0]) ? 'BAD' : 'E';
echo '|', $view['nested'][1], '|', $peer['nested'][0], '|', ReviewArray23['nested'][0];
unset($empty, $view);
$again = constant('ReviewArray23');
echo '|', isset($again['empty'][0]) ? 'BAD' : 'E', '|', $again['nested'][0], '|A|';
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

#!/usr/bin/env python3
"""Native-first CONFIG argument streaming from real source Generators."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'fixed-config-generator-drains-before-api': br'''<?php
function configGenerator90() {
    echo 'Y0|'; yield -11 => 'precision';
    echo 'Y1|'; yield 7 => '8';
    echo 'F|';
}
$it = configGenerator90(); $result = 99; echo 'B|';
$result = ini_set(...$it);
echo 'A|', $result, '|', ini_get('precision'), '|E';
''',
    'retained-config-generator-preserves-selection-and-historical-input': br'''<?php
function configOwnedGenerator90() {
    global $it, $call;
    echo 'Y0|'; $it = 17; $call = ini_get(...);
    yield 3 => 'precision';
    echo 'Y1|'; ini_set('precision', '6'); yield 3 => '11';
    echo 'F|'; ini_set('precision', '7');
}
$it = configOwnedGenerator90(); $hold = $it;
$call = ini_set(...); $keep = $call; $result = 99; echo 'B|';
$result = $call(...$it);
echo 'A|', $result, '|', ini_get('precision'), '|', $call('precision'), '|', $it;
echo '|R|', $keep('precision', '9'), '|', ini_get('precision');
''',
}
family.UNSUPPORTED = {}
family.BASELINE = ('CONFIG Traversable unpack outside initialized Iterator domain', b'B|')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()

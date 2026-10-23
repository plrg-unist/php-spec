#!/usr/bin/env python3
"""WeakMap's object key rejects a retained CONFIG call before copying current."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'retained-config-weakmap-key-error-precedes-owning-current-and-api': br'''<?php
class ConfigWeakMapReview88 {}
$map = new WeakMap; $mapHold = $map;
$key = new stdClass; $keyHold = $key;
$current = new ConfigWeakMapReview88;
$map[$key] = $current; unset($current);
$call = ini_set(...); $keep = $call;
$result = 99; echo 'B|';
try {
    $result = $call->__invoke(
        ...$map
    );
    echo 'BAD';
} catch (Error $e) {
    echo $e instanceof TypeError ? 'BAD' : 'E';
    echo '|', $e->getMessage(), '|', $e->getLine(), '|';
    echo $e->getTrace() === [] ? 'T' : 'BAD';
    echo '|', $result, '|', ini_get('precision'), '|';
    echo $map[$key] instanceof ConfigWeakMapReview88 ? 'V' : 'BAD';
} finally { echo '|Z'; }
echo '|R|', $keep('precision', '9'), '|', ini_get('precision'), '|', $result;
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

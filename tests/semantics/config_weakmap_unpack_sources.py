#!/usr/bin/env python3
"""Native-first CONFIG argument unpacking from borrowed WeakMaps."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'empty-weakmap-reaches-config-arity-after-traversal': br'''<?php
$map = new WeakMap; $hold = $map; $result = 99; echo 'B|';
try {
    $result = ini_set(
        ...$map
    );
    echo 'BAD';
} catch (ArgumentCountError $e) {
    $trace = $e->getTrace();
    echo 'A|', $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'], '|';
    echo $trace[0]['args'] === [] ? 'Z' : 'BAD';
    echo '|', $result, '|', ini_get('precision');
}
echo '|R|', ini_set('precision', '9'), '|', ini_get('precision');
''',
    'occupied-weakmap-rejects-object-key-before-any-config-send': br'''<?php
$map = new WeakMap; $hold = $map; $key = new stdClass; $keyhold = $key;
$map[$key] = 'precision'; $result = 99; echo 'B|';
try {
    $result = ini_set(
        ...$map
    );
    echo 'BAD';
} catch (Error $e) {
    echo $e instanceof TypeError ? 'T|' : 'E|';
    echo $e->getMessage(), '|', $e->getLine(), '|';
    echo $e->getTrace() === [] ? 'Z' : 'BAD';
    echo '|', $result, '|', ini_get('precision');
}
echo '|V|', $map[$key], '|R|', ini_set('precision', '9'), '|', ini_get('precision');
''',
    'retained-empty-weakmap-arity-preserves-wrapper-and-setter': br'''<?php
$map = new WeakMap; $hold = $map;
$call = ini_set(...); $keep = $call; $result = 99; echo 'B|';
try {
    $result = $call->__invoke(
        ...$map
    );
    echo 'BAD';
} catch (ArgumentCountError $e) {
    $trace = $e->getTrace();
    echo 'A|', $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'], '|';
    echo $trace[0]['args'] === [] ? 'Z' : 'BAD';
    if (isset($trace[1])) {
        echo '|W|', $trace[1]['function'], '|';
        echo $trace[1]['args'] === [] ? 'Z' : 'BAD';
    } else { echo '|N'; }
    echo '|', $result, '|', ini_get('precision');
}
echo '|R|', $keep('precision', '9'), '|', ini_get('precision');
''',
}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()

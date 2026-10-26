#!/usr/bin/env python3
"""A terminal throw retires CONFIG's sole Generator DATA owner."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'sole-data-config-generator-terminal-throw-retires-before-catch': br'''<?php
function configGeneratorSoleThrowReview92() {
    global $generator, $call, $saved, $effects;
    echo 'Y0|'; ++$effects; $generator = 17;
    yield 3 => 'precision';
    echo 'Y1|'; ++$effects; $call = ini_get(...); ini_set('precision', '6');
    yield 3 => '11';
    echo 'T|'; ++$effects; throw $saved;
}
$generator = configGeneratorSoleThrowReview92();
$watch = WeakReference::create($generator);
$call = ini_set(...); $keep = $call;
$saved = new Exception('config-generator-sole-data92'); $effects = 0;
$result = 99; echo 'B|';
try {
    $result = $call->__invoke(
        ...$generator
    );
    echo 'BAD';
} catch (Exception $e) {
    echo $e === $saved ? 'I' : 'BAD';
    echo '|', $result, '|', $effects, '|', ini_get('precision'), '|', $generator;
    echo $e->getTrace() === [] ? '|F' : '|BAD';
    echo $watch->get() === null ? '|D' : '|BAD';
} finally { echo '|Z'; }
echo '|L|', $call('precision'), '|R|', $keep('precision', '9'), '|', ini_get('precision'), '|', $result;
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

#!/usr/bin/env python3
"""A terminal Generator throw cancels CONFIG after both positional sends."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'retained-config-generator-terminal-throw-cancels-api': br'''<?php
function configGeneratorThrowReview90() {
    global $call, $saved, $effects;
    echo 'Y0|'; ++$effects; yield 3 => 'precision';
    echo 'Y1|'; ++$effects; $call = ini_get(...); ini_set('precision', '6');
    yield 3 => '11';
    echo 'T|'; ++$effects;
    $saved = new Exception('config-generator-after-sends90'); throw $saved;
}
$generator = configGeneratorThrowReview90(); $generatorHold = $generator;
$call = ini_set(...); $keep = $call; $saved = null; $effects = 0;
$result = 99; echo 'B|';
try {
    $result = $call->__invoke(
        ...$generator
    );
    echo 'BAD';
} catch (Exception $e) {
    $trace = $e->getTrace();
    echo $e === $saved ? 'I' : 'BAD';
    echo '|', $result, '|', $effects, '|', ini_get('precision');
    echo '|', $trace[0]['function'], '|', $trace[0]['line'], '|';
    echo $trace[0]['args'] === [] ? 'A' : 'BAD';
    echo isset($trace[1]) ? '|BAD' : '|F';
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

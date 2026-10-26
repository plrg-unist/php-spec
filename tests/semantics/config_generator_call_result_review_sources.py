#!/usr/bin/env python3
"""A real factory result stays owned through terminal Generator throw cleanup."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'factory-generator-call-result-terminal-throw-releases-input': br'''<?php
function configGeneratorFactoryReview94() {
    global $watch, $saved, $call, $effects;
    echo 'P|'; ++$effects;
    $generator = configGeneratorBodyReview94();
    $watch = WeakReference::create($generator);
    $saved = new Exception('config-generator-call-result94');
    $call = ini_get(...); ini_set('precision', '6');
    return $generator;
}
function configGeneratorBodyReview94() {
    global $watch, $saved, $effects;
    echo 'Y0|'; ++$effects;
    echo $watch->get() !== null ? 'H|' : 'BAD|';
    yield 3 => 'precision';
    echo 'Y1|'; ++$effects; ini_set('precision', '7'); yield 3 => '11';
    echo 'T|'; ++$effects; throw $saved;
}
$watch = null; $saved = null; $effects = 0;
$call = ini_set(...); $keep = $call; $result = 99; echo 'B|';
try {
    $result = $call->__invoke(
        ...configGeneratorFactoryReview94()
    );
    echo 'BAD';
} catch (Exception $e) {
    $trace = $e->getTrace();
    echo $e === $saved ? 'I' : 'BAD';
    echo '|', $result, '|', $effects, '|', ini_get('precision');
    echo '|', $trace[0]['function'], '|', $trace[0]['line'];
    echo $trace[0]['args'] === [] ? '|A' : '|BAD';
    echo isset($trace[1]) ? '|BAD' : '|F';
    echo $watch->get() === null ? '|D' : '|BAD';
}
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

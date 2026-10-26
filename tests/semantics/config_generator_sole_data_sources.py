#!/usr/bin/env python3
"""Native-first CONFIG Generator sole-DATA retirement and historical reception."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'sole-data-config-generator-retires-before-normal-api': br'''<?php
function configGeneratorSole92() {
    global $generator;
    echo 'Y0|'; $generator = 17; yield 3 => 'precision';
    echo 'Y1|'; yield 3 => '8';
    echo 'F|';
}
$generator = configGeneratorSole92();
$watch = WeakReference::create($generator); $result = 99; echo 'B|';
$result = ini_set(...$generator);
echo 'A|', $result, '|', ini_get('precision'), '|', $generator;
echo $watch->get() === null ? '|D' : '|BAD';
echo '|E';
''',
    'sole-data-config-generator-retires-before-owned-arity-error': br'''<?php
function configGeneratorSoleArity92() {
    global $generator, $call;
    echo 'Y0|'; $generator = 17; $call = ini_get(...);
    ini_set('precision', '6'); yield 3 => 'precision';
    echo 'F|'; ini_set('precision', '7');
}
$generator = configGeneratorSoleArity92();
$watch = WeakReference::create($generator);
$call = ini_set(...); $keep = $call; $result = 99; echo 'B|';
try {
    $result = $call->__invoke(
        ...$generator
    );
    echo 'BAD';
} catch (ArgumentCountError $e) {
    $trace = $e->getTrace();
    echo 'C|', $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'], '|', $trace[0]['args'][0];
    if (isset($trace[1])) { echo '|W|', $trace[1]['function'], '|', $trace[1]['args'][0]; }
    else { echo '|N'; }
    echo '|', $result, '|', ini_get('precision'), '|', $generator;
    echo $watch->get() === null ? '|D' : '|BAD';
}
echo '|L|', $call('precision'), '|R|', $keep('precision', '9'), '|', ini_get('precision'), '|', $result;
''',
}
family.UNSUPPORTED = {}
family.BASELINE = ('CONFIG Generator unpack last DATA or callee owner', b'B|Y0|Y1|F|')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()

#!/usr/bin/env python3
"""Native-first temporary Generator-call INPUT and DATA lifetimes in CONFIG."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'fixed-config-temporary-generator-call-drains-before-api': br'''<?php
function configGeneratorCall94() {
    echo 'Y0|'; yield 3 => 'precision';
    echo 'Y1|'; yield 3 => '8'; echo 'F|';
}
$result = 99; echo 'B|';
$result = ini_set(...configGeneratorCall94());
echo 'A|', $result, '|', ini_get('precision'), '|E';
''',
    'retained-config-factory-generator-input-retires-before-api': br'''<?php
function configGeneratorFactoryBody94() {
    global $watch;
    echo 'Y0|'; echo $watch->get() === null ? 'BAD|' : 'H|';
    yield 3 => 'precision';
    echo 'Y1|'; ini_set('precision', '7'); yield 3 => '11';
    echo 'F|'; ini_set('precision', '8');
}
function configGeneratorFactory94() {
    global $watch, $call;
    echo 'P|'; $call = ini_get(...); ini_set('precision', '6');
    $local = configGeneratorFactoryBody94();
    $watch = WeakReference::create($local); return $local;
}
$watch = null; $call = ini_set(...); $keep = $call; $result = 99; echo 'B|';
$result = $call->__invoke(
    ...configGeneratorFactory94()
);
echo 'A|', $result, '|', ini_get('precision');
echo $watch->get() === null ? '|D' : '|BAD';
echo '|L|', $call('precision'), '|R|', $keep('precision', '9'), '|', ini_get('precision');
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

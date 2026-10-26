#!/usr/bin/env python3
"""CLOSED Generator return storage retires before CONFIG API reception."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'config-generator-return-destructor-precedes-selected-api': br'''<?php
class ConfigGeneratorReturnPayload96 {
    public function __destruct() {
        global $watch, $call;
        echo 'D|'; echo $watch->get() !== null ? 'H|' : 'BAD|';
        ini_set('precision', '6'); $call = ini_get(...);
    }
}
function configGeneratorReturn96() {
    global $generator;
    echo 'Y0|'; yield 3 => 'precision';
    echo 'Y1|'; $generator = 17; yield 3 => '8';
    echo 'F|'; return new ConfigGeneratorReturnPayload96();
}
$generator = configGeneratorReturn96(); $watch = WeakReference::create($generator);
$call = ini_set(...); $keep = $call; $result = 99; echo 'B|';
$result = $call->__invoke(
    ...$generator
);
echo 'A|', $result, '|', ini_get('precision'), '|', $generator;
echo $watch->get() === null ? '|G' : '|BAD';
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

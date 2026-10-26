#!/usr/bin/env python3
"""Native-first CONFIG unpack through a real Aggregate-returned Generator."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'fixed-config-aggregate-produces-retained-generator': br'''<?php
function configProducedGenerator91() {
    echo 'Y0|'; yield -11 => 'precision';
    echo 'Y1|'; yield 7 => '8';
    echo 'F|';
}
class ConfigGeneratorProducer91 implements IteratorAggregate {
    public function getIterator(): Traversable { global $it; echo 'G|'; return $it; }
}
$it = configProducedGenerator91(); $iteratorHold = $it;
$aggregate = new ConfigGeneratorProducer91; $aggregateHold = $aggregate;
$result = 99; echo 'B|';
$result = ini_set(...$aggregate);
echo 'A|', $result, '|', ini_get('precision'), '|E';
''',
    'retained-config-aggregate-generator-preserves-two-histories': br'''<?php
function configOwnedProducedGenerator91() {
    global $it;
    echo 'Y0|'; $it = 17; yield 3 => 'precision';
    echo 'Y1|'; ini_set('precision', '7'); yield 3 => '11';
    echo 'F|'; ini_set('precision', '8');
}
class ConfigOwnedGeneratorProducer91 implements IteratorAggregate {
    public function getIterator(): Traversable {
        global $it, $aggregate, $call;
        echo 'G|'; $aggregate = 23; $call = ini_get(...);
        ini_set('precision', '6'); return $it;
    }
}
$it = configOwnedProducedGenerator91(); $iteratorHold = $it;
$aggregate = new ConfigOwnedGeneratorProducer91; $aggregateHold = $aggregate;
$call = ini_set(...); $keep = $call; $result = 99; echo 'B|';
$result = $call(...$aggregate);
echo 'A|', $result, '|', ini_get('precision'), '|', $call('precision'), '|', $it, '|', $aggregate;
echo '|R|', $keep('precision', '9'), '|', ini_get('precision');
''',
}
family.UNSUPPORTED = {}
family.BASELINE = ('CONFIG Aggregate return outside shared initialized Iterator domain', b'B|G|')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()

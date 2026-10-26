#!/usr/bin/env python3
"""Native-first CONFIG acquisition of generator-function getIterator methods."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'fixed-config-generator-method-retains-and-retires-receiver': br'''<?php
class ConfigGeneratorMethod93 implements IteratorAggregate {
    public function getIterator(): Traversable {
        global $aggregate;
        echo 'G|'; $aggregate = 17;
        echo $this instanceof ConfigGeneratorMethod93 ? 'R|' : 'BAD|';
        yield 3 => 'precision'; echo 'Y1|'; yield 3 => '8';
        echo 'F|';
    }
}
$aggregate = new ConfigGeneratorMethod93;
$watch = WeakReference::create($aggregate); $result = 99; echo 'B|';
$result = ini_set(...$aggregate);
echo 'A|', $result, '|', ini_get('precision'), '|', $aggregate;
echo $watch->get() === null ? '|D' : '|BAD'; echo '|E';
''',
    'retained-config-inherited-generator-method-preserves-callee': br'''<?php
class ConfigGeneratorMethodParent93 implements IteratorAggregate {
    public function getIterator(): Traversable {
        global $aggregate, $call;
        echo 'G|'; $aggregate = 23; $call = ini_get(...);
        echo $this instanceof ConfigGeneratorMethodChild93 ? 'R|' : 'BAD|';
        ini_set('precision', '6'); yield 3 => 'precision';
        echo 'Y1|'; yield 3 => '11';
        echo 'F|'; ini_set('precision', '7');
    }
}
class ConfigGeneratorMethodChild93 extends ConfigGeneratorMethodParent93 {}
$aggregate = new ConfigGeneratorMethodChild93;
$watch = WeakReference::create($aggregate);
$call = ini_set(...); $keep = $call; $result = 99; echo 'B|';
$result = $call->__invoke(
    ...$aggregate
);
echo 'A|', $result, '|', ini_get('precision'), '|', $aggregate;
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

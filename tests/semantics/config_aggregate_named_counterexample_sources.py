#!/usr/bin/env python3
"""Check inherited named CONFIG sends from an Aggregate-returned Iterator."""
from pathlib import Path

import global_constant_sources as family


CLASSES = br'''<?php
class ConfigAggregateNamedIterator101 implements Iterator {
    public $i = 0;
    public function rewind(): void { echo 'R|'; $this->i = 0; }
    public function valid(): bool { echo 'V', $this->i, '|'; return $this->i < 2; }
    public function current(): mixed {
        global $v0, $v1;
        echo 'C', $this->i, '|';
        return $this->i === 0 ? $v0 : $v1;
    }
    public function key(): mixed {
        global $aggregate, $v0, $k0, $k1;
        echo 'K', $this->i, '|';
        if ($this->i === 0) { $aggregate = null; $v0 = 'output_buffering'; }
        return $this->i === 0 ? $k0 : $k1;
    }
    public function next(): void { echo 'N', $this->i, '|'; ++$this->i; }
}
class ConfigAggregateNamed101 implements IteratorAggregate {
    public function getIterator(): Traversable { global $it; echo 'G|'; return $it; }
}
'''


def source(setup, call):
    return CLASSES + setup + br'''
$it = new ConfigAggregateNamedIterator101; $itHold = $it;
$aggregate = new ConfigAggregateNamed101; $aggregateHold = $aggregate;
$result = 99; echo 'B|';
''' + call


family.CASES = {
    'aggregate-named-forward': source(
        br"$k0 = 'option'; $k1 = 'value'; $v0 = 'precision'; $v1 = '8';",
        br'''$result = ini_set(...$aggregate);
echo 'A|', $result, '|', ini_get('precision'), '|', $it->i, '|', $v0;
'''),
    'aggregate-duplicate-stops-before-next': source(
        br"$k0 = 'option'; $k1 = 'option'; $v0 = 'precision'; $v1 = 'output_buffering';",
        br'''try { $result = ini_set(...$aggregate); echo 'BAD-CALL|'; }
catch (Error $e) { echo 'E|', $e->getMessage(), '|', $result, '|', ini_get('precision'), '|', $it->i, '|', $v0; }
'''),
}
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()

#!/usr/bin/env python3
"""An Aggregate input CV becomes its returned Iterator at an invalid key."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'aggregate-rebound-input-invalid-second-key': br'''<?php
class ConfigReboundKeyIterator104 implements Iterator {
    public $i = 0;
    public function rewind(): void { echo 'R|'; $this->i = 0; }
    public function valid(): bool { echo 'V', $this->i, '|'; return $this->i < 2; }
    public function current(): mixed { echo 'C', $this->i, '|'; return $this->i === 0 ? 'precision' : '8'; }
    public function key(): mixed {
        global $aggregate, $iterator;
        echo 'K', $this->i, '|';
        if ($this->i === 1) { $aggregate = $iterator; }
        return $this->i === 0 ? 0 : null;
    }
    public function next(): void { echo 'N', $this->i, '|'; ++$this->i; }
}
class ConfigReboundAggregate104 implements IteratorAggregate {
    public function getIterator(): Traversable { global $iterator; echo 'G|'; return $iterator; }
}
$iterator = new ConfigReboundKeyIterator104; $iteratorHold = $iterator;
$aggregate = new ConfigReboundAggregate104; $aggregateHold = $aggregate;
$result = 99; echo 'B|';
try { $result = ini_set(...$aggregate); echo 'BAD-CALL|'; }
catch (Error $e) {
    echo 'E|', $e->getMessage(), '|', $e->getLine(), '|', $result,
         '|', ini_get('precision'), '|', $iterator->i, '|', $aggregate === $iterator ? 'S' : 'BAD';
}
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

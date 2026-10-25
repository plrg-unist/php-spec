#!/usr/bin/env python3
"""Native-first CONFIG unpack through a real IteratorAggregate producer."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'fixed-config-aggregate-produces-retained-user-iterator': br'''<?php
class ConfigAggregateIterator89 implements Iterator {
    public $pos = 0;
    public function rewind(): void { echo 'R|'; $this->pos = 0; }
    public function valid(): bool { echo 'V', $this->pos, '|'; return $this->pos < 2; }
    public function current(): mixed { echo 'C', $this->pos, '|'; return $this->pos === 0 ? 'precision' : '8'; }
    public function key(): mixed { echo 'K', $this->pos, '|'; return $this->pos === 0 ? -11 : 7; }
    public function next(): void { echo 'N', $this->pos, '|'; ++$this->pos; }
}
class ConfigAggregate89 implements IteratorAggregate {
    public function getIterator(): Traversable { global $it; echo 'G|'; return $it; }
}
$it = new ConfigAggregateIterator89; $iteratorHold = $it;
$aggregate = new ConfigAggregate89; $aggregateHold = $aggregate;
$result = 99; echo 'B|';
$result = ini_set(...$aggregate);
echo 'A|', $result, '|', ini_get('precision'), '|', $it->pos, '|E';
''',
    'retained-config-aggregate-preserves-selected-setter-through-producer': br'''<?php
class ConfigOwnedAggregateIterator89 implements Iterator {
    public $pos = 0;
    public function rewind(): void { echo 'R|'; $this->pos = 0; }
    public function valid(): bool { echo 'V', $this->pos, '|'; return $this->pos < 2; }
    public function current(): mixed { echo 'C', $this->pos, '|'; return $this->pos === 0 ? 'precision' : '11'; }
    public function key(): mixed { echo 'K', $this->pos, '|'; return 3; }
    public function next(): void {
        echo 'N', $this->pos, '|';
        if ($this->pos === 1) { ini_set('precision', '7'); }
        ++$this->pos;
    }
}
class ConfigOwnedAggregate89 implements IteratorAggregate {
    public function getIterator(): Traversable {
        global $it, $call;
        echo 'G|'; $call = ini_get(...); ini_set('precision', '6');
        return $it;
    }
}
$it = new ConfigOwnedAggregateIterator89; $iteratorHold = $it;
$aggregate = new ConfigOwnedAggregate89; $aggregateHold = $aggregate;
$call = ini_set(...); $keep = $call; $result = 99; echo 'B|';
$result = $call(...$aggregate);
echo 'A|', $result, '|', ini_get('precision'), '|', $call('precision'), '|', $it->pos;
echo '|R|', $keep('precision', '9'), '|', ini_get('precision');
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

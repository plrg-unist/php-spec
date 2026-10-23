#!/usr/bin/env python3
"""Native-first CONFIG calls unpacking an initialized user Iterator."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'fixed-config-iterator-runs-all-callbacks-before-api': br'''<?php
class ConfigFixedIterator87 implements Iterator {
    public $pos = 0;
    public function rewind(): void { echo 'R|'; $this->pos = 0; }
    public function valid(): bool { echo 'V', $this->pos, '|'; return $this->pos < 2; }
    public function current(): mixed { echo 'C', $this->pos, '|'; return $this->pos === 0 ? 'precision' : '8'; }
    public function key(): mixed { echo 'K', $this->pos, '|'; return $this->pos === 0 ? -11 : 7; }
    public function next(): void { echo 'N', $this->pos, '|'; ++$this->pos; }
}
$it = new ConfigFixedIterator87; $result = 99; echo 'B|';
$result = ini_set(...$it);
echo 'A|', $result, '|', ini_get('precision'), '|', $it->pos;
unset($it); echo '|E';
''',
    'retained-config-iterator-preserves-callee-across-callback-writes': br'''<?php
class ConfigOwnedIterator87 implements Iterator {
    public $pos = 0;
    public function rewind(): void { echo 'R|'; $this->pos = 0; }
    public function valid(): bool { echo 'V', $this->pos, '|'; return $this->pos < 2; }
    public function current(): mixed {
        global $call;
        echo 'C', $this->pos, '|';
        if ($this->pos === 0) { $call = ini_get(...); return 'precision'; }
        return '11';
    }
    public function key(): mixed { echo 'K', $this->pos, '|'; return 3; }
    public function next(): void {
        echo 'N', $this->pos, '|';
        if ($this->pos === 1) { ini_set('precision', '6'); }
        ++$this->pos;
    }
}
$it = new ConfigOwnedIterator87; $call = ini_set(...); $keep = $call;
$result = 99; echo 'B|';
$result = $call(...$it);
echo 'A|', $result, '|', ini_get('precision'), '|', $call('precision'), '|', $it->pos;
unset($it); echo '|E|R|', $keep('precision', '12'), '|', ini_get('precision');
''',
    'config-nontraversable-still-rejects-before-api': br'''<?php
$it = new stdClass; $result = 99; echo 'B|';
try { $result = ini_set(...$it); echo 'BAD'; }
catch (TypeError $e) { echo $e->getMessage(), '|', $result, '|', ini_get('precision'); }
echo '|E';
''',
    'config-generator-unpack-remains-explicitly-unsupported': br'''<?php
function configGenerator87() { echo 'G|'; yield 'precision'; yield '8'; }
$it = configGenerator87(); echo 'B|';
$result = ini_set(...$it); echo 'A|', $result, '|', ini_get('precision');
''',
    'config-aggregate-unpack-remains-explicitly-unsupported': br'''<?php
class ConfigAggregate87 implements IteratorAggregate {
    public function getIterator(): Traversable { echo 'G|'; yield 'precision'; yield '8'; }
}
$it = new ConfigAggregate87; echo 'B|';
$result = ini_set(...$it); echo 'A|', $result, '|', ini_get('precision');
''',
}
family.UNSUPPORTED = {
    name: ('CONFIG Traversable unpack outside initialized Iterator domain', b'B|')
    for name in family.CASES if name.endswith('remains-explicitly-unsupported')
}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()

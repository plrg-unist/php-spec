#!/usr/bin/env python3
"""Frozen native-first CONFIG Aggregate-returned Iterator child originals."""
from pathlib import Path
import hashlib

import global_constant_sources as family


COMMON = br'''<?php
class Child116 { public function __destruct() { global $stamp; $stamp = 2; echo 'C|'; } }
class FreshIterator114 implements Iterator {
    public $child;
    public $i = 0;
    public function __destruct() { global $stamp, $childWatch; $stamp = 1; echo 'D|', $childWatch->get() === $this->child ? 'L|' : 'BAD|'; }
    public function rewind(): void { echo 'R|'; $this->i = 0; }
    public function valid(): bool { echo 'V', $this->i, '|'; return $this->i < 2; }
    public function current(): mixed {
        global $iterWatch;
        echo 'C', $this->i, '|', $iterWatch->get() === $this ? 'L|' : 'BAD|';
        return $this->i === 0 ? 'precision' : '8';
    }
    public function key(): mixed {
        global $producer, $producerWatch, $iterWatch, $saved, $mode;
        echo 'K', $this->i, '|';
        if ($this->i === 0) {
            $producer = null;
            echo 'P', $producerWatch->get() === null ? 'D|' : 'L|';
            echo 'I', $iterWatch->get() === $this ? 'L|' : 'D|';
        }
        if ($mode === 'throw' && $this->i === 1) { throw $saved; }
        return $mode === 'invalid' && $this->i === 1 ? false : $this->i;
    }
    public function next(): void { echo 'N', $this->i, '|'; ++$this->i; }
}
class FreshAggregate114 implements IteratorAggregate {
    public function getIterator(): Traversable {
        global $iterWatch, $childWatch;
        echo 'G|';
        $it = new FreshIterator114;
        $it->child = new Child116;
        $childWatch = WeakReference::create($it->child);
        $iterWatch = WeakReference::create($it);
        return $it;
    }
}
'''

SETUP = br'''$iterWatch = null;
$childWatch = null;
$stamp = 0;
$producer = new FreshAggregate114;
$producerWatch = WeakReference::create($producer);
$saved = new Exception('saved');
$result = 99;
echo 'B|';
'''

TAILS = {
    'normal': br'''$result = ini_set(...$producer);
echo 'A|', $result, '|', ini_get('precision'), '|';
echo 'W|', $producerWatch->get() === null ? 'D|' : 'L|', $iterWatch->get() === null ? 'D|' : 'L|', $childWatch->get() === null ? 'D|' : 'L|', 'S', $stamp, '|';
''',
    'invalid': br'''try { $result = ini_set(...$producer); echo 'BAD|'; }
catch (Error $e) {
    echo 'E|', $e->getMessage(), '|', $e->getLine(), '|', $result,
         '|', ini_get('precision'), '|';
}
echo 'W|', $producerWatch->get() === null ? 'D|' : 'L|', $iterWatch->get() === null ? 'D|' : 'L|', $childWatch->get() === null ? 'D|' : 'L|', 'S', $stamp, '|';
''',
    'throw': br'''try { $result = ini_set(...$producer); echo 'BAD|'; }
catch (Exception $e) {
    echo 'E|', $e === $saved ? 'S|' : 'BAD|', $e->getMessage(), '|',
         $result, '|', ini_get('precision'), '|';
}
echo 'W|', $producerWatch->get() === null ? 'D|' : 'L|', $iterWatch->get() === null ? 'D|' : 'L|', $childWatch->get() === null ? 'D|' : 'L|', 'S', $stamp, '|';
''',
}

family.CASES = {
    'iterator-child-' + name: COMMON + ("$mode = '" + name + "';\n").encode() + SETUP + tail
    for name, tail in TAILS.items()
}
family.UNSUPPORTED = {}
family.BASELINE = ('CONFIG Aggregate return outside shared initialized Iterator domain', b'B|G|')
family.MODEL_TIMEOUTS = {name: 180 for name in family.CASES}
EXPECTED_SHA256 = {
    'iterator-child-normal': '0fcdb875b39447335576cc474a354d710cdc63011814d4fdfabfed9e782e34e6',
    'iterator-child-invalid': '07b3d979623963ced73dfa532cea962f991150a938d9889c51b09b17d491b8c9',
    'iterator-child-throw': '55ce1cf9637d9f58766f68a10559c9163f2fd55be9c0a4fb2fc9dc3b59c6f148',
}
assert {name: hashlib.sha256(source).hexdigest() for name, source in family.CASES.items()} == EXPECTED_SHA256
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()

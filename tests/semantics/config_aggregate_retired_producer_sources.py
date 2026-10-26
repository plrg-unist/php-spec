#!/usr/bin/env python3
"""Frozen native-first Aggregate producer-retirement CONFIG originals."""
from pathlib import Path
import hashlib

import global_constant_sources as family


COMMON = br'''<?php
class FreshIterator114 implements Iterator {
    public $i = 0;
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
        global $iterWatch;
        echo 'G|';
        $it = new FreshIterator114;
        $iterWatch = WeakReference::create($it);
        return $it;
    }
}
'''

SETUP = br'''$iterWatch = null;
$producer = new FreshAggregate114;
$producerWatch = WeakReference::create($producer);
$saved = new Exception('saved');
$result = 99;
echo 'B|';
'''

TAILS = {
    'normal': br'''$result = ini_set(...$producer);
echo 'A|', $result, '|', ini_get('precision'), '|';
echo 'W|', $producerWatch->get() === null ? 'D|' : 'L|', $iterWatch->get() === null ? 'D|' : 'L|';
''',
    'invalid': br'''try { $result = ini_set(...$producer); echo 'BAD|'; }
catch (Error $e) {
    echo 'E|', $e->getMessage(), '|', $e->getLine(), '|', $result,
         '|', ini_get('precision'), '|';
}
echo 'W|', $producerWatch->get() === null ? 'D|' : 'L|', $iterWatch->get() === null ? 'D|' : 'L|';
''',
    'throw': br'''try { $result = ini_set(...$producer); echo 'BAD|'; }
catch (Exception $e) {
    echo 'E|', $e === $saved ? 'S|' : 'BAD|', $e->getMessage(), '|',
         $result, '|', ini_get('precision'), '|';
}
echo 'W|', $producerWatch->get() === null ? 'D|' : 'L|', $iterWatch->get() === null ? 'D|' : 'L|';
''',
}

family.CASES = {
    'retired-' + name: COMMON + ("$mode = '" + name + "';\n").encode() + SETUP + tail
    for name, tail in TAILS.items()
}
family.UNSUPPORTED = {}
EXPECTED_SHA256 = {
    'retired-normal': '5057047255cefa72e4b7f25ace825117a61b257bfb21fbd5ba38102deb732100',
    'retired-invalid': '2da69f27ba8dbd205a896e2c4410d073ea9d3a23823850a8efea5b08419a3acc',
    'retired-throw': '4ab4bb1abc839585633742eba64c583a70309bc47cc00afe22609b2ffc965990',
}
assert {name: hashlib.sha256(source).hexdigest() for name, source in family.CASES.items()} == EXPECTED_SHA256
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()

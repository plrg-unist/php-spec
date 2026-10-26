#!/usr/bin/env python3
"""Frozen native-first CONFIG Aggregate-returned Iterator finalizer originals."""
from pathlib import Path
import hashlib

import global_constant_sources as family


COMMON = br'''<?php
class FreshIterator114 implements Iterator {
    public $i = 0;
    public function __destruct() { global $stamp; $stamp = 1; echo 'D|'; }
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
echo 'W|', $producerWatch->get() === null ? 'D|' : 'L|', $iterWatch->get() === null ? 'D|' : 'L|', 'S', $stamp, '|';
''',
    'invalid': br'''try { $result = ini_set(...$producer); echo 'BAD|'; }
catch (Error $e) {
    echo 'E|', $e->getMessage(), '|', $e->getLine(), '|', $result,
         '|', ini_get('precision'), '|';
}
echo 'W|', $producerWatch->get() === null ? 'D|' : 'L|', $iterWatch->get() === null ? 'D|' : 'L|', 'S', $stamp, '|';
''',
    'throw': br'''try { $result = ini_set(...$producer); echo 'BAD|'; }
catch (Exception $e) {
    echo 'E|', $e === $saved ? 'S|' : 'BAD|', $e->getMessage(), '|',
         $result, '|', ini_get('precision'), '|';
}
echo 'W|', $producerWatch->get() === null ? 'D|' : 'L|', $iterWatch->get() === null ? 'D|' : 'L|', 'S', $stamp, '|';
''',
}

family.CASES = {
    'iterator-finalizer-' + name: COMMON + ("$mode = '" + name + "';\n").encode() + SETUP + tail
    for name, tail in TAILS.items()
}
family.UNSUPPORTED = {}
family.MODEL_TIMEOUTS = {name: 180 for name in family.CASES}
EXPECTED_SHA256 = {
    'iterator-finalizer-normal': '5f9b9a44ef2cf3be6588d929487783f6bf64a6e8641e836d003dee00f2856b4b',
    'iterator-finalizer-invalid': 'f238ffb19da5596dbe21a5b882891549715defa081ae18772048811bb261196f',
    'iterator-finalizer-throw': '64dc22dee89c69651ce75046e1f006df88823084d7b21cacef5867636802b66d',
}
assert {name: hashlib.sha256(source).hexdigest() for name, source in family.CASES.items()} == EXPECTED_SHA256
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()

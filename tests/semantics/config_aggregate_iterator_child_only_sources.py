#!/usr/bin/env python3
"""Frozen child-only CONFIG Iterator originals from the CONFIG116 review."""
from pathlib import Path
import hashlib

import global_constant_sources as family


COMMON = br'''<?php
class ReviewChild116 {
    public function __destruct() { global $childDeaths; ++$childDeaths; echo 'C|'; }
}
class ReviewIterator116 implements Iterator {
    public $i = 0;
    public $child;
    public function rewind(): void { echo 'R|'; $this->i = 0; }
    public function valid(): bool { echo 'V', $this->i, '|'; return $this->i < 2; }
    public function current(): mixed { echo 'U', $this->i, '|'; return $this->i === 0 ? 'precision' : '8'; }
    public function key(): mixed {
        global $producer, $producerWatch, $iterWatch, $childWatch, $saved, $mode;
        echo 'K', $this->i, '|';
        if ($this->i === 0) {
            $producer = null;
            echo 'P', $producerWatch->get() === null ? 'D|' : 'L|';
            echo 'I', $iterWatch->get() === $this ? 'L|' : 'D|';
            echo 'F', $childWatch->get() === $this->child ? 'L|' : 'D|';
        }
        if ($mode === 'throw' && $this->i === 1) { throw $saved; }
        return $mode === 'invalid' && $this->i === 1 ? false : $this->i;
    }
    public function next(): void { echo 'N', $this->i, '|'; ++$this->i; }
}
class ReviewAggregate116 implements IteratorAggregate {
    public function getIterator(): Traversable {
        global $iterWatch, $childWatch;
        echo 'G|';
        $it = new ReviewIterator116;
        $it->child = new ReviewChild116;
        $iterWatch = WeakReference::create($it);
        $childWatch = WeakReference::create($it->child);
        return $it;
    }
}
$iterWatch = null;
$childWatch = null;
$childDeaths = 0;
$producer = new ReviewAggregate116;
$producerWatch = WeakReference::create($producer);
$saved = new Exception('saved');
$result = 99;
echo 'B|';
'''

TAILS = {
    'child-only-normal': br'''$mode = 'normal';
$result = ini_set(...$producer);
echo 'A|', $result, '|', ini_get('precision'), '|';
echo 'W|', $producerWatch->get() === null ? 'D|' : 'L|', $iterWatch->get() === null ? 'D|' : 'L|', $childWatch->get() === null ? 'D|' : 'L|', 'C', $childDeaths, '|';
''',
    'child-only-invalid': br'''$mode = 'invalid';
try { $result = ini_set(...$producer); echo 'BAD|'; }
catch (Error $e) { echo 'E|', $e->getMessage(), '|', $e->getLine(), '|', $result, '|', ini_get('precision'), '|'; }
echo 'W|', $producerWatch->get() === null ? 'D|' : 'L|', $iterWatch->get() === null ? 'D|' : 'L|', $childWatch->get() === null ? 'D|' : 'L|', 'C', $childDeaths, '|';
''',
    'child-only-throw': br'''$mode = 'throw';
try { $result = ini_set(...$producer); echo 'BAD|'; }
catch (Exception $e) { echo 'E|', $e === $saved ? 'S|' : 'BAD|', $e->getMessage(), '|', $result, '|', ini_get('precision'), '|'; }
echo 'W|', $producerWatch->get() === null ? 'D|' : 'L|', $iterWatch->get() === null ? 'D|' : 'L|', $childWatch->get() === null ? 'D|' : 'L|', 'C', $childDeaths, '|';
''',
}
family.CASES = {name: COMMON + tail for name, tail in TAILS.items()}
family.UNSUPPORTED = {}
family.BASELINE = ('CONFIG Aggregate return outside shared initialized Iterator domain', b'B|G|')
family.MODEL_TIMEOUTS = {name: 180 for name in family.CASES}
EXPECTED_SHA256 = {'child-only-normal': 'b4e6ae1318f6f117fd587d503ceeb48a0d6ca4c9e900d304d06abdc1d848f1b4', 'child-only-invalid': '0adf84b5e199724a840ecacd0735f9bdc7ccb2fcc435a17b3d3f4ff539227e72', 'child-only-throw': '9fa30aa17edfdc7faa71b4d4ec81b8317d42dcb1cbec4a250c368cc92f3cfb91'}
assert {name: hashlib.sha256(source).hexdigest() for name, source in family.CASES.items()} == EXPECTED_SHA256
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()

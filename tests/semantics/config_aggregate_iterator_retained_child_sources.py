#!/usr/bin/env python3
"""Native-first CONFIG Iterator Child retained by an actual outside CV."""
from pathlib import Path
import hashlib

import global_constant_sources as family


COMMON = br'''<?php
class RetainedChild118 {
    public function __destruct() { global $childDeaths, $iterWatch, $childWatch; ++$childDeaths; echo 'C|', $iterWatch->get() === null ? 'PD|' : 'BAD|', $childWatch->get() === $this ? 'CL|' : 'BAD|'; }
}
class RetainedIterator118 implements Iterator {
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
class RetainedAggregate118 implements IteratorAggregate {
    public function getIterator(): Traversable {
        global $iterWatch, $childWatch, $heldChild;
        echo 'G|';
        $it = new RetainedIterator118;
        $it->child = new RetainedChild118;
        $heldChild = $it->child;
        $iterWatch = WeakReference::create($it);
        $childWatch = WeakReference::create($it->child);
        return $it;
    }
}
$iterWatch = null;
$childWatch = null;
$heldChild = null;
$childDeaths = 0;
$producer = new RetainedAggregate118;
$producerWatch = WeakReference::create($producer);
$saved = new Exception('saved');
$result = 99;
echo 'B|';
'''

TAILS = {
    'retained-child-normal': br'''$mode = 'normal';
$result = ini_set(...$producer);
echo 'A|', $result, '|', ini_get('precision'), '|';
echo 'W|', $producerWatch->get() === null ? 'D|' : 'L|', $iterWatch->get() === null ? 'D|' : 'L|', $childWatch->get() === $heldChild ? 'L|' : 'BAD|', 'C', $childDeaths, '|';
echo 'U|'; unset($heldChild);
echo 'Z|', $childWatch->get() === null ? 'D|' : 'BAD|', 'C', $childDeaths, '|';
''',
    'retained-child-invalid': br'''$mode = 'invalid';
try { $result = ini_set(...$producer); echo 'BAD|'; }
catch (Error $e) { echo 'E|', $e->getMessage(), '|', $e->getLine(), '|', $result, '|', ini_get('precision'), '|'; }
echo 'W|', $producerWatch->get() === null ? 'D|' : 'L|', $iterWatch->get() === null ? 'D|' : 'L|', $childWatch->get() === $heldChild ? 'L|' : 'BAD|', 'C', $childDeaths, '|';
echo 'U|'; unset($heldChild);
echo 'Z|', $childWatch->get() === null ? 'D|' : 'BAD|', 'C', $childDeaths, '|';
''',
    'retained-child-throw': br'''$mode = 'throw';
try { $result = ini_set(...$producer); echo 'BAD|'; }
catch (Exception $e) { echo 'E|', $e === $saved ? 'S|' : 'BAD|', $e->getMessage(), '|', $result, '|', ini_get('precision'), '|'; }
echo 'W|', $producerWatch->get() === null ? 'D|' : 'L|', $iterWatch->get() === null ? 'D|' : 'L|', $childWatch->get() === $heldChild ? 'L|' : 'BAD|', 'C', $childDeaths, '|';
echo 'U|'; unset($heldChild);
echo 'Z|', $childWatch->get() === null ? 'D|' : 'BAD|', 'C', $childDeaths, '|';
''',
}
family.CASES = {name: COMMON + tail for name, tail in TAILS.items()}
family.UNSUPPORTED = {}
family.BASELINE = ('CONFIG Aggregate return outside shared initialized Iterator domain', b'B|G|')
family.MODEL_TIMEOUTS = {name: 180 for name in family.CASES}
EXPECTED_SHA256 = {
    "retained-child-normal": "b34f0f064e3138a1c77e053be69cfe341bed69fc74067fa42fed02182a3d7e7e",
    "retained-child-invalid": "274660c5075c6adaec710a143c590a1310a77adda0d18894b067e068543f356d",
    "retained-child-throw": "cf29c627df80f136bb46ef4d59c6e44bf12ebb7fc9de48afb609c198eb7d742a"
}
assert {name: hashlib.sha256(source).hexdigest() for name, source in family.CASES.items()} == EXPECTED_SHA256
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()

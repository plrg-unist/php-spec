#!/usr/bin/env python3
"""Native-first descriptor-backed CONFIG Iterator fields and finite Child DAGs."""
from pathlib import Path
import hashlib

import global_constant_sources as family


PRIMITIVE = br'''<?php
class LayoutPrimitiveIterator119 implements Iterator {
    public $i = 0;
    private int $tag = 7;
    public $pool = [1, [2]];
    public $payload;
    public $shadow;
    public $alias;
    public function rewind(): void { echo 'R|'; $this->i = 0; }
    public function valid(): bool { echo 'V', $this->i, '|'; return $this->i < 2; }
    public function current(): mixed { echo 'U', $this->i, '|'; return $this->i === 0 ? 'precision' : '8'; }
    public function key(): mixed {
        global $producer, $producerWatch, $iterWatch, $scalar, $arrayHold;
        echo 'K', $this->i, '|';
        if ($this->i === 0) {
            $producer = null;
            $this->alias = 74;
            $this->payload['x'][1] = 9;
            echo 'P', $producerWatch->get() === null ? 'D|' : 'BAD|';
            echo 'I', $iterWatch->get() === $this ? 'L|' : 'BAD|';
            echo 'F|', $this->tag, '|', $scalar, '|', $this->payload['x'][1], '|', $this->shadow['x'][1], '|', $arrayHold['x'][1], '|', $this->pool[1][0], '|';
        }
        return $this->i;
    }
    public function next(): void { echo 'N', $this->i, '|'; ++$this->i; }
}
class LayoutPrimitiveAggregate119 implements IteratorAggregate {
    public function getIterator(): Traversable {
        global $iterWatch, $scalar, $arrayHold;
        echo 'G|';
        $it = new LayoutPrimitiveIterator119;
        $it->payload = ['x' => ['p', 3]];
        $it->shadow = $it->payload;
        $arrayHold = $it->payload;
        $it->alias =& $scalar;
        $iterWatch = WeakReference::create($it);
        return $it;
    }
}
$iterWatch = null;
$scalar = 73;
$arrayHold = null;
$producer = new LayoutPrimitiveAggregate119;
$producerWatch = WeakReference::create($producer);
echo 'B|';
$result = ini_set(...$producer);
echo 'A|', $result, '|', ini_get('precision'), '|';
echo 'W|', $producerWatch->get() === null ? 'PD|' : 'BAD|', $iterWatch->get() === null ? 'ID|' : 'BAD|', $scalar, '|', $arrayHold['x'][1], '|';
'''

GRAPH = br'''<?php
class LayoutLeaf119 {
    public function __destruct() { global $leafDeaths, $iterWatch, $leafWatch; ++$leafDeaths; echo 'L|', $iterWatch->get() === null ? 'PD|' : 'BAD|', $leafWatch->get() === $this ? 'CL|' : 'BAD|'; }
}
class LayoutBranch119 {
    public $bag;
    public $tag = 5;
    public function __destruct() { global $branchDeaths, $iterWatch, $branchWatch, $leafWatch; ++$branchDeaths; echo 'J|', $iterWatch->get() === null ? 'PD|' : 'BAD|', $branchWatch->get() === $this ? 'BL|' : 'BAD|', $this->bag[0] === $leafWatch->get() && $this->bag[1] === $this->bag[0] ? 'LL|' : 'BAD|', $this->tag, '|'; }
}
class LayoutGraphIterator119 implements Iterator {
    public $i = 0;
    private int $tag = 7;
    public $pool = [1, [2]];
    public $payload;
    public $shadow;
    public $alias;
    public function rewind(): void { echo 'R|'; $this->i = 0; }
    public function valid(): bool { echo 'V', $this->i, '|'; return $this->i < 2; }
    public function current(): mixed { echo 'U', $this->i, '|'; return $this->i === 0 ? 'precision' : '8'; }
    public function key(): mixed {
        global $producer, $producerWatch, $iterWatch, $branchWatch, $leafWatch, $saved, $mode;
        echo 'K', $this->i, '|';
        if ($this->i === 0) {
            $producer = null;
            echo 'P', $producerWatch->get() === null ? 'D|' : 'BAD|';
            echo 'I', $iterWatch->get() === $this ? 'L|' : 'BAD|';
            echo 'F|', $this->payload[0][0] === $this->shadow && $this->shadow === $branchWatch->get() ? 'BL|' : 'BAD|', $this->alias === $leafWatch->get() ? 'LL|' : 'BAD|', $this->tag, '|', $this->pool[1][0], '|';
        }
        if ($mode === 'throw' && $this->i === 1) { throw $saved; }
        return $mode === 'invalid' && $this->i === 1 ? false : $this->i;
    }
    public function next(): void { echo 'N', $this->i, '|'; ++$this->i; }
}
class LayoutGraphAggregate119 implements IteratorAggregate {
    public function getIterator(): Traversable {
        global $iterWatch, $branchWatch, $leafWatch, $heldLeaf;
        echo 'G|';
        $leaf = new LayoutLeaf119;
        $branch = new LayoutBranch119;
        $branch->bag = [$leaf, $leaf];
        $it = new LayoutGraphIterator119;
        $it->payload = [[$branch]];
        $it->shadow = $branch;
        $heldLeaf = $leaf;
        $it->alias =& $heldLeaf;
        $iterWatch = WeakReference::create($it);
        $branchWatch = WeakReference::create($branch);
        $leafWatch = WeakReference::create($leaf);
        return $it;
    }
}
$iterWatch = null;
$branchWatch = null;
$leafWatch = null;
$heldLeaf = null;
$branchDeaths = 0;
$leafDeaths = 0;
$producer = new LayoutGraphAggregate119;
$producerWatch = WeakReference::create($producer);
$saved = new Exception('saved');
$result = 99;
echo 'B|';
'''

BOUNDARY = br'''echo 'W|', $producerWatch->get() === null ? 'PD|' : 'BAD|', $iterWatch->get() === null ? 'ID|' : 'BAD|', $branchWatch->get() === null ? 'BD|' : 'BAD|', $leafWatch->get() === $heldLeaf ? 'LL|' : 'BAD|', 'J', $branchDeaths, '|L', $leafDeaths, '|';
echo 'X|'; unset($heldLeaf);
echo 'Z|', $leafWatch->get() === null ? 'LD|' : 'BAD|', 'L', $leafDeaths, '|';
'''
TAILS = {
    'graph-normal': br'''$mode = 'normal';
$result = ini_set(...$producer);
echo 'A|', $result, '|', ini_get('precision'), '|';
''',
    'graph-invalid': br'''$mode = 'invalid';
try { $result = ini_set(...$producer); echo 'BAD|'; }
catch (Error $e) { echo 'E|', $e->getMessage(), '|', $e->getLine(), '|', $result, '|', ini_get('precision'), '|'; }
''',
    'graph-throw': br'''$mode = 'throw';
try { $result = ini_set(...$producer); echo 'BAD|'; }
catch (Exception $e) { echo 'E|', $e === $saved ? 'S|' : 'BAD|', $e->getMessage(), '|', $result, '|', ini_get('precision'), '|'; }
''',
}
family.CASES = {'primitive-layout': PRIMITIVE, **{name: GRAPH + tail + BOUNDARY for name, tail in TAILS.items()}}
family.UNSUPPORTED = {}
family.BASELINE = ('CONFIG Aggregate return outside shared initialized Iterator domain', b'B|G|')
family.MODEL_TIMEOUTS = {name: 240 for name in family.CASES}
EXPECTED_SHA256 = {
    'primitive-layout': '0435cabc56471ec74e77d07827d07f0b65142c5a70eaaec40e0fceb4321f6780',
    'graph-normal': '6a11ccedb80b26edde46f175230e73cbd60c8bf47bb9652666ac1079129fa8d0',
    'graph-invalid': '729967dc043949839a4e1e388047be06a129a2ae78186d437df73c4b84cf3c61',
    'graph-throw': '8599c542b6f46997d5d8491647934f8ccea5d55b73046681056e0eaad5d29428',
}
assert {name: hashlib.sha256(source).hexdigest() for name, source in family.CASES.items()} == EXPECTED_SHA256

family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()

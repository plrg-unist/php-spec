#!/usr/bin/env python3
"""A temporary Iterator's invalid unpack key retires DATA then INPUT."""
from pathlib import Path

import global_constant_sources as family


COMMON = br'''<?php
class ConfigTempInvalidKey106 implements Iterator {
    public $i = 0;
    public function rewind(): void { echo 'R|'; $this->i = 0; }
    public function valid(): bool { echo 'V', $this->i, '|'; return $this->i < 2; }
    public function current(): mixed {
        global $v0, $v1;
        echo 'C', $this->i, '|';
        return $this->i === 0 ? $v0 : $v1;
    }
    public function key(): mixed {
        global $badAt, $badKey, $seen, $watch, $v0, $v1;
        echo 'K', $this->i, '|', $watch->get() === null ? 'BAD|' : 'H|';
        $seen = $this->i;
        if ($this->i === 0) { $v0 = '8'; } else { $v1 = 'precision'; }
        return $this->i === $badAt ? $badKey : $this->i;
    }
    public function next(): void { echo 'N', $this->i, '|'; ++$this->i; }
}
function makeConfigTempInvalidKey106() {
    global $watch, $hold, $retain;
    echo 'P|';
    $it = new ConfigTempInvalidKey106;
    $watch = WeakReference::create($it);
    if ($retain) { $hold = $it; }
    return $it;
}
'''


def source(setup):
    return COMMON + setup + br'''
$watch = null; $hold = null; $seen = -1; $v0 = 'precision'; $v1 = '8';
$result = 99; echo 'B|';
try { $result = ini_set(...makeConfigTempInvalidKey106()); echo 'BAD-CALL|'; }
catch (Error $e) {
    echo 'E|', $e->getMessage(), '|', $e->getLine(), '|', $result,
         '|', ini_get('precision'), '|', $seen, '|', $v0, '|', $v1,
         '|', $watch->get() === null ? 'D' : 'H';
} finally { echo '|F'; }
'''


family.CASES = {
    'sole-first-null-key-retires-input': source(br'$retain = false; $badAt = 0; $badKey = null;'),
    'retained-second-bool-key-keeps-input': source(br'$retain = true; $badAt = 1; $badKey = true;'),
    'sole-second-float-key-retires-input': source(br'$retain = false; $badAt = 1; $badKey = 1.5;'),
}
family.UNSUPPORTED = {}
family.BASELINE = ('CONFIG Iterator unpack key outside integer domain', b'B|P|R|V0|C0|K0|H|')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()

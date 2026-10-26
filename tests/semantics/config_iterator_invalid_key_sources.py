#!/usr/bin/env python3
"""Invalid user Iterator keys fail CONFIG unpack before send, next, or API."""
from pathlib import Path

import global_constant_sources as family


COMMON = br'''<?php
class ConfigInvalidKey104 implements Iterator {
    public $i = 0;
    public function rewind(): void { echo 'R|'; $this->i = 0; }
    public function valid(): bool { echo 'V', $this->i, '|'; return $this->i < 2; }
    public function current(): mixed {
        global $v0, $v1;
        echo 'C', $this->i, '|';
        return $this->i === 0 ? $v0 : $v1;
    }
    public function key(): mixed {
        global $badAt, $badKey, $v0, $v1;
        echo 'K', $this->i, '|';
        if ($this->i === 0) { $v0 = 'output_buffering'; }
        else { $v1 = 'output_buffering'; }
        return $this->i === $badAt ? $badKey : $this->i;
    }
    public function next(): void { echo 'N', $this->i, '|'; ++$this->i; }
}
'''


def source(setup):
    return COMMON + setup + br'''
$v0 = 'precision'; $v1 = '8'; $it = new ConfigInvalidKey104;
$result = 99; echo 'B|';
try { $result = ini_set(...$it); echo 'BAD-CALL|'; }
catch (Error $e) {
    echo 'E|', $e->getMessage(), '|', $e->getLine(), '|', $result,
         '|', ini_get('precision'), '|', $it->i, '|', $v0, '|', $v1;
} finally { echo '|F'; }
'''


family.CASES = {
    'null-first-key-stops-before-send': source(br'$badAt = 0; $badKey = null;'),
    'null-second-key-abandons-first-send': source(br'$badAt = 1; $badKey = null;'),
    'bool-second-key-abandons-first-send': source(br'$badAt = 1; $badKey = true;'),
    'float-second-key-abandons-first-send': source(br'$badAt = 1; $badKey = 1.5;'),
}
family.UNSUPPORTED = {}
family.BASELINE = ('CONFIG Iterator unpack key outside integer domain', b'B|R|V0|C0|K0|')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()

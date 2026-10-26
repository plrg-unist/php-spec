#!/usr/bin/env python3
"""Named keys streamed by a source Iterator into CONFIG ini_set."""
from pathlib import Path

import global_constant_sources as family


ITERATOR = br'''<?php
class ConfigNamedIterator99 implements Iterator {
    public $i = 0;
    public function rewind(): void { echo 'R|'; $this->i = 0; }
    public function valid(): bool { echo 'V', $this->i, '|'; return $this->i < 2; }
    public function current(): mixed {
        global $v0, $v1;
        echo 'C', $this->i, '|';
        return $this->i === 0 ? $v0 : $v1;
    }
    public function key(): mixed {
        global $k0, $k1, $v0;
        echo 'K', $this->i, '|';
        if ($this->i === 0) { $v0 = 'output_buffering'; }
        return $this->i === 0 ? $k0 : $k1;
    }
    public function next(): void { echo 'N', $this->i, '|'; ++$this->i; }
}
'''


def source(setup, call):
    return ITERATOR + setup + br'''
$it = new ConfigNamedIterator99; $result = 99; echo 'B|';
''' + call


family.CASES = {
    'named-option-then-value-caches-current': source(
        br"$k0 = 'option'; $k1 = 'value'; $v0 = 'precision'; $v1 = '8';",
        br'''$result = ini_set(...$it);
echo 'A|', $result, '|', ini_get('precision'), '|', $it->i, '|', $v0;
'''),
    'named-value-then-option': source(
        br"$k0 = 'value'; $k1 = 'option'; $v0 = '7'; $v1 = 'precision';",
        br'''$result = ini_set(...$it);
echo 'A|', $result, '|', ini_get('precision'), '|', $it->i, '|', $v0;
'''),
    'duplicate-named-stops-before-next': source(
        br"$k0 = 'option'; $k1 = 'option'; $v0 = 'precision'; $v1 = 'output_buffering';",
        br'''try { $result = ini_set(...$it); echo 'BAD-CALL|'; }
catch (Error $e) { echo 'E|', $e->getMessage(), '|', $result, '|', ini_get('precision'), '|', $it->i, '|', $v0; }
'''),
    'unknown-named-stops-before-next': source(
        br"$k0 = 'other'; $k1 = 'value'; $v0 = 'precision'; $v1 = '8';",
        br'''try { $result = ini_set(...$it); echo 'BAD-CALL|'; }
catch (Error $e) { echo 'E|', $e->getMessage(), '|', $result, '|', ini_get('precision'), '|', $it->i, '|', $v0; }
'''),
    'named-then-numeric-string-stops-before-next': source(
        br"$k0 = 'option'; $k1 = '0'; $v0 = 'precision'; $v1 = '8';",
        br'''try { $result = ini_set(...$it); echo 'BAD-CALL|'; }
catch (Error $e) { echo 'E|', $e->getMessage(), '|', $result, '|', ini_get('precision'), '|', $it->i, '|', $v0; }
'''),
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

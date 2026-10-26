#!/usr/bin/env python3
"""Native-first invalid CONFIG keys from a fresh Aggregate-returned Iterator."""
from pathlib import Path

import global_constant_sources as family


COMMON = br'''<?php
class ConfigFreshInvalidIterator111 implements Iterator {
    public $i = 0;
    public function rewind(): void { echo 'R|'; $this->i = 0; }
    public function valid(): bool { echo 'V', $this->i, '|'; return $this->i < 2; }
    public function current(): mixed {
        global $watch, $option, $value;
        echo 'C', $this->i, '|', $watch->get() === $this ? 'H|' : 'BAD|';
        return $this->i === 0 ? $option : $value;
    }
    public function key(): mixed {
        global $watch, $aggregate, $rebindAt, $key0, $key1, $option;
        echo 'K', $this->i, '|', $watch->get() === $this ? 'H|' : 'BAD|';
        if ($this->i === $rebindAt) { $aggregate = null; echo 'U|'; }
        if ($this->i === 0) { $option = 'output_buffering'; }
        return $this->i === 0 ? $key0 : $key1;
    }
    public function next(): void { echo 'N', $this->i, '|'; ++$this->i; }
}
class ConfigFreshInvalidAggregate111 implements IteratorAggregate {
    public function getIterator(): Traversable {
        global $watch;
        echo 'G|';
        $it = new ConfigFreshInvalidIterator111;
        $watch = WeakReference::create($it);
        return $it;
    }
}
'''


def source(setup, call, held=True):
    hold = br'$aggregateHold = $aggregate;' if held else b''
    return COMMON + setup + br'''
$watch = null; $option = 'precision'; $value = '8';
$aggregate = new ConfigFreshInvalidAggregate111; ''' + hold + br'''
$result = 99; echo 'B|';
''' + call


ERROR_CALL = br'''try { $result = ini_set(...$aggregate); echo 'BAD-API|'; }
catch (Error $e) {
    echo 'E|', $e->getMessage(), '|', $e->getLine(), '|', $result,
         '|', ini_get('precision'), '|', $option, '|',
         $watch->get() === null ? 'D' : 'LIVE';
}
echo '|R|', ini_set('precision', '9'), '|', ini_get('precision');
'''


family.CASES = {
    'fresh-null-first-key': source(
        br'$key0 = null; $key1 = 1; $rebindAt = -1;', ERROR_CALL),
    'fresh-bool-second-key-rebind': source(
        br'$key0 = 0; $key1 = false; $rebindAt = 1;', ERROR_CALL),
    'fresh-float-second-key-rebind': source(
        br'$key0 = 0; $key1 = 1.5; $rebindAt = 1;', ERROR_CALL),
    'fresh-named-forward-control': source(
        br"$key0 = 'option'; $key1 = 'value'; $rebindAt = 0;",
        br'''$result = ini_set(...$aggregate);
echo 'A|', $result, '|', ini_get('precision'), '|', $option, '|',
     $watch->get() === null ? 'D' : 'LIVE';
'''),
    'fresh-named-duplicate-control': source(
        br"$key0 = 'option'; $key1 = 'option'; $rebindAt = 0;", ERROR_CALL),
    'unheld-aggregate-rebind-boundary': source(
        br'$key0 = 0; $key1 = 1; $rebindAt = 0;',
        br'''$result = ini_set(...$aggregate);
echo 'A|', $result, '|', ini_get('precision'), '|', $option, '|',
     $watch->get() === null ? 'D' : 'LIVE';
''', held=False),
}
family.UNSUPPORTED = {}
family.BASELINE = ('CONFIG Iterator unpack key outside integer domain', b'B|G|')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()

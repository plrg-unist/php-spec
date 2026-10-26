#!/usr/bin/env python3
"""A borrowed Aggregate returns a fresh, solely DATA-owned Iterator."""
from pathlib import Path

import global_constant_sources as family


COMMON = br'''<?php
class ConfigFreshAggregateIterator109 implements Iterator {
    public $i = 0;
    public function rewind(): void { echo 'R|'; $this->i = 0; }
    public function valid(): bool { echo 'V', $this->i, '|'; return $this->i < 2; }
    public function current(): mixed {
        global $watch, $option, $value;
        echo 'C', $this->i, '|', $watch->get() === $this ? 'H|' : 'BAD|';
        return $this->i === 0 ? $option : $value;
    }
    public function key(): mixed {
        global $watch, $option, $saved, $throwKey, $invalidKey;
        echo 'K', $this->i, '|', $watch->get() === $this ? 'H|' : 'BAD|';
        if ($this->i === 0) { $option = 'output_buffering'; }
        if ($this->i === 1 && $throwKey) { echo 'T|'; throw $saved; }
        return $this->i === 1 && $invalidKey ? false : $this->i;
    }
    public function next(): void { echo 'N', $this->i, '|'; ++$this->i; }
}
class ConfigFreshAggregate109 implements IteratorAggregate {
    public function getIterator(): Traversable {
        global $watch;
        echo 'G|';
        $it = new ConfigFreshAggregateIterator109;
        $watch = WeakReference::create($it);
        return $it;
    }
}
'''


def source(setup, call):
    return COMMON + setup + br'''
$watch = null; $option = 'precision'; $value = '8';
$aggregate = new ConfigFreshAggregate109; $aggregateHold = $aggregate;
$result = 99; echo 'B|';
''' + call


family.CASES = {
    'fresh-return-normal-sole-data': source(
        br'$throwKey = false; $invalidKey = false; $saved = null;',
        br'''$result = ini_set(...$aggregate);
echo 'A|', $result, '|', ini_get('precision'), '|', $option, '|',
     $watch->get() === null ? 'D' : 'BAD';
'''),
    'fresh-return-key-exception-sole-data': source(
        br"$throwKey = true; $invalidKey = false; $saved = new Exception('fresh-key109');",
        br'''try { $result = ini_set(...$aggregate); echo 'BAD-CALL|'; }
catch (Exception $e) {
    echo $e === $saved ? 'I|' : 'BAD|';
    echo $result, '|', ini_get('precision'), '|', $option, '|',
         $watch->get() === null ? 'D' : 'BAD';
}
echo '|R|', ini_set('precision', '9'), '|', ini_get('precision');
'''),
    'fresh-return-invalid-key-boundary': source(
        br'$throwKey = false; $invalidKey = true; $saved = null;',
        br'''try { $result = ini_set(...$aggregate); echo 'BAD-CALL|'; }
catch (Error $e) {
    echo 'E|', $e->getMessage(), '|', $e->getLine(), '|', $result,
         '|', ini_get('precision'), '|', $option, '|',
         $watch->get() === null ? 'D' : 'BAD';
}
'''),
}
family.UNSUPPORTED = {}
family.BASELINE = ('CONFIG Aggregate return outside shared initialized Iterator domain', b'B|G|')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()

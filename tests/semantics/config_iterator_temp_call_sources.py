#!/usr/bin/env python3
"""A temporary user Iterator factory supplies CONFIG unpack INPUT and DATA."""
from pathlib import Path

import global_constant_sources as family


COMMON = br'''<?php
class ConfigTempIterator101 implements Iterator {
    public $i = 0;
    public function rewind(): void { echo 'R|'; $this->i = 0; }
    public function valid(): bool { echo 'V', $this->i, '|'; return $this->i < 2; }
    public function current(): mixed {
        global $v0, $v1, $watch;
        echo 'C', $this->i, '|', $watch->get() === null ? 'BAD|' : 'H|';
        return $this->i === 0 ? $v0 : $v1;
    }
    public function key(): mixed {
        global $throwKey, $saved;
        echo 'K', $this->i, '|';
        if ($throwKey && $this->i === 1) { echo 'T|'; throw $saved; }
        return $this->i;
    }
    public function next(): void { echo 'N', $this->i, '|'; ++$this->i; }
}
function makeConfigTempIterator101() {
    global $watch, $hold, $retain;
    echo 'P|';
    $it = new ConfigTempIterator101;
    $watch = WeakReference::create($it);
    if ($retain) { $hold = $it; }
    return $it;
}
'''


def source(setup, call):
    return COMMON + setup + br'''
$watch = null; $hold = null; $v0 = 'precision'; $v1 = '8';
$result = 99; echo 'B|';
''' + call


family.CASES = {
    'retained-factory-iterator-drains-before-api': source(
        br'$retain = true; $throwKey = false; $saved = null;',
        br'''$result = ini_set(...makeConfigTempIterator101());
echo 'A|', $result, '|', ini_get('precision'), '|', $hold->i;
echo $watch->get() === null ? '|BAD' : '|H';
'''),
    'sole-factory-iterator-input-retires-before-api': source(
        br'$retain = false; $throwKey = false; $saved = null;',
        br'''$result = ini_set(...makeConfigTempIterator101());
echo 'A|', $result, '|', ini_get('precision');
echo $watch->get() === null ? '|D' : '|BAD';
'''),
    'factory-iterator-key-throw-cancels-api': source(
        br"$retain = false; $throwKey = true; $saved = new Exception('temp-iterator-key101');",
        br'''try { $result = ini_set(...makeConfigTempIterator101()); echo 'BAD-CALL|'; }
catch (Exception $e) {
    echo $e === $saved ? 'I|' : 'BAD|';
    echo $result, '|', ini_get('precision');
    echo $watch->get() === null ? '|D' : '|BAD';
}
'''),
}
family.UNSUPPORTED = {}
family.BASELINE = ('CONFIG Traversable unpack outside initialized Iterator domain', b'B|P|')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()

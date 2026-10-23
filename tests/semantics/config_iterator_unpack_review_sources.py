#!/usr/bin/env python3
"""A supplied key exception cancels CONFIG entry after the current cache."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'selected-config-iterator-key-throw-preserves-unsent-current-and-setter': br'''<?php
class ConfigIteratorReview87 implements Iterator {
    public $i = 0;
    public function rewind(): void { echo 'R|'; $this->i = 0; }
    public function valid(): bool { echo 'V', $this->i, '|'; return $this->i < 2; }
    public function current(): mixed {
        global $call, $effects;
        echo 'C', $this->i, '|'; $effects++;
        if ($this->i === 0) { $call = 'ini_get'; return 'precision'; }
        return '8';
    }
    public function key(): mixed {
        global $saved, $effects;
        echo 'K', $this->i, '|';
        if ($this->i === 1) {
            ini_set('precision', '6'); $effects++;
            $saved = new Exception('config-iterator-before-api87'); throw $saved;
        }
        return 5;
    }
    public function next(): void { echo 'N', $this->i, '|'; $this->i++; }
}
$call = 'InI_SeT'; $keep = $call; $iterator = new ConfigIteratorReview87(); $hold = $iterator;
$effects = 0; $saved = null; $result = 99; echo 'B|';
try { $result = $call(...$iterator); echo 'BAD'; }
catch (Exception $e) {
    echo $e === $saved ? 'I' : 'BAD';
    echo '|', $result, '|', $effects, '|', $call, '|', ini_get('precision');
} finally { echo '|Z'; }
echo '|R|', $keep('precision', '9'), '|', ini_get('precision'), '|', $result;
''',
}
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()

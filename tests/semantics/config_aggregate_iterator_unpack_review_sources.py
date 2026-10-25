#!/usr/bin/env python3
"""A real getIterator exception cancels Iterator DATA and captured CONFIG entry."""
from pathlib import Path

import global_constant_sources as family


family.CASES = {
    'retained-config-aggregate-getiterator-throw-cancels-data-and-api': br'''<?php
class ConfigAggregateUnusedIteratorReview89 implements Iterator {
    public $i = 0;
    public function rewind(): void { echo 'BAD-R|'; $this->i = 0; }
    public function valid(): bool { echo 'BAD-V|'; return $this->i < 2; }
    public function current(): mixed { echo 'BAD-C|'; return $this->i === 0 ? 'precision' : '8'; }
    public function key(): mixed { echo 'BAD-K|'; return $this->i; }
    public function next(): void { echo 'BAD-N|'; ++$this->i; }
}
class ConfigAggregateThrowReview89 implements IteratorAggregate {
    public function getIterator(): Traversable {
        global $call, $saved, $effects;
        echo 'G|'; ++$effects;
        $call = ini_get(...); ini_set('precision', '6');
        $saved = new Exception('config-aggregate-before-iterator89'); throw $saved;
    }
}
$iterator = new ConfigAggregateUnusedIteratorReview89; $iteratorHold = $iterator;
$aggregate = new ConfigAggregateThrowReview89; $aggregateHold = $aggregate;
$call = ini_set(...); $keep = $call; $saved = null; $effects = 0;
$result = 99; echo 'B|';
try {
    $result = $call->__invoke(
        ...$aggregate
    );
    echo 'BAD';
} catch (Exception $e) {
    $trace = $e->getTrace();
    echo $e === $saved ? 'I' : 'BAD';
    echo '|', $result, '|', $effects, '|', ini_get('precision');
    echo '|', $trace[0]['function'], '|', $trace[0]['class'], '|', $trace[0]['type'], '|', $trace[0]['line'], '|';
    echo $trace[0]['args'] === [] ? 'A' : 'BAD';
    echo isset($trace[1]) ? '|BAD' : '|T';
} finally { echo '|Z'; }
echo '|L|', $call('precision'), '|R|', $keep('precision', '9'), '|', ini_get('precision'), '|', $result;
''',
}
family.UNSUPPORTED = {}
family.BASELINE = ('CONFIG Traversable unpack outside initialized Iterator domain', b'B|')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()

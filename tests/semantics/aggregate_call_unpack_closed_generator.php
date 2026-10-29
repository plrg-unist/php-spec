<?php
function closedGenerator126(): Generator { try { echo 'Y|'; yield 17; } finally { echo 'F|'; } }
class ClosedAggregate126 implements IteratorAggregate {
    public function getIterator(): Traversable { global $generator; echo 'G|'; return $generator; }
    public function __destruct() { echo 'D|aggregate|'; }
}
function closedTarget126($value) { echo 'BAD|'; }
$generator = closedGenerator126();
$generator->next();
$aggregate = new ClosedAggregate126();
try { closedTarget126(...$aggregate); }
catch (Exception $error) { echo 'E|', $error->getMessage(), '|'; }
unset($aggregate, $generator);
echo 'Z|';

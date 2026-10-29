<?php
class SelfAggregate126 implements IteratorAggregate {
    public function getIterator(): Traversable { echo 'G|'; return $this; }
    public function __destruct() { echo 'D|aggregate|'; }
}
function selfTarget126() { echo 'BAD|'; }
$aggregate = new SelfAggregate126();
try { selfTarget126(...$aggregate); }
catch (Exception $error) { echo 'E|', $error->getMessage(), '|'; }
unset($aggregate);
echo 'Z|';

<?php
function referenceGenerator126(): Generator { try { echo 'Y|'; yield 'value' => 13; } finally { echo 'F|'; } }
class ReferenceAggregate126 implements IteratorAggregate {
    public function getIterator(): Traversable { echo 'G|'; return referenceGenerator126(); }
    public function __destruct() { echo 'D|aggregate|'; }
}
function &aggregateReference126() { global $aggregate; echo 'S|'; return $aggregate; }
$aggregate = new ReferenceAggregate126();
$function = function ($value) { echo 'H|', $value, '|'; return 41; };
$answer = $function(...aggregateReference126());
echo 'A|', $answer, '|';
unset($aggregate);
echo 'Z|';

<?php
function reboundGenerator126(): Generator { echo 'Y|'; yield 0 => 16; }
class ReboundOther126 implements IteratorAggregate {
    public function getIterator(): Traversable { echo 'BAD|'; return reboundGenerator126(); }
    public function __destruct() { echo 'D|other|'; }
}
class ReboundAggregate126 implements IteratorAggregate {
    public $index = 0;
    public function getIterator(): Traversable {
        global $aggregate;
        echo 'G', $this->index, '|';
        if ($this->index === 0) { ++$this->index; $aggregate = new ReboundOther126(); return $this; }
        return reboundGenerator126();
    }
    public function __destruct() { echo 'D|aggregate|'; }
}
class ReboundTarget126 {
    public function __invoke($value) { echo 'H|', $value, '|'; return 43; }
}
$aggregate = new ReboundAggregate126();
$keep = $aggregate;
$target = new ReboundTarget126();
try { $answer = $target(...$aggregate); echo 'A|', $answer, '|'; }
catch (Exception $error) { echo 'E|', $error->getMessage(), '|'; }
unset($keep, $aggregate);
echo 'Z|';

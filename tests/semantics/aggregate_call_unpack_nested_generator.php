<?php
function nestedGenerator126(): Generator { try { echo 'Y|'; yield 0 => 14; yield 'right' => 15; } finally { echo 'F|'; } }
class InnerAggregate126 implements IteratorAggregate {
    public function getIterator(): Traversable { echo 'G|inner|'; return nestedGenerator126(); }
    public function __destruct() { echo 'D|inner|'; }
}
class OuterAggregate126 implements IteratorAggregate {
    public function getIterator(): Traversable { echo 'G|outer|'; return new InnerAggregate126(); }
    public function __destruct() { echo 'D|outer|'; }
}
class NestedReceiver126 {
    public function take($left, $right) { echo 'H|', $left, '|', $right, '|'; return 42; }
    public function __destruct() { echo 'D|receiver|'; }
}
$receiver = new NestedReceiver126();
$function = [$receiver, 'take'];
$answer = $function(...new OuterAggregate126());
echo 'A|', $answer, '|';
unset($function, $receiver);
echo 'Z|';

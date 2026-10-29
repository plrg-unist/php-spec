<?php
class GetterPayload126 { public function __destruct() { echo 'D|prefix|'; } }
class ThrowAggregate126 implements IteratorAggregate {
    public function getIterator(): Traversable { global $receiver, $exception; echo 'G|'; $receiver = null; throw $exception; }
    public function __destruct() { echo 'D|aggregate|'; }
}
class ThrowReceiver126 {
    public function take($value) { echo 'BAD|'; }
    public function __destruct() { echo 'D|receiver|'; }
}
$exception = new Exception('supplied');
$receiver = new ThrowReceiver126();
$answer = 44;
try { $answer = $receiver->take(new GetterPayload126(), ...new ThrowAggregate126()); }
catch (Exception $error) { echo 'E|', $error === $exception ? 1 : 0, '|', $answer, '|'; }
echo 'Z|';

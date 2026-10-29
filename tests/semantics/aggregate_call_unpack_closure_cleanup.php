<?php
class ClosureCapture126 { public function __destruct() { echo 'D|capture|'; } }
class ClosurePositional126 { public function __destruct() { echo 'D|positional|'; } }
class ClosureNamed126 { public function __destruct() { echo 'D|named|'; } }
class ClosureThrowAggregate126 implements IteratorAggregate {
    public function getIterator(): Traversable {
        global $function, $capture, $exception;
        echo 'G|';
        $function = null;
        $capture = null;
        throw $exception;
    }
    public function __destruct() { echo 'D|aggregate|'; }
}
$exception = new Exception('supplied');
$capture = new ClosureCapture126();
$function = function ($positional, ...$arguments) use ($capture) { echo 'BAD|'; };
try { $function(...[new ClosurePositional126(), 'named' => new ClosureNamed126()], ...new ClosureThrowAggregate126()); }
catch (Exception $error) { echo 'E|', $error === $exception ? 1 : 0, '|'; }
echo 'Z|';

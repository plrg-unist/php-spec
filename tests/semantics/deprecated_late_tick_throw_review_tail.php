<?php
class ThrowTick19First {
    public function __destruct() { echo 'A;'; throw new Exception('tick-arg-failure'); }
}
class ThrowTick19Later { public function __destruct() { echo 'L;'; } }
class ThrowTick19TailArg { public function __destruct() { echo 'U;'; } }
class ThrowTick19Caller {
    public function __invoke(...$args) { echo 'BAD-CALL;'; }
    public function __destruct() { echo 'C;'; }
}
class ThrowTick19TailCaller {
    public function __invoke(...$args) { echo 'BAD-CALL;'; }
    public function __destruct() { echo 'T;'; }
}
function throw_review_tail_final($bytes, $phase) {
    $callback = new ThrowTick19Caller(); $throwing = new ThrowTick19First();
    $later = new ThrowTick19Later(); $tail = new ThrowTick19TailCaller();
    $tail_arg = new ThrowTick19TailArg();
    register_tick_function($callback, $throwing, $later);
    register_tick_function($tail, $tail_arg);
    $callback = null; $throwing = null; $later = null; $tail = null; $tail_arg = null;
    return $bytes . 'F;';
}
ob_start('throw_review_tail_final');
echo 'B;';

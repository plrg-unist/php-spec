<?php
class ExitThrow20First {
    public function __destruct() { echo 'A;'; throw new Exception('exit7-tick-failure'); }
}
class ExitThrow20Later { public function __destruct() { echo 'L;'; } }
class ExitThrow20TailArg { public function __destruct() { echo 'U;'; } }
class ExitThrow20QueueArg { public function __destruct() { echo 'Q;'; } }
class ExitThrow20Caller {
    public function __invoke(...$args) { echo 'BAD-CALL;'; }
    public function __destruct() { echo 'C;'; }
}
class ExitThrow20TailCaller {
    public function __invoke(...$args) { echo 'BAD-CALL;'; }
    public function __destruct() { echo 'T;'; }
}
function exit_throw20_never($arg) { echo 'BAD-SHUTDOWN;'; }
function exit_throw_review_tail_final($bytes, $phase) {
    $queue_arg = new ExitThrow20QueueArg();
    $callback = new ExitThrow20Caller(); $throwing = new ExitThrow20First();
    $later = new ExitThrow20Later(); $tail = new ExitThrow20TailCaller();
    $tail_arg = new ExitThrow20TailArg();
    register_shutdown_function('exit_throw20_never', $queue_arg);
    register_tick_function($callback, $throwing, $later);
    register_tick_function($tail, $tail_arg);
    $queue_arg = null; $callback = null; $throwing = null; $later = null;
    $tail = null; $tail_arg = null;
    return $bytes . 'F;';
}
ob_start('exit_throw_review_tail_final');
echo 'B;';
exit(7);

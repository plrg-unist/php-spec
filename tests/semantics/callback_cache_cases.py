"""Native-first persistent callback caches and inline tick retirement."""


def tick_closure(throwing=False):
    argument_tail = 'throw $GLOBALS["saved"];' if throwing else ''
    prefix = r'''<?php
$calls = 0;
class TickCacheCapture {
    public function __destruct() {
        echo "C:", $GLOBALS["weak_arg"]->get() === null, ":", $GLOBALS["weak_cb"]->get() === null, ":", $GLOBALS["weak_recv"]->get() !== null, ";";
    }
}
class TickCacheArgument {
    public function __destruct() {
        echo "T:", $GLOBALS["weak_cb"]->get() !== null, ":", $GLOBALS["weak_recv"]->get() !== null, ":", $GLOBALS["weak_capture"]->get() !== null, ":", $GLOBALS["calls"] === 1, ";";
        ARGUMENT_TAIL
    }
}
class TickCacheReceiver {
    public function make($captured) {
        return #[\NoDiscard] function ($argument) use ($captured) {
            $GLOBALS["calls"]++;
            echo "B:", $GLOBALS["weak_cb"]->get() !== null, ":", $GLOBALS["weak_recv"]->get() === $this, ":", $GLOBALS["weak_capture"]->get() === $captured, ":", $GLOBALS["weak_arg"]->get() === $argument, ";";
            return 7;
        };
    }
    public function __destruct() {
        echo "R:", $GLOBALS["weak_arg"]->get() === null, ":", $GLOBALS["weak_capture"]->get() === null, ":", $GLOBALS["weak_cb"]->get() === null, ";";
    }
}
$receiver = new TickCacheReceiver(); $capture = new TickCacheCapture();
$callback = $receiver->make($capture); $argument = new TickCacheArgument();
$weak_recv = WeakReference::create($receiver); $weak_capture = WeakReference::create($capture);
$weak_cb = WeakReference::create($callback); $weak_arg = WeakReference::create($argument);
register_tick_function($callback, $argument);
$receiver = null; $capture = null; $callback = null; $argument = null;
echo "P:", $weak_cb->get() !== null, ":", $weak_recv->get() !== null, ":", $weak_capture->get() !== null, ":", $weak_arg->get() !== null, ";";
declare(ticks=1) { $marker = 1; }
echo "Q:", $calls === 1, ";";
'''.replace('ARGUMENT_TAIL', argument_tail)
    tail = r'''
echo "E:", $calls === 1, ":", $weak_cb->get() === null, ":", $weak_recv->get() === null, ":", $weak_capture->get() === null, ":", $weak_arg->get() === null, ";";
'''
    if throwing:
        prefix = prefix.replace('$calls = 0;', '$calls = 0; $saved = new Exception("raw arg");', 1)
        tail = r'''
echo "E:", $caught === 1, ":", $calls === 1, ":", $weak_cb->get() === null, ":", $weak_recv->get() === null, ":", $weak_capture->get() === null, ":", $weak_arg->get() === null, ";";
'''
        call = r'''$caught = 0;
try { unregister_tick_function($weak_cb->get()); }
catch (Throwable $error) {
    $caught = 1;
    echo "X:", $error === $saved, ":", $weak_cb->get() === null, ":", $weak_recv->get() === null, ":", $weak_capture->get() === null, ":", $weak_arg->get() === null, ";";
}
'''
    else:
        call = 'unregister_tick_function($weak_cb->get());\n'
    return (prefix + call + tail).encode()


def shutdown_retention():
    return br'''<?php
class ShutdownCacheReceiver {
    public function make($snapshot) {
        return #[\NoDiscard] function () use ($snapshot) {
            echo "B:", $snapshot === 7, ":", $GLOBALS["weak_recv"]->get() === $this, ":", $GLOBALS["weak_cb"]->get() !== null, ";";
            return 7;
        };
    }
}
function last_callback() {
    echo "S:", $GLOBALS["weak_cb"]->get() !== null, ":", $GLOBALS["weak_recv"]->get() !== null, ";";
}
$receiver = new ShutdownCacheReceiver(); $callback = $receiver->make(7);
$weak_recv = WeakReference::create($receiver); $weak_cb = WeakReference::create($callback);
$observe_cb = $weak_cb; $observe_recv = $weak_recv;
$finalizer = function ($buffer, $phase) use (&$observe_cb, &$observe_recv) {
    $result = $buffer . "F:" . ($phase === 9) . ":" . ($observe_cb->get() !== null) . ":" . ($observe_recv->get() !== null) . ";";
    $observe_cb = null; $observe_recv = null;
    $GLOBALS["weak_cb"] = null; $GLOBALS["weak_recv"] = null;
    return $result;
};
register_shutdown_function($callback); register_shutdown_function("last_callback");
$receiver = null; $callback = null;
ob_start($finalizer); $finalizer = null;
echo "P:", $weak_cb->get() !== null, ":", $weak_recv->get() !== null, ";";
'''


CASES = {
    'tick-bound-closure-cache-and-ordered-unregister': tick_closure(),
    'tick-raw-argument-throw-keeps-cached-callable-retirement': tick_closure(True),
    'shutdown-bound-closure-cache-and-captured-final-observers': shutdown_retention(),
}
EXPECTED_STDOUT = {
    'tick-bound-closure-cache-and-ordered-unregister': b'P:1:1:1:1;B:1:1:1:1;Q:1;T:1:1:1:1;C:1:1:1;R:1:1:1;E:1:1:1:1:1;',
    'tick-raw-argument-throw-keeps-cached-callable-retirement': b'P:1:1:1:1;B:1:1:1:1;Q:1;T:1:1:1:1;C:1:1:1;R:1:1:1;X:1:1:1:1:1;E:1:1:1:1:1:1;',
    'shutdown-bound-closure-cache-and-captured-final-observers': b'P:1:1;B:1:1:1;S:1:1;F:1:1:1;',
}
EXIT_CODES = {name: 0 for name in CASES}


def expected_stderr(name, path):
    return b''

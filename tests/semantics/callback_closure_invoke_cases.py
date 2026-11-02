"""Native-first tick calls through a cached Closure::__invoke wrapper."""
from deprecated_closure_invoke_review_cases import at80


CASES = {
    'tick-invoke-reference-warning-between-outer-and-inner': at80([
        '#[\\Deprecated, \\NoDiscard]',
        'function tick_reference_target(&$value) { $GLOBALS["body"]++; echo "B:", $value === 7, ":", $GLOBALS["calls"] === 3, ";"; $value = 9; return 7; }',
        'function reference_notice($level, $message, $file, $line) {',
        '    $GLOBALS["calls"]++;',
        '    if ($level === 8192) { echo "O:", $GLOBALS["calls"] === 1, ":", $message === "Method Closure::__invoke() is deprecated", ";"; return true; }',
        '    if ($level === 2) { echo "W:", $GLOBALS["calls"] === 2, ":", $message === \'Closure::__invoke(): Argument #1 ($value) must be passed by reference, value given\', ":", $file === __FILE__ && $line === 80, ";"; return true; }',
        '    if ($level === 16384) { echo "I:", $GLOBALS["calls"] === 3, ":", $message === "Function tick_reference_target() is deprecated", ";"; return true; }',
        '    echo "BAD-WARNING;"; return true;',
        '}',
        '$calls = 0; $body = 0; $input = 7; $alias =& $input; $callback = tick_reference_target(...);',
        '$weak_cb = WeakReference::create($callback); register_tick_function([$callback, "__invoke"], $alias); $callback = null;',
        'set_error_handler("reference_notice");',
    ], 'declare(ticks=1) { $marker = 1; }', [
        'restore_error_handler(); unregister_tick_function([$weak_cb->get(), "__invoke"]);',
        'echo "E:", $body === 1, ":", $calls === 3, ":", $input === 7 && $alias === 7, ":", $weak_cb->get() === null, ";";',
    ]),
    'tick-invoke-warning-phases-weak-receive-and-unused-result': at80([
        'declare(strict_types=1);',
        'class TickInvokeArgument {}',
        'class TickInvokeValue {',
        '    public function __destruct() { echo "V:", $GLOBALS["body"] === 1, ":", $GLOBALS["calls"] === 2, ":", $GLOBALS["weak_cb"]->get() !== null, ":", $GLOBALS["weak_recv"]->get() !== null, ";"; }',
        '}',
        'class TickInvokeOwner {',
        '    #[\\Deprecated("cached", "19"), \\NoDiscard]',
        '    public function act(#[\\SensitiveParameter] int $value, $argument) {',
        '        $GLOBALS["body"]++; $trace = (new Exception("body"))->getTrace();',
        '        echo "B:", $value === 7, ":", $GLOBALS["weak_cb"]->get() !== null, ":", $GLOBALS["weak_recv"]->get() === $this, ":", $GLOBALS["calls"] === 2, ":", $trace[0]["args"][0] instanceof SensitiveParameterValue && $trace[0]["args"][0]->getValue() === 7, ":", $trace[1]["args"][0] instanceof SensitiveParameterValue && $trace[1]["args"][0]->getValue() === "7", ":", $trace[0]["file"] === __FILE__ && $trace[0]["line"] === 80, ":", $trace[1]["file"] === __FILE__ && $trace[1]["line"] === 80, ":", $trace[1]["function"] === "__invoke" && $trace[1]["class"] === "Closure", ":", $trace[0]["args"][0] !== $trace[1]["args"][0], ";"; $trace = null;',
        '        $result = new TickInvokeValue(); $GLOBALS["weak_result"] = WeakReference::create($result); return $result;',
        '    }',
        '    public function __destruct() { echo "R:", $GLOBALS["weak_cb"]->get() === null, ":", $GLOBALS["weak_result"]->get() === null, ":", $GLOBALS["body"] === 1, ";"; }',
        '}',
        'function tick_notice($level, $message, $file, $line) {',
        '    $GLOBALS["calls"]++;',
        '    if ($level === 8192) { echo "O:", $message === "Method Closure::__invoke() is deprecated since 19, cached", ":", $file === __FILE__ && $line === 80, ":", $GLOBALS["body"] === 0, ":", $GLOBALS["weak_cb"]->get() !== null, ";"; return true; }',
        '    if ($level === 16384) { echo "I:", $message === "Method TickInvokeOwner::act() is deprecated since 19, cached", ":", $file === __FILE__ && $line === 80, ":", $GLOBALS["body"] === 0, ":", $GLOBALS["weak_recv"]->get() !== null, ";"; return true; }',
        '    echo "BAD-WARNING;"; return true;',
        '}',
        '$calls = 0; $body = 0; $receiver = new TickInvokeOwner(); $callback = $receiver->act(...);',
        '$weak_recv = WeakReference::create($receiver); $weak_cb = WeakReference::create($callback);',
        '$argument = new TickInvokeArgument(); $weak_arg = WeakReference::create($argument);',
        'register_tick_function([$callback, "__invoke"], "7", $argument); $callback = null; $receiver = null; $argument = null;',
        'set_error_handler("tick_notice");',
    ], 'declare(ticks=1) { $marker = 1; }', [
        'restore_error_handler(); echo "Q:", $body === 1, ":", $calls === 2, ":", $weak_result->get() === null, ";";',
        'unregister_tick_function([$weak_cb->get(), "__invoke"]);',
        'echo "E:", $body === 1, ":", $calls === 2, ":", $weak_cb->get() === null, ":", $weak_recv->get() === null, ";";',
    ]),
    'tick-invoke-outer-throw-before-raw-copy-keeps-cache': at80([
        'class TickOuterArgument {',
        '    public function __destruct() { echo "T:", $GLOBALS["weak_cb"]->get() !== null, ":", $GLOBALS["weak_recv"]->get() !== null, ";"; }',
        '}',
        'class TickOuterOwner {',
        '    #[\\Deprecated, \\NoDiscard]',
        '    public function act($argument) { $GLOBALS["body"]++; echo "BAD-BODY;"; return 7; }',
        '    public function __destruct() { echo "R:", $GLOBALS["weak_cb"]->get() === null, ":", $GLOBALS["weak_arg"]->get() === null, ";"; }',
        '}',
        'function outer_notice($level, $message, $file, $line) {',
        '    $GLOBALS["calls"]++;',
        '    echo "O:", $level === 8192, ":", $message === "Method Closure::__invoke() is deprecated", ":", $GLOBALS["body"] === 0, ":", $GLOBALS["weak_arg"]->get() !== null, ":", $GLOBALS["weak_cb"]->get() !== null, ";";',
        '    throw $GLOBALS["saved"];',
        '}',
        '$calls = 0; $body = 0; $saved = new Exception("outer");',
        '$receiver = new TickOuterOwner(); $callback = $receiver->act(...); $argument = new TickOuterArgument();',
        '$weak_recv = WeakReference::create($receiver); $weak_cb = WeakReference::create($callback); $weak_arg = WeakReference::create($argument);',
        'register_tick_function([$callback, "__invoke"], $argument); $callback = null; $receiver = null; $argument = null;',
        'set_error_handler("outer_notice");',
    ], 'try { declare(ticks=1) { $marker = 1; } } catch (Exception $caught) { echo "C:", $caught === $saved, ":", $calls === 1, ":", $body === 0, ":", $weak_cb->get() !== null, ":", $weak_recv->get() !== null, ":", $weak_arg->get() !== null, ":", $caught->getPrevious() === null, ";"; }', [
        'restore_error_handler(); unregister_tick_function([$weak_cb->get(), "__invoke"]);',
        'echo "E:", $body === 0, ":", $calls === 1, ":", $weak_cb->get() === null, ":", $weak_recv->get() === null, ":", $weak_arg->get() === null, ";";',
    ]),
}

EXPECTED_STDOUT = {
    'tick-invoke-reference-warning-between-outer-and-inner': b'O:1:1;W:1:1:1;I:1:1;B:1:1;E:1:1:1:1;',
    'tick-invoke-warning-phases-weak-receive-and-unused-result': b'O:1:1:1:1;I:1:1:1:1;B:1:1:1:1:1:1:1:1:1:1;V:1:1:1:1;Q:1:1:1;R:1:1:1;E:1:1:1:1;',
    'tick-invoke-outer-throw-before-raw-copy-keeps-cache': b'O:1:1:1:1:1;C:1:1:1:1:1:1:1;T:1:1;R:1:1;E:1:1:1:1:1;',
}
EXIT_CODES = {name: 0 for name in CASES}


def expected_stderr(name, path):
    return b''

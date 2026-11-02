"""Independent raw-wrapper trace and inner-warning cancellation witness."""
from deprecated_closure_invoke_review_cases import at80


CASES = {
    'tick-invoke-inner-throw-keeps-raw-wrapper-and-persistent-cache': at80([
        'class TickInnerArgument {',
        '    public function __destruct() { echo "T:", $GLOBALS["body"] === 0, ":", $GLOBALS["calls"] === 2, ":", $GLOBALS["weak_cb"]->get() !== null, ";"; }',
        '}',
        '#[\\Deprecated("raw", "29"), \\NoDiscard]',
        'function tick_inner_target(int $value, TickInnerArgument $argument) { $GLOBALS["body"]++; echo "BAD-BODY;"; return 7; }',
        'function inner_notice($level, $message, $file, $line) {',
        '    $GLOBALS["calls"]++;',
        '    if ($level === 8192) {',
        '        $trace = (new Exception("outer view"))->getTrace();',
        '        echo "O:", $message === "Method Closure::__invoke() is deprecated since 29, raw", ":", $file === __FILE__ && $line === 80, ":", !isset($trace[1]), ":", $GLOBALS["body"] === 0, ":", $GLOBALS["weak_cb"]->get() !== null, ":", $GLOBALS["weak_arg"]->get() !== null, ";";',
        '        return true;',
        '    }',
        '    if ($level === 16384) {',
        '        $error = new Exception("inner"); $GLOBALS["saved"] = $error; $trace = $error->getTrace();',
        '        $raw = $trace[1]["args"][0]; $raw_token = $trace[1]["args"][1];',
        '        echo "I:", $message === "Function tick_inner_target() is deprecated since 29, raw", ":", $file === __FILE__ && $line === 80, ":", $trace[0]["function"] === "inner_notice", ":", $trace[1]["function"] === "__invoke" && $trace[1]["class"] === "Closure" && $trace[1]["type"] === "->", ":", $raw === "7", ":", $raw_token === $GLOBALS["weak_arg"]->get(), ":", $GLOBALS["body"] === 0, ":", $GLOBALS["calls"] === 2, ":", !isset($trace[2]), ";";',
        '        throw $error;',
        '    }',
        '    echo "BAD-WARNING;"; return true;',
        '}',
        '$calls = 0; $body = 0; $saved = null; $callback = tick_inner_target(...); $argument = new TickInnerArgument();',
        '$weak_cb = WeakReference::create($callback); $weak_arg = WeakReference::create($argument);',
        'register_tick_function([$callback, "__invoke"], "7", $argument); $callback = null; $argument = null;',
        'echo "P:", $weak_cb->get() !== null, ":", $weak_arg->get() !== null, ";";',
        'set_error_handler("inner_notice");',
    ], 'try { declare(ticks=1) { $marker = 1; } } catch (Exception $caught) { echo "C:", $caught === $saved, ":", $calls === 2, ":", $body === 0, ":", $weak_cb->get() !== null, ":", $weak_arg->get() !== null, ":", $caught->getPrevious() === null, ";"; }', [
        'restore_error_handler(); $caught = null; $saved = null;',
        'echo "Q:", $body === 0, ":", $calls === 2, ":", $weak_cb->get() !== null, ":", $weak_arg->get() !== null, ";";',
        'unregister_tick_function([$weak_cb->get(), "__invoke"]);',
        'echo "E:", $weak_cb->get() === null, ":", $weak_arg->get() === null, ":", $calls === 2, ":", $body === 0, ";";',
    ]),
}

EXPECTED_STDOUT = {
    'tick-invoke-inner-throw-keeps-raw-wrapper-and-persistent-cache': b'P:1:1;O:1:1:1:1:1:1;I:1:1:1:1:1:1:1:1:1;C:1:1:1:1:1:1;Q:1:1:1:1;T:1:1:1;E:1:1:1:1;',
}
EXIT_CODES = {name: 0 for name in CASES}


def expected_stderr(name, path):
    return b''

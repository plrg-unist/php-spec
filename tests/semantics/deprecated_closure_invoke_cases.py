"""Native-first explicit Closure wrapper warning phases and prepared owners."""
from deprecated_cases import at60


CASES = {
    'explicit-wrapper-positional-before-type-reception': at60([
        '#[\\Deprecated("old", "9"), \\NoDiscard]',
        'function captured(int $value) { echo "BAD-B;"; return 7; }',
        'function notice($level, $message, $file, $line) {',
        '    $GLOBALS["calls"]++; $trace = (new Exception("trace"))->getTrace();',
        '    if ($GLOBALS["calls"] === 1) {',
        '        $GLOBALS["arg"] = 8;',
        '        echo "W:", $level === 8192, ":", $message === "Method Closure::__invoke() is deprecated since 9, old", ":", $file === __FILE__, ":", $line === 60, ":", !isset($trace[1]), ";";',
        '    } else {',
        '        echo "U:", $level === 16384, ":", $message === "Function captured() is deprecated since 9, old", ":", $file === __FILE__, ":", $line === 60, ":", $trace[1]["function"] === "__invoke", ":", $trace[1]["class"] === "Closure", ":", $trace[1]["args"][0] === "bad", ";";',
        '    }',
        '    return true;',
        '}',
        '$calls = 0; $arg = "bad"; $closure = captured(...); set_error_handler("notice");',
        'try {',
    ], '    $closure->__invoke($arg);', [
        '    echo "BAD-R;";',
        '} catch (TypeError $caught) {',
        '    echo "C:", $calls === 2, ":", $arg === 8, ":", $caught->getLine() === 3, ":", $caught->getMessage() === "captured(): Argument #1 (\\$value) must be of type int, string given", ":", $caught->getPrevious() === null, ";";',
        '}',
        'restore_error_handler();',
    ]),
    'explicit-wrapper-outer-throw-releases-raw-owners': at60([
        'class Token { public function __destruct() { echo "T;"; } }',
        'class Owner {',
        '    #[\\Deprecated, \\NoDiscard]',
        '    public function act($value) { echo "BAD-B;"; return 7; }',
        '    public function __destruct() { echo "O;"; }',
        '}',
        'function notice($level, $message, $file, $line) {',
        '    $GLOBALS["calls"]++; $GLOBALS["closure"] = null; $GLOBALS["token"] = null;',
        '    echo "W:", $level === 8192, ":", $message === "Method Closure::__invoke() is deprecated", ":", $GLOBALS["weak_closure"]->get() !== null, ":", $GLOBALS["weak_owner"]->get() !== null, ":", $GLOBALS["weak_token"]->get() !== null, ";";',
        '    throw $GLOBALS["saved"];',
        '}',
        '$owner = new Owner(); $weak_owner = WeakReference::create($owner);',
        '$closure = $owner->act(...); $weak_closure = WeakReference::create($closure); $owner = null;',
        '$token = new Token(); $weak_token = WeakReference::create($token);',
        '$calls = 0; $saved = new Exception("supplied"); set_error_handler("notice");',
        'try {',
    ], '    $closure->__invoke($token);', [
        '    echo "BAD-R;";',
        '} catch (Exception $caught) {',
        '    echo "C:", $caught === $saved, ":", $calls === 1, ":", $weak_closure->get() === null, ":", $weak_owner->get() === null, ":", $weak_token->get() === null, ":", $caught->getPrevious() === null, ";";',
        '}',
        'restore_error_handler();',
    ]),
    'explicit-wrapper-required-named-hole-before-error': at60([
        '#[\\Deprecated, \\NoDiscard]',
        'function captured($first, $second) { echo "BAD-B;"; return 7; }',
        'function notice($level, $message, $file, $line) {',
        '    $GLOBALS["calls"]++;',
        '    if ($GLOBALS["calls"] === 1) {',
        '        echo "W:", $level === 8192, ":", $message === "Method Closure::__invoke() is deprecated", ":", $line === 60, ";";',
        '    } else {',
        '        echo "U:", $level === 16384, ":", $message === "Function captured() is deprecated", ":", $line === 60, ";";',
        '    }',
        '    return true;',
        '}',
        '$calls = 0; $closure = captured(...); set_error_handler("notice");',
        'try {',
    ], '    $closure->__invoke(second: 2);', [
        '    echo "BAD-R;";',
        '} catch (ArgumentCountError $caught) {',
        '    echo "C:", $calls === 2, ":", $caught->getMessage() === \'captured(): Argument #1 ($first) not passed\', ":", $caught->getLine() === 3, ":", $caught->getPrevious() === null, ";";',
        '}',
        'restore_error_handler();',
    ]),
}

EXPECTED_STDOUT = {
    'explicit-wrapper-positional-before-type-reception': b'W:1:1:1:1:1;U:1:1:1:1:1:1:1;C:1:1:1:1:1;',
    'explicit-wrapper-outer-throw-releases-raw-owners': b'W:1:1:1:1:1;T;O;C:1:1:1:1:1:1;',
    'explicit-wrapper-required-named-hole-before-error': b'W:1:1:1;U:1:1:1;C:1:1:1:1;',
}
EXIT_CODES = {name: 0 for name in CASES}


def expected_stderr(name, path):
    return b''

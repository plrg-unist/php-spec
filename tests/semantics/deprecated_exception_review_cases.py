"""Independent frozen Deprecated exception-handler source witnesses."""


def at80(prefix, operation, suffix=()):
    lines = ['<?php'] + prefix
    assert len(lines) <= 79
    lines += [''] * (79 - len(lines)) + [operation] + list(suffix)
    assert lines[79] == operation
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'deprecated-warning-throw-reenters-replacement-then-original': at80([
        '#[\\Deprecated("early", "9"), \\NoDiscard]',
        'function selected_terminal($error) {',
        '    $GLOBALS["body"]++; echo "B:", $error === $GLOBALS["weak_original"]->get(), ":", get_exception_handler() === "replacement", ";"; return 7;',
        '}',
        'function replacement($error) {',
        '    $GLOBALS["replacement"]++; echo "R:", $error === $GLOBALS["saved"], ":", get_exception_handler() === null, ":", $GLOBALS["weak_original"]->get() !== null, ";";',
        '}',
        'function notice($level, $message, $file, $line) {',
        '    $GLOBALS["deprecated"]++;',
        '    echo "D:", $level === 16384 && $message === "Function selected_terminal() is deprecated since 9, early", ":", $file === "Unknown" && $line === 0, ":", get_exception_handler() === null, ";";',
        '    set_exception_handler("replacement"); throw $GLOBALS["saved"];',
        '}',
        'function raise_original() { $error = new Exception("original"); $GLOBALS["weak_original"] = WeakReference::create($error); throw $error; }',
        'function finish() {',
        '    echo "E:", $GLOBALS["body"] === 1, ":", $GLOBALS["deprecated"] === 1, ":", $GLOBALS["replacement"] === 1, ":", $GLOBALS["weak_original"]->get() === null, ":", get_exception_handler() === "replacement", ";";',
        '    $GLOBALS["saved"] = null; echo "S:", $GLOBALS["weak_saved"]->get() === null, ";";',
        '}',
        '$body = 0; $deprecated = 0; $replacement = 0; $saved = new Exception("supplied"); $weak_saved = WeakReference::create($saved);',
        'register_shutdown_function("finish"); set_error_handler("notice"); set_exception_handler("selected_terminal");',
    ], 'raise_original();'),
    'deprecated-byref-selected-target-and-fresh-throwable-slot': at80([
        '#[\\Deprecated("reference", "10"), \\NoDiscard]',
        'function fresh_terminal(&$error) {',
        '    $GLOBALS["body"]++; echo "B:", $error === $GLOBALS["weak_original"]->get(), ":", get_exception_handler() === "replacement", ";";',
        '    $fresh = new Exception("fresh"); $GLOBALS["weak_fresh"] = WeakReference::create($fresh); $error = $fresh;',
        '    echo "F:", $GLOBALS["weak_original"]->get() !== null, ":", $error === $GLOBALS["weak_fresh"]->get(), ";"; return 7;',
        '}',
        'function replacement($error) { echo "BAD-REPLACEMENT;"; }',
        'function notice($level, $message, $file, $line) {',
        '    if ($level === 16384) {',
        '        $GLOBALS["deprecated"]++; echo "D:", $message === "Function fresh_terminal() is deprecated since 10, reference", ":", get_exception_handler() === null, ";"; return true;',
        '    }',
        '    $GLOBALS["warnings"]++; set_exception_handler("replacement");',
        '    echo "W:", $level === 2 && $message === \'fresh_terminal(): Argument #1 ($error) must be passed by reference, value given\', ":", $file === "Unknown" && $line === 0, ":", $GLOBALS["weak_original"]->get() !== null, ";"; return true;',
        '}',
        'function raise_original() { $error = new Exception("original"); $GLOBALS["weak_original"] = WeakReference::create($error); throw $error; }',
        'function finish() { echo "E:", $GLOBALS["body"] === 1, ":", $GLOBALS["deprecated"] === 1, ":", $GLOBALS["warnings"] === 1, ":", $GLOBALS["weak_original"]->get() === null, ":", $GLOBALS["weak_fresh"]->get() === null, ":", get_exception_handler() === "replacement", ";"; }',
        '$body = 0; $deprecated = 0; $warnings = 0;',
        'register_shutdown_function("finish"); set_error_handler("notice"); set_exception_handler("fresh_terminal");',
    ], 'raise_original();'),
    'deprecated-closure-retained-entry-and-registry-retirement': at80([
        'class CachedTerminal {',
        '    #[\\Deprecated("cached", "11"), \\NoDiscard]',
        '    public function retired($error) {',
        '        $GLOBALS["body"]++; echo "B:", $error === $GLOBALS["weak_original"]->get(), ":", $GLOBALS["weak_closure"]->get() !== null, ":", $GLOBALS["weak_receiver"]->get() === $this, ";"; return 7;',
        '    }',
        '    public function __destruct() { echo "X:", $GLOBALS["body"] === 1, ";"; }',
        '}',
        'function notice($level, $message, $file, $line) {',
        '    echo "D:", $level === 16384 && $message === "Method CachedTerminal::retired() is deprecated since 11, cached", ":", get_exception_handler() === null, ":", $GLOBALS["weak_closure"]->get() !== null, ";"; return true;',
        '}',
        'function raise_original() { $error = new Exception("original"); $GLOBALS["weak_original"] = WeakReference::create($error); throw $error; }',
        'function finish() {',
        '    echo "S:", $GLOBALS["weak_original"]->get() === null, ":", $GLOBALS["weak_closure"]->get() !== null, ":", get_exception_handler() === $GLOBALS["weak_closure"]->get(), ";";',
        '    restore_exception_handler(); echo "E:", $GLOBALS["weak_closure"]->get() === null, ":", $GLOBALS["weak_receiver"]->get() === null, ":", get_exception_handler() === null, ";";',
        '}',
        '$body = 0; $receiver = new CachedTerminal(); $callback = $receiver->retired(...);',
        '$weak_closure = WeakReference::create($callback); $weak_receiver = WeakReference::create($receiver);',
        'register_shutdown_function("finish"); set_error_handler("notice"); set_exception_handler($callback); $callback = null; $receiver = null;',
    ], 'raise_original();'),
}

EXPECTED_STDOUT = {
    'deprecated-warning-throw-reenters-replacement-then-original': b'D:1:1:1;R:1:1:1;B:1:1;E:1:1:1:1:1;S:1;',
    'deprecated-byref-selected-target-and-fresh-throwable-slot': b'D:1:1;W:1:1:1;B:1:1;F:1:1;E:1:1:1:1:1:1;',
    'deprecated-closure-retained-entry-and-registry-retirement': b'D:1:1:1;B:1:1:1;S:1:1:1;X:1;E:1:1:1;',
}
EXIT_CODES = {name: 0 for name in CASES}


def expected_stderr(name, source):
    return b''

PREFIX = [
    'class RetiringTerminal {',
    '    #[\\Deprecated("retiring", "13"), \\NoDiscard]',
    '    public function retired($error) {',
    '        $GLOBALS["body"]++; echo "B:", $error === $GLOBALS["weak_original"]->get(), ":", $GLOBALS["weak_closure"]->get() !== null, ":", $GLOBALS["weak_receiver"]->get() === $this, ";";',
    '        restore_exception_handler(); restore_exception_handler();',
    '        echo "K:", $GLOBALS["weak_closure"]->get() !== null, ":", $GLOBALS["weak_receiver"]->get() === $this, ":", get_exception_handler() === null, ";"; return 7;',
    '    }',
    '    public function __destruct() { echo "X:", $GLOBALS["body"] === 1, ":", $GLOBALS["weak_original"]->get() !== null, ";"; }',
    '}',
    'function notice($level, $message, $file, $line) {',
    '    echo "D:", $level === 16384 && $message === "Method RetiringTerminal::retired() is deprecated since 13, retiring", ":", get_exception_handler() === null, ":", $GLOBALS["weak_closure"]->get() !== null, ";"; return true;',
    '}',
    'function raise_original() { $error = new Exception("original"); $GLOBALS["weak_original"] = WeakReference::create($error); throw $error; }',
    'function finish() { echo "E:", $GLOBALS["weak_original"]->get() === null, ":", $GLOBALS["weak_closure"]->get() === null, ":", $GLOBALS["weak_receiver"]->get() === null, ":", get_exception_handler() === null, ";"; }',
    '$body = 0; $receiver = new RetiringTerminal(); $callback = $receiver->retired(...);',
    '$weak_closure = WeakReference::create($callback); $weak_receiver = WeakReference::create($receiver);',
    'register_shutdown_function("finish"); set_error_handler("notice"); set_exception_handler($callback); $callback = null; $receiver = null;',
]
CASES['exception-closure-body-drop-preserves-call-retain'] = at80(PREFIX, 'raise_original();')
EXPECTED_STDOUT['exception-closure-body-drop-preserves-call-retain'] = b'D:1:1:1;B:1:1:1;K:1:1:1;X:1:1;E:1:1:1:1;'
EXIT_CODES['exception-closure-body-drop-preserves-call-retain'] = 0

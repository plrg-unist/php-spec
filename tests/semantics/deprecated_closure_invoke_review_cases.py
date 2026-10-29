"""Independent explicit Closure::__invoke source witnesses."""


def at80(prefix, operation, suffix):
    lines = ['<?php'] + prefix
    assert len(lines) <= 79
    lines += [''] * (79 - len(lines)) + [operation] + suffix
    assert lines[79] == operation
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'invoke-inner-warning-throw-keeps-raw-wrapper-owners': at80([
        'class RawArgument { public function __destruct() { $GLOBALS["arg_retired"]++; } }',
        'class InnerCarrier {',
        '    #[\\Deprecated("raw", "14"), \\NoDiscard]',
        '    public function retired(int $value) { $GLOBALS["body"]++; echo "BAD-BODY;"; return 7; }',
        '    public function __destruct() { $GLOBALS["receiver_retired"]++; }',
        '}',
        'function send_argument() { $value = new RawArgument(); $GLOBALS["weak_argument"] = WeakReference::create($value); return $value; }',
        'function notice($level, $message, $file, $line) {',
        '    $GLOBALS["calls"]++;',
        '    if ($level === 8192) {',
        '        echo "O:", $message === "Method Closure::__invoke() is deprecated since 14, raw", ":", $GLOBALS["body"] === 0, ";"; return true;',
        '    }',
        '    if ($level === 16384) {',
        '        $GLOBALS["inner"]++; $GLOBALS["closure"] = null;',
        '        $probe = new Exception("phase"); $trace = $probe->getTrace();',
        '        $wrapper = $trace[0]["function"] === "notice" && $trace[1]["function"] === "__invoke" && $trace[1]["class"] === "Closure" && $trace[1]["type"] === "->" && !isset($trace[2]);',
        '        $raw = $trace[1]["args"][0] === $GLOBALS["weak_argument"]->get() && !isset($trace[1]["args"][1]);',
        '        echo "I:", $message === "Method InnerCarrier::retired() is deprecated since 14, raw", ":", $file === __FILE__ && $line === 80, ":", $wrapper, ":", $raw, ":", $GLOBALS["weak_closure"]->get() !== null, ":", $GLOBALS["weak_receiver"]->get() !== null, ":", $GLOBALS["arg_retired"] === 0 && $GLOBALS["receiver_retired"] === 0, ";";',
        '        throw $GLOBALS["saved"];',
        '    }',
        '    $GLOBALS["other"]++; echo "BAD-WARNING;"; return true;',
        '}',
        '$body = 0; $calls = 0; $inner = 0; $other = 0; $arg_retired = 0; $receiver_retired = 0;',
        '$saved = new Exception("supplied"); $receiver = new InnerCarrier(); $closure = $receiver->retired(...);',
        '$weak_receiver = WeakReference::create($receiver); $weak_closure = WeakReference::create($closure); $receiver = null;',
        'set_error_handler("notice");',
    ], 'try { $closure->__invoke(send_argument()); } catch (Exception $caught) { echo "C:", $caught === $saved, ":", $body === 0, ":", $calls === 2 && $inner === 1 && $other === 0, ":", $weak_closure->get() === null, ":", $weak_receiver->get() === null, ":", $weak_argument->get() === null, ":", $arg_retired === 1 && $receiver_retired === 1, ";"; }', [
        'restore_error_handler();',
    ]),
    'invoke-unmarked-nodiscard-weak-reception-control': at80([
        'declare(strict_types=1);',
        '#[\\NoDiscard("masked")]',
        'function unmarked(int $value) { $GLOBALS["body"]++; echo "B:", $value === $GLOBALS["expected"], ";"; return $value + 1; }',
        'function notice($level, $message, $file, $line) { $GLOBALS["warnings"]++; echo "BAD-WARNING;"; return true; }',
        '$body = 0; $warnings = 0; $expected = 7; $closure = unmarked(...); set_error_handler("notice");',
    ], '$closure->__invoke("7"); $expected = 8; $result = $closure->__invoke("8");', [
        'restore_error_handler(); echo "E:", $body === 2, ":", $warnings === 0, ":", $result === 9, ";";',
    ]),
}

EXPECTED_STDOUT = {
    'invoke-inner-warning-throw-keeps-raw-wrapper-owners': b'O:1:1;I:1:1:1:1:1:1:1;C:1:1:1:1:1:1:1;',
    'invoke-unmarked-nodiscard-weak-reception-control': b'B:1;B:1;E:1:1:1;',
}

EXIT_CODES = {name: 0 for name in CASES}


def expected_stderr(name, path):
    return b''

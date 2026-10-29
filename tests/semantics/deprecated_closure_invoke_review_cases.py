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
    'invoke-reference-slot-live-through-both-warnings': at80([
        '#[\\Deprecated("alias", "15"), \\NoDiscard]',
        'function through(&$value, $tail) { $GLOBALS["body"]++; echo "B:", $value === 23, ":", $tail === "raw", ";"; $value = 31; return 9; }',
        'function decoy(&$value, $tail) { echo "BAD-DECOY;"; return 0; }',
        'function notice($level, $message, $file, $line) {',
        '    $GLOBALS["calls"]++;',
        '    if ($level === 8192) {',
        '        $GLOBALS["closure"] = $GLOBALS["replacement"]; $GLOBALS["value"] = 17;',
        '        echo "O:", $message === "Method Closure::__invoke() is deprecated since 15, alias", ":", $GLOBALS["weak_closure"]->get() !== null, ";"; return true;',
        '    }',
        '    if ($level === 16384) {',
        '        $GLOBALS["value"] = 23; $trace = (new Exception("phase"))->getTrace();',
        '        $GLOBALS["snapshot"] = $trace[1]["args"][0];',
        '        echo "I:", $message === "Function through() is deprecated since 15, alias", ":", $trace[1]["function"] === "__invoke", ":", $trace[1]["args"][0] === 23 && $trace[1]["args"][1] === "raw", ":", $GLOBALS["body"] === 0, ";"; return true;',
        '    }',
        '    $GLOBALS["other"]++; echo "BAD-WARNING;"; return true;',
        '}',
        '$body = 0; $calls = 0; $other = 0; $value = 7; $alias =& $value; $snapshot = null;',
        '$closure = through(...); $weak_closure = WeakReference::create($closure); $replacement = decoy(...);',
        'set_error_handler("notice");',
    ], '$closure->__invoke($alias, "raw");', [
        'restore_error_handler(); echo "E:", $body === 1, ":", $calls === 2 && $other === 0, ":", $value === 31 && $alias === 31, ":", $snapshot === 23, ":", $weak_closure->get() === null, ":", $closure === $replacement, ";";',
    ]),
    'invoke-body-return-retires-raw-argument-before-outer-receiver': at80([
        'class ReturnToken {',
        '    public function __destruct() { echo "T:", $GLOBALS["body"] === 1, ":", $GLOBALS["weak_closure"]->get() !== null, ":", $GLOBALS["weak_receiver"]->get() !== null, ";"; }',
        '}',
        'class ReturnCarrier {',
        '    #[\\Deprecated, \\NoDiscard]',
        '    public function act($value) { $GLOBALS["body"]++; echo "B:", $GLOBALS["weak_closure"]->get() !== null, ":", $GLOBALS["weak_receiver"]->get() === $this, ":", $value === $GLOBALS["weak_token"]->get(), ";"; return 7; }',
        '    public function __destruct() { echo "R:", $GLOBALS["body"] === 1, ":", $GLOBALS["weak_token"]->get() === null, ":", $GLOBALS["weak_closure"]->get() === null, ";"; }',
        '}',
        'function notice($level, $message, $file, $line) {',
        '    $GLOBALS["calls"]++;',
        '    if ($level === 8192) {',
        '        $GLOBALS["closure"] = null; $GLOBALS["token"] = null;',
        '        echo "O:", $message === "Method Closure::__invoke() is deprecated", ":", $GLOBALS["weak_closure"]->get() !== null, ":", $GLOBALS["weak_token"]->get() !== null, ";"; return true;',
        '    }',
        '    if ($level === 16384) { echo "I:", $message === "Method ReturnCarrier::act() is deprecated", ":", $GLOBALS["weak_closure"]->get() !== null, ";"; return true; }',
        '    $GLOBALS["other"]++; echo "BAD-WARNING;"; return true;',
        '}',
        '$body = 0; $calls = 0; $other = 0; $receiver = new ReturnCarrier(); $closure = $receiver->act(...);',
        '$weak_receiver = WeakReference::create($receiver); $weak_closure = WeakReference::create($closure); $receiver = null;',
        '$token = new ReturnToken(); $weak_token = WeakReference::create($token); set_error_handler("notice");',
    ], '$closure->__invoke($token);', [
        'restore_error_handler(); echo "E:", $body === 1, ":", $calls === 2 && $other === 0, ":", $weak_token->get() === null, ":", $weak_closure->get() === null, ":", $weak_receiver->get() === null, ";";',
    ]),
    'invoke-named-unpack-default-hole-stays-raw-through-warnings': at80([
        '#[\\Deprecated("unpack", "16"), \\NoDiscard]',
        'function raw_defaults($first = 5, $second = 8) { $GLOBALS["body"]++; echo "B:", $first === 5, ":", $second === 2, ":", $GLOBALS["calls"] === 2, ";"; return 7; }',
        'function notice($level, $message, $file, $line) {',
        '    $GLOBALS["calls"]++; $trace = (new Exception("phase"))->getTrace();',
        '    if ($level === 8192) {',
        '        echo "O:", $message === "Method Closure::__invoke() is deprecated since 16, unpack", ":", $file === __FILE__ && $line === 80, ":", !isset($trace[1]), ";"; return true;',
        '    }',
        '    if ($level === 16384) {',
        '        echo "I:", $message === "Function raw_defaults() is deprecated since 16, unpack", ":", $trace[1]["function"] === "__invoke" && $trace[1]["class"] === "Closure", ":", $trace[1]["args"][0] === null && $trace[1]["args"][1] === 2, ":", !isset($trace[2]), ":", $GLOBALS["body"] === 0, ";"; return true;',
        '    }',
        '    $GLOBALS["other"]++; echo "BAD-WARNING;"; return true;',
        '}',
        '$body = 0; $calls = 0; $other = 0; $closure = raw_defaults(...); set_error_handler("notice");',
    ], '$closure->__invoke(...["second" => 2]);', [
        'restore_error_handler(); echo "E:", $body === 1, ":", $calls === 2 && $other === 0, ";";',
    ]),
    'invoke-unused-owning-result-retires-between-raw-argument-and-receiver': at80([
        'class ResultToken {',
        '    public function __destruct() { echo "T:", $GLOBALS["body"] === 1, ":", $GLOBALS["weak_value"]->get() !== null, ":", $GLOBALS["weak_closure"]->get() !== null, ":", $GLOBALS["weak_receiver"]->get() !== null, ";"; }',
        '}',
        'class ResultValue {',
        '    public function __destruct() { echo "V:", $GLOBALS["weak_token"]->get() === null, ":", $GLOBALS["weak_closure"]->get() !== null, ":", $GLOBALS["weak_receiver"]->get() !== null, ";"; }',
        '}',
        'class ResultCarrier {',
        '    #[\\Deprecated, \\NoDiscard]',
        '    public function act($argument) {',
        '        $GLOBALS["body"]++; $value = new ResultValue(); $GLOBALS["weak_value"] = WeakReference::create($value);',
        '        echo "B:", $argument === $GLOBALS["weak_token"]->get(), ":", $GLOBALS["weak_closure"]->get() !== null, ":", $GLOBALS["weak_receiver"]->get() === $this, ";"; return $value;',
        '    }',
        '    public function __destruct() { echo "R:", $GLOBALS["weak_token"]->get() === null, ":", $GLOBALS["weak_value"]->get() === null, ":", $GLOBALS["weak_closure"]->get() === null, ";"; }',
        '}',
        'function notice($level, $message, $file, $line) {',
        '    $GLOBALS["calls"]++;',
        '    if ($level === 8192) {',
        '        $GLOBALS["closure"] = null; $GLOBALS["token"] = null;',
        '        echo "O:", $message === "Method Closure::__invoke() is deprecated", ":", $GLOBALS["weak_closure"]->get() !== null, ":", $GLOBALS["weak_token"]->get() !== null, ";"; return true;',
        '    }',
        '    if ($level === 16384) { echo "I:", $message === "Method ResultCarrier::act() is deprecated", ":", $GLOBALS["weak_closure"]->get() !== null, ";"; return true; }',
        '    $GLOBALS["other"]++; echo "BAD-WARNING;"; return true;',
        '}',
        '$body = 0; $calls = 0; $other = 0; $receiver = new ResultCarrier(); $closure = $receiver->act(...);',
        '$weak_receiver = WeakReference::create($receiver); $weak_closure = WeakReference::create($closure); $receiver = null;',
        '$token = new ResultToken(); $weak_token = WeakReference::create($token); set_error_handler("notice");',
    ], '$closure->__invoke($token);', [
        'restore_error_handler(); echo "E:", $body === 1, ":", $calls === 2 && $other === 0, ":", $weak_token->get() === null, ":", $weak_value->get() === null, ":", $weak_closure->get() === null, ":", $weak_receiver->get() === null, ";";',
    ]),
}

EXPECTED_STDOUT = {
    'invoke-inner-warning-throw-keeps-raw-wrapper-owners': b'O:1:1;I:1:1:1:1:1:1:1;C:1:1:1:1:1:1:1;',
    'invoke-unmarked-nodiscard-weak-reception-control': b'B:1;B:1;E:1:1:1;',
    'invoke-reference-slot-live-through-both-warnings': b'O:1:1;I:1:1:1:1;B:1:1;E:1:1:1:1:1:1;',
    'invoke-body-return-retires-raw-argument-before-outer-receiver': b'O:1:1:1;I:1:1;B:1:1:1;T:1:1:1;R:1:1:1;E:1:1:1:1:1;',
    'invoke-named-unpack-default-hole-stays-raw-through-warnings': b'O:1:1:1;I:1:1:1:1:1;B:1:1:1;E:1:1;',
    'invoke-unused-owning-result-retires-between-raw-argument-and-receiver': b'O:1:1:1;I:1:1;B:1:1:1;T:1:1:1:1;V:1:1:1;R:1:1:1;E:1:1:1:1:1:1;',
}

EXIT_CODES = {name: 0 for name in CASES}
BOUNDARIES = {
    'invoke-unused-owning-result-retires-between-raw-argument-and-receiver':
        ('unused owning explicit Closure wrapper result', b'O:1:1:1;I:1:1;B:1:1:1;'),
}


def expected_stderr(name, path):
    return b''

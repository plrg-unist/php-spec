"""Native-first used and throwing explicit Closure wrapper return owners."""
from deprecated_review_cases import at80


CASES = {
    'invoke-used-owning-result-survives-outer-receiver': at80([
        'class UsedToken {',
        '    public function __destruct() { echo "T:", $GLOBALS["body"] === 1, ":", $GLOBALS["weak_value"]->get() !== null, ":", $GLOBALS["weak_closure"]->get() !== null, ":", $GLOBALS["weak_receiver"]->get() !== null, ";"; }',
        '}',
        'class UsedValue {',
        '    public function __destruct() { echo "V:", $GLOBALS["weak_token"]->get() === null, ":", $GLOBALS["weak_closure"]->get() === null, ":", $GLOBALS["weak_receiver"]->get() === null, ";"; }',
        '}',
        'class UsedCarrier {',
        '    #[\\Deprecated, \\NoDiscard]',
        '    public function act($argument) {',
        '        $GLOBALS["body"]++; $value = new UsedValue(); $GLOBALS["weak_value"] = WeakReference::create($value);',
        '        echo "B:", $argument === $GLOBALS["weak_token"]->get(), ":", $GLOBALS["weak_closure"]->get() !== null, ":", $GLOBALS["weak_receiver"]->get() === $this, ";"; return $value;',
        '    }',
        '    public function __destruct() { echo "R:", $GLOBALS["weak_token"]->get() === null, ":", $GLOBALS["weak_value"]->get() !== null, ":", $GLOBALS["weak_closure"]->get() === null, ";"; }',
        '}',
        'function notice($level, $message, $file, $line) {',
        '    $GLOBALS["calls"]++;',
        '    if ($level === 8192) {',
        '        $GLOBALS["closure"] = null; $GLOBALS["token"] = null;',
        '        echo "O:", $message === "Method Closure::__invoke() is deprecated", ":", $GLOBALS["weak_closure"]->get() !== null, ":", $GLOBALS["weak_token"]->get() !== null, ";"; return true;',
        '    }',
        '    if ($level === 16384) { echo "I:", $message === "Method UsedCarrier::act() is deprecated", ":", $GLOBALS["weak_closure"]->get() !== null, ";"; return true; }',
        '    $GLOBALS["other"]++; echo "BAD-WARNING;"; return true;',
        '}',
        '$body = 0; $calls = 0; $other = 0; $receiver = new UsedCarrier(); $closure = $receiver->act(...);',
        '$weak_receiver = WeakReference::create($receiver); $weak_closure = WeakReference::create($closure); $receiver = null;',
        '$token = new UsedToken(); $weak_token = WeakReference::create($token); set_error_handler("notice");',
    ], '$used = $closure->__invoke($token);', [
        'echo "U:", $used === $weak_value->get(), ":", $weak_token->get() === null, ":", $weak_closure->get() === null, ":", $weak_receiver->get() === null, ";";',
        '$used = null; restore_error_handler(); echo "E:", $weak_value->get() === null, ":", $calls === 2 && $other === 0, ":", $body === 1, ";";',
    ]),
    'invoke-unused-result-destructor-throw-keeps-outer-owner-and-caller-trace': at80([
        'class ThrowToken {',
        '    public function __destruct() {',
        '        $trace = (new Exception("token trace"))->getTrace();',
        '        echo "T:", $GLOBALS["weak_value"]->get() !== null, ":", $GLOBALS["weak_closure"]->get() !== null, ":", $GLOBALS["weak_receiver"]->get() !== null, ":", $trace[0]["function"] === "__destruct" && $trace[0]["class"] === "ThrowToken", ":", $trace[0]["file"] === __FILE__ && $trace[0]["line"] === 80, ":", !isset($trace[1]), ";";',
        '    }',
        '}',
        'class ThrowValue {',
        '    public function __destruct() {',
        '        $trace = (new Exception("value trace"))->getTrace();',
        '        echo "V:", $GLOBALS["weak_token"]->get() === null, ":", $GLOBALS["weak_closure"]->get() !== null, ":", $GLOBALS["weak_receiver"]->get() !== null, ":", $trace[0]["function"] === "__destruct" && $trace[0]["class"] === "ThrowValue", ":", $trace[0]["file"] === __FILE__ && $trace[0]["line"] === 80, ":", !isset($trace[1]), ";";',
        '        throw $GLOBALS["saved"];',
        '    }',
        '}',
        'class ThrowCarrier {',
        '    #[\\Deprecated, \\NoDiscard]',
        '    public function act($argument) {',
        '        $GLOBALS["body"]++; $value = new ThrowValue(); $GLOBALS["weak_value"] = WeakReference::create($value);',
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
        '    if ($level === 16384) { echo "I:", $message === "Method ThrowCarrier::act() is deprecated", ":", $GLOBALS["weak_closure"]->get() !== null, ";"; return true; }',
        '    $GLOBALS["other"]++; echo "BAD-WARNING;"; return true;',
        '}',
        '$body = 0; $calls = 0; $other = 0; $saved = new Exception("supplied");',
        '$receiver = new ThrowCarrier(); $closure = $receiver->act(...);',
        '$weak_receiver = WeakReference::create($receiver); $weak_closure = WeakReference::create($closure); $receiver = null;',
        '$token = new ThrowToken(); $weak_token = WeakReference::create($token); set_error_handler("notice");',
        'try {',
    ], '    $closure->__invoke($token);', [
        '    echo "BAD-RETURN;";',
        '} catch (Exception $caught) {',
        '    echo "C:", $caught === $saved, ":", $caught->getPrevious() === null, ":", $calls === 2 && $other === 0, ":", $body === 1, ":", $weak_token->get() === null, ":", $weak_value->get() === null, ":", $weak_closure->get() === null, ":", $weak_receiver->get() === null, ";";',
        '}',
        'restore_error_handler();',
    ]),
}

EXPECTED_STDOUT = {
    'invoke-used-owning-result-survives-outer-receiver': b'O:1:1:1;I:1:1;B:1:1:1;T:1:1:1:1;R:1:1:1;U:1:1:1:1;V:1:1:1;E:1:1:1;',
    'invoke-unused-result-destructor-throw-keeps-outer-owner-and-caller-trace': b'O:1:1:1;I:1:1;B:1:1:1;T:1:1:1:1:1:1;V:1:1:1:1:1:1;R:1:1:1;C:1:1:1:1:1:1:1:1;',
}
EXIT_CODES = {name: 0 for name in CASES}


def expected_stderr(name, path):
    return b''

"""Independent native-first explicit Closure wrapper return aliases."""
from deprecated_review_cases import at80


CASES = {
    'invoke-unused-aliased-result-outlives-later-raw-argument': at80([
        'class AliasToken {',
        '    public function __destruct() { echo "T:", $GLOBALS["weak_marker"]->get() === null, ":", $GLOBALS["weak_closure"]->get() !== null, ":", $GLOBALS["weak_receiver"]->get() !== null, ";"; }',
        '}',
        'class AliasMarker {',
        '    public function __destruct() { echo "M:", $GLOBALS["body"] === 1, ":", $GLOBALS["weak_token"]->get() !== null, ":", $GLOBALS["weak_closure"]->get() !== null, ":", $GLOBALS["weak_receiver"]->get() !== null, ";"; }',
        '}',
        'class AliasCarrier {',
        '    #[\\Deprecated, \\NoDiscard]',
        '    public function act($first, $second) {',
        '        $GLOBALS["body"]++; echo "B:", $first === $GLOBALS["weak_token"]->get(), ":", $second === $GLOBALS["weak_marker"]->get(), ":", $GLOBALS["weak_receiver"]->get() === $this, ";"; return $first;',
        '    }',
        '    public function __destruct() { echo "R:", $GLOBALS["weak_token"]->get() === null, ":", $GLOBALS["weak_marker"]->get() === null, ":", $GLOBALS["weak_closure"]->get() === null, ";"; }',
        '}',
        'function notice($level, $message, $file, $line) {',
        '    $GLOBALS["calls"]++;',
        '    if ($level === 8192) {',
        '        $GLOBALS["closure"] = null; $GLOBALS["token"] = null; $GLOBALS["marker"] = null;',
        '        echo "O:", $message === "Method Closure::__invoke() is deprecated", ":", $GLOBALS["weak_closure"]->get() !== null, ":", $GLOBALS["weak_token"]->get() !== null, ":", $GLOBALS["weak_marker"]->get() !== null, ";"; return true;',
        '    }',
        '    if ($level === 16384) { echo "I:", $message === "Method AliasCarrier::act() is deprecated", ":", $GLOBALS["weak_closure"]->get() !== null, ";"; return true; }',
        '    $GLOBALS["other"]++; echo "BAD-WARNING;"; return true;',
        '}',
        '$body = 0; $calls = 0; $other = 0; $receiver = new AliasCarrier(); $closure = $receiver->act(...);',
        '$weak_receiver = WeakReference::create($receiver); $weak_closure = WeakReference::create($closure); $receiver = null;',
        '$token = new AliasToken(); $marker = new AliasMarker();',
        '$weak_token = WeakReference::create($token); $weak_marker = WeakReference::create($marker); set_error_handler("notice");',
    ], '$closure->__invoke($token, $marker);', [
        'restore_error_handler(); echo "E:", $calls === 2 && $other === 0, ":", $body === 1, ":", $weak_token->get() === null, ":", $weak_marker->get() === null, ":", $weak_closure->get() === null, ":", $weak_receiver->get() === null, ";";',
    ]),
}

EXPECTED_STDOUT = {
    'invoke-unused-aliased-result-outlives-later-raw-argument': b'O:1:1:1:1;I:1:1;B:1:1:1;M:1:1:1:1;T:1:1:1;R:1:1:1;E:1:1:1:1:1:1;',
}
EXIT_CODES = {name: 0 for name in CASES}


def expected_stderr(name, path):
    return b''

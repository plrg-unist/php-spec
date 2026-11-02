"""Independent native-first FCC spelling and scoped tick-cache lifetimes."""
from deprecated_cases import php


PULSE = [
    'function cache_pulse($phase) {',
    '    $GLOBALS["phase"] = $phase;',
    '    declare(ticks=1) {',
    '        $GLOBALS["armed"] = true;',
    '        $GLOBALS["armed"] = false;',
    '    }',
    '}',
]


CASES = {
    'tick-raw-object-cache-distinct-from-invoke-array': php([
        '$armed = false; $phase = 0; $calls = 0;',
        'class CacheInvoker {',
        '    public function __invoke() {',
        '        if (!$GLOBALS["armed"]) { return 7; }',
        '        $GLOBALS["calls"]++; echo "C:", $GLOBALS["phase"] === 1 || $GLOBALS["phase"] === 2, ";"; return 7;',
        '    }',
        '    public function __destruct() { echo "R:", $GLOBALS["calls"] === 3, ":", $GLOBALS["phase"] === 2, ";"; }',
        '}',
        *PULSE,
        '$callback = new CacheInvoker(); $weak = WeakReference::create($callback);',
        'register_tick_function($callback);',
        'register_tick_function([$callback, "__invoke"]);',
        '$callback = null; echo "P:", $weak->get() !== null, ";";',
        'cache_pulse(1); echo "A:", $calls === 2, ";";',
        'unregister_tick_function([$weak->get(), "__invoke"]);',
        'unregister_tick_function([$weak->get(), "__invoke"]);',
        'echo "U:", $weak->get() !== null, ":", $calls === 2, ";";',
        'cache_pulse(2); echo "B:", $calls === 3, ";";',
        'unregister_tick_function($weak->get());',
        'echo "E:", $weak->get() === null, ":", $calls === 3, ":", $phase === 2, ";";',
    ]),
    'tick-scoped-method-closure-cache-arguments-before-owner': php([
        '$armed = false; $phase = 0; $calls = 0;',
        'class CacheToken {',
        '    public function __destruct() {',
        '        echo "T:", $GLOBALS["calls"] === 1, ":", $GLOBALS["weak_callback"]->get() !== null, ":", $GLOBALS["weak_owner"]->get() !== null, ";";',
        '    }',
        '}',
        'class CacheOwner {',
        '    private $value = 7;',
        '    public function capture() { return $this->tick(...); }',
        '    private function tick($argument) {',
        '        if (!$GLOBALS["armed"]) { return 7; }',
        '        $GLOBALS["calls"]++;',
        '        echo "C:", $this->value === 7, ":", $GLOBALS["weak_owner"]->get() === $this, ":", $argument === $GLOBALS["weak_token"]->get(), ";"; return 7;',
        '    }',
        '    public function __destruct() {',
        '        echo "R:", $GLOBALS["calls"] === 1, ":", $GLOBALS["weak_callback"]->get() === null, ":", $GLOBALS["weak_token"]->get() === null, ";";',
        '    }',
        '}',
        *PULSE,
        '$owner = new CacheOwner(); $callback = $owner->capture(); $token = new CacheToken();',
        '$weak_owner = WeakReference::create($owner); $weak_callback = WeakReference::create($callback); $weak_token = WeakReference::create($token);',
        'register_tick_function($callback, $token);',
        '$owner = null; $callback = null; $token = null;',
        'echo "P:", $weak_callback->get() !== null, ":", $weak_owner->get() !== null, ":", $weak_token->get() !== null, ";";',
        'cache_pulse(1); echo "A:", $calls === 1, ";";',
        'unregister_tick_function($weak_callback->get());',
        'echo "E:", $calls === 1, ":", $weak_callback->get() === null, ":", $weak_owner->get() === null, ":", $weak_token->get() === null, ";";',
    ]),
}

EXPECTED_STDOUT = {
    'tick-raw-object-cache-distinct-from-invoke-array':
        b'P:1;C:1;C:1;A:1;U:1:1;C:1;B:1;R:1:1;E:1:1:1;',
    'tick-scoped-method-closure-cache-arguments-before-owner':
        b'P:1:1:1;C:1:1:1;A:1;T:1:1:1;R:1:1:1;E:1:1:1:1;',
}
EXIT_CODES = {name: 0 for name in CASES}


def expected_stderr(name, path):
    assert name in CASES
    return b''

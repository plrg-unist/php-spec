"""Native-first Deprecated declarations, VM call phases and pending owners."""


def php(lines):
    return ('\n'.join(['<?php'] + lines) + '\n').encode()


def at60(prefix, operation, suffix):
    lines = ['<?php'] + prefix
    assert len(lines) <= 59
    lines += [''] * (59 - len(lines)) + [operation] + suffix
    assert lines[59] == operation
    return ('\n'.join(lines) + '\n').encode()


ND = 'The return value of function marked() should either be used or intentionally ignored by casting it as (void)'

CASES = {
    'alias-binary-suffix-all-result-uses': at60([
        'use Deprecated as Old;',
        '#[Old(since: "8\\0x", message: "use\\0new")]',
        'function marked() { echo "B;"; return 7; }',
        '#[\\Deprecated(message: null, since: "")]',
        'function bare() { echo "Z;"; return 9; }',
        'function notice($level, $message, $file, $line) {',
        '    $GLOBALS["calls"]++;',
        '    $expected = $GLOBALS["calls"] < 4 ? "Function marked() is deprecated since 8\\0x, use\\0new" : "Function bare() is deprecated";',
        '    echo "D:", $level === 16384, ":", $message === $expected, ":", $file === __FILE__, ":", $line === 60, ";";',
        '    return true;',
        '}',
        '$calls = 0; set_error_handler("notice");',
    ], 'marked(); $result = marked(); (void) marked(); $other = bare();', [
        'restore_error_handler(); echo "E:", $calls === 4, ":", $result === 7, ":", $other === 9, ";";',
    ]),
    'deprecated-before-nodiscard-before-type-recv': at60([
        '#[\\NoDiscard("must-use"), \\Deprecated("old", since: "1")]',
        'function marked(int $value) { echo "BAD-B;"; return 7; }',
        'function notice($level, $message, $file, $line) {',
        '    $GLOBALS["calls"]++;',
        '    if ($GLOBALS["calls"] === 1) {',
        '        $GLOBALS["arg"] = 7;',
        '        echo "D:", $level === 16384, ":", $message === "Function marked() is deprecated since 1, old", ":", $line === 60, ";";',
        '    } else {',
        '        echo "N:", $level === 512, ":", $message === "' + ND + ', must-use", ":", $GLOBALS["arg"] === 7, ";";',
        '    }',
        '    return true;',
        '}',
        '$calls = 0; $arg = "bad"; set_error_handler("notice");',
        'try {',
    ], '    marked($arg);', [
        '    echo "BAD-R;";',
        '} catch (TypeError $caught) {',
        '    echo "C:", $calls === 2, ":", $arg === 7, ":", $caught->getLine() === 3, ":", $caught->getPrevious() === null, ";";',
        '}',
        'restore_error_handler();',
    ]),
    'deprecated-throw-cancels-nodiscard-and-recv': at60([
        'class Token { public function __destruct() { echo "D;"; } }',
        '#[\\NoDiscard, \\Deprecated]',
        'function marked(int $value) { echo "BAD-B;"; return 7; }',
        'function notice($level, $message, $file, $line) {',
        '    $GLOBALS["calls"]++; $GLOBALS["arg"] = null;',
        '    echo "H:", $level === 16384, ":", $message === "Function marked() is deprecated", ":", $GLOBALS["weak"]->get() !== null, ";";',
        '    throw $GLOBALS["saved"];',
        '}',
        '$arg = new Token(); $weak = WeakReference::create($arg);',
        '$saved = new Exception("stop"); $calls = 0; set_error_handler("notice");',
        'try {',
    ], '    marked($arg);', [
        '    echo "BAD-R;";',
        '} catch (Exception $caught) {',
        '    echo "C:", $caught === $saved, ":", $calls === 1, ":", $weak->get() === null, ":", $caught->getPrevious() === null, ";";',
        '}',
        'restore_error_handler();',
    ]),
    'positional-arity-versus-required-named-hole': at60([
        '#[\\Deprecated]',
        'function need($first, $second) { echo "BAD-B;"; return 7; }',
        'function notice($level, $message, $file, $line) {',
        '    $GLOBALS["calls"]++; echo "D:", $level === 16384, ":", $line === 60, ";"; return true;',
        '}',
        '$calls = 0; set_error_handler("notice");',
        'try {',
    ], '    need();', [
        '    echo "BAD-P;";',
        '} catch (ArgumentCountError $caught) {',
        '    echo "P:", $calls === 1, ":", $caught->getMessage() === "Too few arguments to function need(), 0 passed in " . __FILE__ . " on line 60 and exactly 2 expected", ";";',
        '}',
        'try { need(second: 2); echo "BAD-N;"; } catch (ArgumentCountError $caught) {',
        '    echo "N:", $calls === 1, ":", $caught->getMessage() === \'need(): Argument #1 ($first) not passed\', ";";',
        '}',
        'restore_error_handler();',
    ]),
    'method-used-result-retains-sent-value-and-receiver': at60([
        'class Owner {',
        '    #[\\Deprecated("replacement", "2")]',
        '    public function act($value) {',
        '        echo "B:", $value === 5, ":", $GLOBALS["arg"] === 9, ":", $GLOBALS["weak"]->get() === $this, ";";',
        '        return 7;',
        '    }',
        '    public function __destruct() { echo "D;"; }',
        '}',
        'function notice($level, $message, $file, $line) {',
        '    $GLOBALS["calls"]++; $GLOBALS["receiver"] = null; $GLOBALS["arg"] = 9;',
        '    echo "H:", $level === 16384, ":", $message === "Method Owner::act() is deprecated since 2, replacement", ":", $GLOBALS["weak"]->get() !== null, ";";',
        '    return true;',
        '}',
        '$receiver = new Owner(); $weak = WeakReference::create($receiver);',
        '$arg = 5; $calls = 0; set_error_handler("notice");',
    ], '$result = $receiver->act($arg);', [
        'restore_error_handler(); echo "E:", $calls === 1, ":", $result === 7, ":", $weak->get() === null, ";";',
    ]),
}

EXPECTED_STDOUT = {
    'alias-binary-suffix-all-result-uses': b'D:1:1:1:1;B;D:1:1:1:1;B;D:1:1:1:1;B;D:1:1:1:1;Z;E:1:1:1;',
    'deprecated-before-nodiscard-before-type-recv': b'D:1:1:1;N:1:1:1;C:1:1:1:1;',
    'deprecated-throw-cancels-nodiscard-and-recv': b'H:1:1:1;D;C:1:1:1:1;',
    'positional-arity-versus-required-named-hole': b'D:1:1;P:1:1;N:1:1;',
    'method-used-result-retains-sent-value-and-receiver': b'H:1:1:1;B:1:1:1;D;E:1:1:1;',
}

STATIC = {
    'repeat-before-invalid-parameter': ('#[\\Deprecated, \\Deprecated] function invalid(void $bad) {}', 'Attribute "Deprecated" must not be repeated', 'php_error'),
    'parameter-target': ('function invalid(#[\\Deprecated] $bad) {}', 'Attribute "Deprecated" cannot target parameter (allowed targets: class, function, method, class constant, constant)', 'php_error'),
    'class-validator-before-members': ('#[\\Deprecated] class Invalid { public int $bad = "wrong"; }', 'Cannot apply #[\\Deprecated] to class Invalid', 'static_rejection'),
}
for name, (declaration, message, status) in STATIC.items():
    CASES[name] = php(['echo "BAD-RUN;";', declaration])
    EXPECTED_STDOUT[name] = b''

CASES['ordinary-owner-control'] = php([
    'class Owner {',
    '    public function act($value) {',
    '        $GLOBALS["receiver"] = null; $GLOBALS["arg"] = 9;',
    '        echo "B:", $value === 5, ":", $GLOBALS["weak"]->get() === $this, ";"; return 7;',
    '    }',
    '    public function __destruct() { echo "D;"; }',
    '}',
    '$receiver = new Owner(); $weak = WeakReference::create($receiver); $arg = 5;',
    '$result = $receiver->act($arg);',
    'echo "E:", $arg === 9, ":", $result === 7, ":", $weak->get() === null, ";";',
])
EXPECTED_STDOUT['ordinary-owner-control'] = b'B:1:1;D;E:1:1:1;'
CONTROLS = {'ordinary-owner-control'}
EXIT_CODES = {name: 255 for name in STATIC}
STATUSES = {name: values[2] for name, values in STATIC.items()}


def expected_stderr(name, path):
    if name in STATIC:
        return (b'Fatal error: ' + STATIC[name][1].encode() + b' in ' + bytes(path) +
                b' on line 3\nStack trace:\n#0 {main}\n')
    return b''


BASELINE_SELECTION = (
    'alias-binary-suffix-all-result-uses',
    'method-used-result-retains-sent-value-and-receiver',
    'class-validator-before-members', 'ordinary-owner-control',
)

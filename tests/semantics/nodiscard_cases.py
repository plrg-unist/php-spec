"""Frozen NoDiscard declarations, call phases, result uses and real owners."""


def php(lines):
    return ('\n'.join(['<?php'] + lines) + '\n').encode()


def at60(prefix, operation, suffix):
    lines = ['<?php'] + prefix
    assert len(lines) <= 59
    lines += [''] * (59 - len(lines)) + [operation] + suffix
    assert lines[59] == operation
    return ('\n'.join(lines) + '\n').encode()


NOTICE = 'The return value of function marked() should either be used or intentionally ignored by casting it as (void)'


def handler(message=NOTICE, result='true'):
    return [
        'function notice($level, $message, $file, $line) {',
        '    $GLOBALS["calls"]++;',
        '    echo "H:", $level === 512, ":", $message === ' + repr(message) + ', ":", $file === __FILE__, ":", $line === 60, ";";',
        '    return ' + result + ';',
        '}',
    ]


CASES = {
    'handler-false-default-warning': at60([
        '#[\\NoDiscard("retain")]',
        'function marked() { echo "B;"; return 7; }',
        *handler(NOTICE + ', retain', 'false'),
        '$calls = 0; set_error_handler("notice");',
    ], 'marked();', [
        'restore_error_handler(); echo "E:", $calls === 1, ";";',
    ]),
    'named-contiguous-before-recv': at60([
        '#[\\NoDiscard(message: "")]',
        'function marked($first, $second) { echo "B:", $first, ":", $second, ";"; return 7; }',
        *handler(),
        '$calls = 0; set_error_handler("notice");',
    ], 'marked(second: 3, first: 4);', [
        'restore_error_handler(); echo "E:", $calls === 1, ";";',
    ]),
    'array-unpack-before-recv': at60([
        '#[\\NoDiscard(null)]',
        'function marked($first, $second) { echo "B:", $first, ":", $second, ";"; return 7; }',
        *handler(),
        '$calls = 0; set_error_handler("notice");',
    ], 'marked(...[4, 3]);', [
        'restore_error_handler(); echo "E:", $calls === 1, ";";',
    ]),
    'named-hole-before-warning-caller-trace': at60([
        '#[\\NoDiscard]',
        'function marked($first = 5, $second = 0) { echo "B:", $first, ":", $second, ";"; return 7; }',
        'function notice($level, $message, $file, $line) {',
        '    $GLOBALS["calls"]++; echo "H:", $level === 512, ":", $message === ' + repr(NOTICE) + ', ":", $file === __FILE__, ":", $line === 60, ";";',
        '    $probe = new Exception("trace"); $trace = $probe->getTrace();',
        '    echo "T:", $trace[0]["function"] === "notice", ":", !isset($trace[1]), ";";',
        '    return true;',
        '}',
        '$calls = 0; set_error_handler("notice");',
    ], 'marked(second: 3);', [
        'restore_error_handler(); echo "E:", $calls === 1, ";";',
    ]),
    'warning-before-type-recv': at60([
        '#[\\NoDiscard]',
        'function marked(int $value) { echo "BAD-B;"; return 7; }',
        *handler(),
        '$calls = 0; set_error_handler("notice");',
        'try {',
    ], '    marked("bad");', [
        '    echo "BAD-R;";',
        '} catch (TypeError $caught) {',
        '    echo "C:", $calls === 1, ":", $caught->getLine() === 3, ":", $caught->getPrevious() === null, ";";',
        '}',
        'restore_error_handler();',
    ]),
    'send-error-before-nodiscard': at60([
        '#[\\NoDiscard]',
        'function marked(&$slot) { echo "BAD-B;"; return 7; }',
        *handler(),
        '$calls = 0; set_error_handler("notice");',
        'try {',
    ], '    marked(1);', [
        '    echo "BAD-R;";',
        '} catch (Error $caught) {',
        '    echo "C:", $calls === 0, ":", $caught->getLine() === 60, ":", $caught->getPrevious() === null, ";";',
        '}',
        'restore_error_handler();',
    ]),
    'callback-api-result-is-used': at60([
        '#[\\NoDiscard]',
        'function marked($level, $message, $file, $line) {',
        '    $GLOBALS["calls"]++; echo "C:", $level === 512, ":", $message === "ordinary", ":", $line === 60, ";";',
        '    return true;',
        '}',
        '$calls = 0; set_error_handler("marked");',
    ], 'trigger_error("ordinary", 512);', [
        'restore_error_handler(); echo "E:", $calls === 1, ";";',
    ]),
    'handler-registry-replacement': at60([
        '#[\\NoDiscard]',
        'function marked() { echo "B;"; return 7; }',
        'function first_notice($level, $message, $file, $line) {',
        '    echo "H1:", $level === 512, ";"; set_error_handler("second_notice"); return true;',
        '}',
        'function second_notice($level, $message, $file, $line) { echo "H2:", $level === 512, ";"; return true; }',
        'set_error_handler("first_notice");',
    ], 'marked(); marked();', [
        'restore_error_handler(); restore_error_handler(); echo "E;";',
    ]),
    'return-reference-stays-selected': at60([
        '#[\\NoDiscard]',
        'function &marked() { echo "B:", $GLOBALS["cell"], ";"; return $GLOBALS["cell"]; }',
        'function reference_notice($level, $message, $file, $line) {',
        '    $GLOBALS["cell"] = 9; echo "H:", $level === 512, ";"; return true;',
        '}',
        '$cell = 5; $outside =& $cell; set_error_handler("reference_notice");',
    ], 'marked();', [
        'restore_error_handler(); echo "E:", $outside === 9, ";";',
    ]),
    'user-invoke-is-not-closure-trampoline': at60([
        'class Invoker {',
        '    #[\\NoDiscard]',
        '    public function __invoke() { echo "B;"; return 7; }',
        '}',
        'function invoke_notice($level, $message, $file, $line) {',
        '    $GLOBALS["calls"]++; echo "H:", $level === 512, ":", $message === "The return value of method Invoker::__invoke() should either be used or intentionally ignored by casting it as (void)", ";"; return true;',
        '}',
        '$calls = 0; $invoker = new Invoker(); set_error_handler("invoke_notice");',
    ], '$invoker(); $invoker->__invoke(); (void) $invoker();', [
        'restore_error_handler(); echo "E:", $calls === 2, ";";',
    ]),
}

EXPECTED_STDOUT = {
    'handler-false-default-warning': b'H:1:1:1:1;B;E:1;',
    'named-contiguous-before-recv': b'H:1:1:1:1;B:4:3;E:1;',
    'array-unpack-before-recv': b'H:1:1:1:1;B:4:3;E:1;',
    'named-hole-before-warning-caller-trace': b'H:1:1:1:1;T:1:1;B:5:3;E:1;',
    'warning-before-type-recv': b'H:1:1:1:1;C:1:1:1;',
    'send-error-before-nodiscard': b'C:1:1:1;',
    'callback-api-result-is-used': b'C:1:1:1;E:1;',
    'handler-registry-replacement': b'H1:1;B;H2:1;B;E;',
    'return-reference-stays-selected': b'H:1;B:9;E:1;',
    'user-invoke-is-not-closure-trampoline': b'H:1:1;B;H:1:1;B;B;E:1;',
}

STATIC = {
    'void-function-before-body': ('#[\\NoDiscard] function invalid(): void { echo "BAD-B;"; }', 'A void function does not return a value, but #[\\NoDiscard] requires a return value', True),
    'never-function-before-body': ('#[\\NoDiscard] function invalid(): never { return; }', 'A never returning function does not return a value, but #[\\NoDiscard] requires a return value', True),
    'void-method-before-body': ('class Invalid { #[\\NoDiscard] public function act(): void { echo "BAD-B;"; } }', 'A void method does not return a value, but #[\\NoDiscard] requires a return value', True),
    'repeated-before-signature': ('#[\\NoDiscard, \\NoDiscard] function invalid(void $bad) {}', 'Attribute "NoDiscard" must not be repeated', True),
    'class-target-before-members': ('#[\\NoDiscard] class Invalid { public int $bad = "wrong"; }', 'Attribute "NoDiscard" cannot target class (allowed targets: function, method)', True),
    'parameter-target': ('function invalid(#[\\NoDiscard] $bad) {}', 'Attribute "NoDiscard" cannot target parameter (allowed targets: function, method)', True),
    'constructor-target': ('class Invalid { #[\\NoDiscard] public function __construct() {} }', 'Method Invalid::__construct cannot be #[\\NoDiscard]', True),
    'hook-target-before-body': ('class Invalid { public int $value { #[\\NoDiscard] get { return 1; } } }', '#[\\NoDiscard] is not supported for property hooks', True),
}
for name, (declaration, message, trace) in STATIC.items():
    CASES[name] = php(['echo "BAD-RUN;";', declaration])
    EXPECTED_STDOUT[name] = b''

# An unchanged source counterpart validates the receiver/ref/observer machinery.
CASES['ordinary-reference-owner-control'] = php([
    'class Owner {',
    '    public function act(&$slot) {',
    '        $GLOBALS["receiver"] = null; $GLOBALS["outside"] = 9;',
    '        $GLOBALS["arg"] =& $GLOBALS["replacement"];',
    '        echo "B:", $slot === 9, ":", $GLOBALS["weak"]->get() === $this, ";";',
    '        $slot = 20; return 7;',
    '    }',
    '    public function __destruct() { echo "D:", $GLOBALS["outside"] === 20, ";"; }',
    '}',
    '$receiver = new Owner(); $weak = WeakReference::create($receiver);',
    '$arg = 5; $outside =& $arg; $replacement = 33;',
    '$receiver->act($arg);',
    'echo "E:", $outside === 20, ":", $arg === 33, ":", $weak->get() === null, ";";',
])
EXPECTED_STDOUT['ordinary-reference-owner-control'] = b'B:1:1;D:1;E:1:1:1;'
CONTROLS = {'ordinary-reference-owner-control'}
EXIT_CODES = {name: 255 for name in STATIC}
STATUSES = {name: 'static_rejection' for name in STATIC}
# Target/repeat checks use E_ERROR, rather than E_COMPILE_ERROR.
STATUSES.update({name: 'php_error' for name in ('repeated-before-signature', 'class-target-before-members', 'parameter-target')})


def expected_stderr(name, path):
    if name == 'handler-false-default-warning':
        return b'Warning: ' + NOTICE.encode() + b', retain in ' + bytes(path) + b' on line 60\n'
    if name in STATIC:
        _, message, trace = STATIC[name]
        return (b'Fatal error: ' + message.encode() + b' in ' + bytes(path) + b' on line 3\n' +
                (b'Stack trace:\n#0 {main}\n' if trace else b''))
    return b''


BASELINE_SELECTION = (
    'handler-false-default-warning', 'user-invoke-is-not-closure-trampoline',
    'class-target-before-members', 'ordinary-reference-owner-control',
)

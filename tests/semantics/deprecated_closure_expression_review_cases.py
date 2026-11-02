"""Independent native-first scoped Closure flags and declaration priorities."""
from deprecated_cases import php
from deprecated_review_cases import at80


def scoped_case(wrapper):
    first_level = '8192' if wrapper else '16384'
    first_message = ('"Method Closure::__invoke() is deprecated since 17, scoped"'
                     if wrapper else '$GLOBALS["expected_deprecated"]')
    second_level = '16384' if wrapper else '512'
    second_message = ('$GLOBALS["expected_deprecated"]' if wrapper else
                      '$GLOBALS["expected_nodiscard"]')
    first_label, second_label = ('W', 'U') if wrapper else ('D', 'N')
    return at80([
        'class Origin {',
        '    public function make($snapshot) {',
        '        $GLOBALS["declline"] = __LINE__ + 3;',
        '        return',
        '            #[\\Deprecated("scoped", "17"), \\NoDiscard("needed")]',
        '            function () use ($snapshot) {',
        '                $GLOBALS["body"]++; echo "B:", $snapshot === 7, ":", $GLOBALS["weak_receiver"]->get() === $this, ":", $GLOBALS["weak_origin"]->get() === null, ":", $GLOBALS["input"] === 8, ";"; return 7;',
        '            };',
        '    }',
        '}',
        'class Rebound {',
        '    public function __destruct() { echo "R:", $GLOBALS["body"] === 1, ":", $GLOBALS["weak_closure"]->get() === null, ":", $GLOBALS["weak_origin"]->get() === null, ";"; }',
        '}',
        'function notice($level, $message, $file, $line) {',
        '    $GLOBALS["calls"]++;',
        '    if ($GLOBALS["calls"] === 1) {',
        '        $GLOBALS["closure"] = static function () { $GLOBALS["replacement"]++; return 99; }; $GLOBALS["input"] = 8;',
        '        echo "' + first_label + ':", $level === ' + first_level + ', ":", $message === ' + first_message + ', ":", $file === __FILE__, ":", $line === 80, ":", $GLOBALS["weak_receiver"]->get() !== null, ";"; return true;',
        '    }',
        '    if ($GLOBALS["calls"] === 2) {',
        '        echo "' + second_label + ':", $level === ' + second_level + ', ":", $message === ' + second_message + ', ":", $line === 80, ":", $GLOBALS["weak_closure"]->get() !== null, ";"; return true;',
        '    }',
        '    $GLOBALS["other"]++; echo "BAD-WARNING;"; return true;',
        '}',
        '$calls = 0; $body = 0; $other = 0; $replacement = 0; $input = 7;',
        '$origin = new Origin(); $weak_origin = WeakReference::create($origin); $template = $origin->make($input);',
        '$receiver = new Rebound(); $closure = $template->bindTo($receiver, Rebound::class);',
        '$weak_closure = WeakReference::create($closure); $weak_receiver = WeakReference::create($receiver);',
        '$origin = null; $template = null; $receiver = null;',
        '$expected_deprecated = "Method Rebound::{closure:Origin::make():" . $declline . "}() is deprecated since 17, scoped";',
        '$expected_nodiscard = "The return value of method Rebound::{closure:Origin::make():" . $declline . "}() should either be used or intentionally ignored by casting it as (void), needed";',
        'set_error_handler("notice");',
    ], '$closure->__invoke();' if wrapper else '$closure();', [
        'restore_error_handler(); echo "E:", $calls === 2 && $other === 0, ":", $body === 1, ":", $replacement === 0, ":", $weak_closure->get() === null, ":", $weak_receiver->get() === null, ":", $weak_origin->get() === null, ";";',
    ])


CASES = {
    'scoped-rebound-closure-vm-flags-retain-selected-receiver': scoped_case(False),
    'scoped-rebound-closure-wrapper-flags-retain-selected-receiver': scoped_case(True),
    'anonymous-scope-closure-warnings-use-two-c-strings': at80([
        'function anonymous_notice($level, $message, $file, $line) {',
        '    $GLOBALS["calls"]++;',
        '    if ($GLOBALS["calls"] === 1) { echo "A:", $level === 16384, ":", $message === "Method class@anonymous::{closure:class@anonymous() is deprecated", ":", $file === __FILE__, ":", $line === 80, ";"; return true; }',
        '    if ($GLOBALS["calls"] === 2) { echo "N:", $level === 512, ":", $message === "The return value of method class@anonymous::{closure:class@anonymous() should either be used or intentionally ignored by casting it as (void)", ":", $line === 80, ";"; return true; }',
        '    $GLOBALS["other"]++; echo "BAD-WARNING;"; return true;',
        '}',
        '$maker = new class {',
        '    public function make() {',
        '        return #[\\Deprecated, \\NoDiscard] static function () { echo "B;"; return 7; };',
        '    }',
        '};',
        '$closure = $maker->make(); $maker = null;',
        '$calls = 0; $other = 0; set_error_handler("anonymous_notice");',
    ], '$closure();', [
        'restore_error_handler(); echo "E:", $calls === 2 && $other === 0, ";";',
    ]),
    'closure-duplicate-use-before-repeated-deprecated': php([
        'echo "BAD-RUN;";',
        '$token = 1;',
        '$closure =',
        '    #[\\Deprecated, \\Deprecated]',
        '    static',
        '    function () use ($token, $token) { return 1; };',
    ]),
    'class-scoped-nodiscard-void-closure-before-bad-body': php([
        'echo "BAD-RUN;";',
        'class Invalid {',
        '    public static function make() {',
        '        $closure =',
        '            #[\\NoDiscard]',
        '            static',
        '            function (): void { return 1; };',
        '    }',
        '}',
    ]),
}

EXPECTED_STDOUT = {
    'scoped-rebound-closure-vm-flags-retain-selected-receiver': b'D:1:1:1:1:1;N:1:1:1:1;B:1:1:1:1;R:1:1:1;E:1:1:1:1:1:1;',
    'scoped-rebound-closure-wrapper-flags-retain-selected-receiver': b'W:1:1:1:1:1;U:1:1:1:1;B:1:1:1:1;R:1:1:1;E:1:1:1:1:1:1;',
    'anonymous-scope-closure-warnings-use-two-c-strings': b'A:1:1:1:1;N:1:1:1;B;E:1;',
    'closure-duplicate-use-before-repeated-deprecated': b'',
    'class-scoped-nodiscard-void-closure-before-bad-body': b'',
}
STATIC = {
    'closure-duplicate-use-before-repeated-deprecated': ('Cannot use variable $token twice', 7),
    'class-scoped-nodiscard-void-closure-before-bad-body':
        ('A void method does not return a value, but #[\\NoDiscard] requires a return value', 8),
}
EXIT_CODES = {name: 255 if name in STATIC else 0 for name in CASES}
STATUSES = {name: 'static_rejection' for name in STATIC}


def expected_stderr(name, path):
    if name in STATIC:
        message, line = STATIC[name]
        return (b'Fatal error: ' + message.encode() + b' in ' + bytes(path) + b' on line ' +
                str(line).encode() + b'\nStack trace:\n#0 {main}\n')
    return b''

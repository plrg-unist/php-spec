"""Native-first NoDiscard context, call-phase and real-owner discriminators."""


def php(lines):
    return ('\n'.join(['<?php'] + lines) + '\n').encode()


def at80(prefix, expression, suffix):
    lines = ['<?php'] + prefix
    assert len(lines) <= 79
    lines += [''] * (79 - len(lines))
    lines += [expression] + suffix
    assert lines[79] == expression
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'alias-binary-message-used-void-nested-discard': php([
        'use NoDiscard as MustKeep;',
        '#[MustKeep(message: "use\\0me")]',
        'function pulse() {',
        '    $GLOBALS["body"]++; echo "B:", $GLOBALS["body"], ";";',
        '    return $GLOBALS["body"];',
        '}',
        'function context_notice($level, $message, $file, $line) {',
        '    $GLOBALS["calls"]++;',
        '    echo "H:", $level === E_USER_WARNING, ":", $message === "The return value of function pulse() should either be used or intentionally ignored by casting it as (void), use\\0me", ":", $file === __FILE__, ":", $line === $GLOBALS["expectedLine"], ":", $GLOBALS["body"], ";";',
        '    return true;',
        '}',
        '$body = 0; $calls = 0;',
        'set_error_handler("context_notice");',
        '$value = pulse();',
        '(void) pulse();',
        'pulse() + 1;',
        'true ? pulse() : pulse();',
        '$expectedLine = __LINE__ + 1;',
        'pulse();',
        '$expectedLine = __LINE__ + 1;',
        '@pulse();',
        'restore_error_handler();',
        'echo "E:", $value === 1, ":", $body === 6, ":", $calls === 2, ";";',
    ]),
    'warning-throw-before-recv-sent-owner-retirement': at80([
        'class SentPayload {',
        '    public function __destruct() { echo "D:", $GLOBALS["body"] === 0, ";"; }',
        '}',
        '#[\\NoDiscard]',
        'function take(int $value) { $GLOBALS["body"]++; echo "BAD-B;"; return 1; }',
        'function throw_notice($level, $message, $file, $line) {',
        '    $GLOBALS["calls"]++;',
        '    echo "H:", $level === E_USER_WARNING, ":", $message === "The return value of function take() should either be used or intentionally ignored by casting it as (void)", ":", $line === 80, ";";',
        '    $GLOBALS["arg"] = null;',
        '    echo "K:", $GLOBALS["weak"]->get() instanceof SentPayload, ";";',
        '    throw $GLOBALS["failure"];',
        '}',
        '$body = 0; $calls = 0; $arg = new SentPayload();',
        '$weak = WeakReference::create($arg); $failure = new Exception("supplied");',
        'set_error_handler("throw_notice");',
        'try {',
    ], '    take($arg);', [
        '    echo "BAD-R;";',
        '} catch (Throwable $caught) {',
        '    echo "C:", $caught === $failure, ":", $weak->get() === null, ":", $body === 0, ";";',
        '}',
        'restore_error_handler();',
        'echo "E:", $calls === 1, ";";',
    ]),
    'inherited-method-receiver-and-selected-reference': at80([
        'class AttrBase {',
        '    #[\\NoDiscard(message: null)]',
        '    public function act(&$slot) {',
        '        echo "B:", $slot, ":", $GLOBALS["weak"]->get() === $this, ";";',
        '        $slot = 20; return $slot;',
        '    }',
        '}',
        'class AttrChild extends AttrBase {',
        '    public function __destruct() { echo "D:", $GLOBALS["outside"] === 20, ";"; }',
        '}',
        'function method_notice($level, $message, $file, $line) {',
        '    $GLOBALS["calls"]++;',
        '    $GLOBALS["receiver"] = null; $GLOBALS["outside"] = 9;',
        '    $GLOBALS["arg"] =& $GLOBALS["replacement"];',
        '    echo "H:", $level === E_USER_WARNING, ":", $message === "The return value of method AttrBase::act() should either be used or intentionally ignored by casting it as (void)", ":", $GLOBALS["weak"]->get() instanceof AttrChild, ";";',
        '    return true;',
        '}',
        '$calls = 0; $receiver = new AttrChild(); $weak = WeakReference::create($receiver);',
        '$arg = 5; $outside =& $arg; $replacement = 33;',
        'set_error_handler("method_notice");',
    ], '$receiver->act($arg);', [
        'restore_error_handler();',
        'echo "E:", $outside === 20, ":", $arg === 33, ":", $weak->get() === null, ":", $calls === 1, ";";',
    ]),
    'positional-recv-versus-required-named-hole': at80([
        '#[\\NoDiscard]',
        'function need($a, $b) { echo "BAD-B;"; return 1; }',
        'function priority_notice($level, $message, $file, $line) {',
        '    $GLOBALS["calls"]++;',
        '    echo "H:", $level === E_USER_WARNING, ":", $line === 80, ";";',
        '    return true;',
        '}',
        '$calls = 0; set_error_handler("priority_notice");',
        'try {',
    ], '    need();', [
        '    echo "BAD-P;";',
        '} catch (ArgumentCountError $caught) {',
        '    echo "P:", $calls === 1, ":", $caught->getMessage() === "Too few arguments to function need(), 0 passed in " . __FILE__ . " on line 80 and exactly 2 expected", ";";',
        '}',
        'try {',
        '    need(b: 2);',
        '    echo "BAD-N;";',
        '} catch (ArgumentCountError $caught) {',
        "    echo 'N:', $calls === 1, ':', $caught->getMessage() === 'need(): Argument #1 ($a) not passed', ';';",
        '}',
        'restore_error_handler();',
        'echo "E:", $calls === 1, ";";',
    ]),
    'converted-closure-direct-versus-explicit-invoke': php([
        '#[\\NoDiscard]',
        'function marked() { $GLOBALS["body"]++; echo "B:", $GLOBALS["body"], ";"; return 1; }',
        'function closure_notice($level, $message, $file, $line) {',
        '    $GLOBALS["calls"]++;',
        '    echo "H:", $level === E_USER_WARNING, ":", $message === "The return value of function marked() should either be used or intentionally ignored by casting it as (void)", ":", $GLOBALS["body"] === 0, ";";',
        '    return true;',
        '}',
        '$body = 0; $calls = 0; set_error_handler("closure_notice");',
        '$closure = marked(...);',
        '$closure();',
        '$closure->__invoke();',
        '(void) $closure();',
        'restore_error_handler();',
        'echo "E:", $body === 3, ":", $calls === 1, ";";',
    ]),
    'for-list-frees-versus-last-condition-use': at80([
        '#[\\NoDiscard]',
        'function probe($value) { $GLOBALS["body"]++; echo "B:", $value, ";"; return $value; }',
        'function list_notice($level, $message, $file, $line) {',
        '    $GLOBALS["calls"]++;',
        '    echo "H:", $level === E_USER_WARNING, ":", $line === 80, ";";',
        '    return true;',
        '}',
        '$body = 0; $calls = 0; $loops = 0; set_error_handler("list_notice");',
    ], 'for (probe(10), probe(11); probe(12), probe($loops < 1 ? 1 : 0); probe(13), probe(14)) { $loops++; }', [
        'restore_error_handler();',
        'echo "E:", $body === 8, ":", $calls === 6, ":", $loops === 1, ";";',
    ]),
}

EXPECTED = {
    'alias-binary-message-used-void-nested-discard': b'B:1;B:2;B:3;B:4;H:1:1:1:1:4;B:5;H:1:1:1:1:5;B:6;E:1:1:1;',
    'warning-throw-before-recv-sent-owner-retirement': b'H:1:1:1;K:1;D:1;C:1:1:1;E:1;',
    'inherited-method-receiver-and-selected-reference': b'H:1:1:1;B:9:1;D:1;E:1:1:1:1;',
    'positional-recv-versus-required-named-hole': b'H:1:1;P:1:1;N:1:1;E:1;',
    'converted-closure-direct-versus-explicit-invoke': b'H:1:1:1;B:1;B:2;B:3;E:1:1;',
    'for-list-frees-versus-last-condition-use': b'H:1:1;B:10;H:1:1;B:11;H:1:1;B:12;B:1;H:1:1;B:13;H:1:1;B:14;H:1:1;B:12;B:0;E:1:1:1;',
}

# Independently frozen fixed/EXTRA/NAMED/receiver cleanup-order original.
lines = [
    '<?php',
    'class PendingArg {',
    '    public $tag;',
    '    public function __construct($tag) { $this->tag = $tag; }',
    '    public function __destruct() {',
    '        echo $this->tag, ":", $GLOBALS["weakReceiver"]->get() instanceof PendingOwner, ":", $GLOBALS["body"] === 0, ";";',
    '    }',
    '}',
    'class PendingOwner {',
    '    #[\\NoDiscard]',
    '    public function act($fixed, ...$extra) { $GLOBALS["body"]++; echo "BAD-B;"; return 1; }',
    '    public function __destruct() {',
    '        echo "R:", $GLOBALS["weakA"]->get() === null, ":", $GLOBALS["weakB"]->get() === null, ":", $GLOBALS["weakN"]->get() === null, ":", $GLOBALS["body"] === 0, ";";',
    '    }',
    '}',
    'function order_notice($level, $message, $file, $line) {',
    '    $GLOBALS["calls"]++;',
    '    echo "H:", $level === E_USER_WARNING, ":", $message === "The return value of method PendingOwner::act() should either be used or intentionally ignored by casting it as (void)", ":", $line === 80, ";";',
    '    $GLOBALS["receiver"] = null; $GLOBALS["a"] = null; $GLOBALS["b"] = null; $GLOBALS["n"] = null;',
    '    echo "K:", $GLOBALS["weakReceiver"]->get() instanceof PendingOwner, ":", $GLOBALS["weakA"]->get() instanceof PendingArg, ":", $GLOBALS["weakB"]->get() instanceof PendingArg, ":", $GLOBALS["weakN"]->get() instanceof PendingArg, ";";',
    '    throw $GLOBALS["failure"];',
    '}',
    '$body = 0; $calls = 0; $receiver = new PendingOwner();',
    '$a = new PendingArg("A"); $b = new PendingArg("B"); $n = new PendingArg("N");',
    '$weakReceiver = WeakReference::create($receiver);',
    '$weakA = WeakReference::create($a); $weakB = WeakReference::create($b); $weakN = WeakReference::create($n);',
    '$failure = new Exception("supplied-order"); set_error_handler("order_notice");',
    'try {',
]
lines += [''] * (79 - len(lines))
lines += [
    '    $receiver->act($a, $b, named: $n);',
    '    echo "BAD-R;";',
    '} catch (Throwable $caught) {',
    '    echo "C:", $caught === $failure, ":", $weakA->get() === null, ":", $weakB->get() === null, ":", $weakN->get() === null, ":", $weakReceiver->get() === null, ":", $body === 0, ";";',
    '}',
    'restore_error_handler(); echo "E:", $calls === 1, ";";',
]
assert lines[79] == '    $receiver->act($a, $b, named: $n);'
CASES.update({'fixed-extra-named-receiver-throw-release-order': ('\n'.join(lines) + '\n').encode()})
EXPECTED.update({'fixed-extra-named-receiver-throw-release-order': b'H:1:1:1;K:1:1:1:1;A:1:1;B:1:1;N:1:1;R:1:1:1:1;C:1:1:1:1:1:1;E:1;'})

# New actual-tail NoDiscard/FINAL callback intersection; native-first join control.
CASES['marked-final-api-versus-inner-source-discard'] = php([
    'function attr_notice($level, $message, $file, $line) {',
    '    $GLOBALS["warnings"]++;',
    '    $GLOBALS["level_ok"] = $level === 512;',
    '    $GLOBALS["message_ok"] = $message === "The return value of function attr_inner() should either be used or intentionally ignored by casting it as (void)";',
    '    $GLOBALS["source_ok"] = $file === __FILE__ && $line === 13;',
    '    return true;',
    '}',
    '#[\\NoDiscard]',
    'function attr_inner() { $GLOBALS["inner"]++; return 7; }',
    '#[\\NoDiscard]',
    'function attr_final($bytes, $phase) {',
    '    attr_inner();',
    '    (void) attr_inner();',
    '    $used = attr_inner();',
    '    return $bytes . ":" . ($phase === 9) . ":" . ($GLOBALS["warnings"] === 1) . ":" . $GLOBALS["level_ok"] . ":" . $GLOBALS["message_ok"] . ":" . $GLOBALS["source_ok"] . ":" . ($GLOBALS["inner"] === 3) . ":" . ($used === 7);',
    '}',
    '$warnings = 0; $inner = 0; $level_ok = false; $message_ok = false; $source_ok = false;',
    'set_error_handler("attr_notice");',
    'ob_start("attr_final");',
    'echo "seed";',
])
EXPECTED['marked-final-api-versus-inner-source-discard'] = b'seed:1:1:1:1:1:1:1'

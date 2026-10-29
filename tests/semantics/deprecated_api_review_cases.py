"""Frozen independent selected API callback PHP payloads and native streams."""


def at80(prefix, operation, suffix):
    lines = ['<?php'] + prefix
    assert len(lines) <= 79
    lines += [''] * (79 - len(lines)) + [operation] + suffix
    assert lines[79] == operation
    return ('\n'.join(lines) + '\n').encode()


CASES = {
    'assert-borrowed-closure-throw-before-argument-copies': at80([
        'class Carrier {',
        '    #[\\Deprecated("old", "4"), \\NoDiscard]',
        '    public function retired(&$file, $line, $code, $description = null) { $GLOBALS["body"]++; echo "BAD-BODY;"; return 7; }',
        '    public function __destruct() { echo "X:", $GLOBALS["body"] === 0, ";"; }',
        '}',
        'function notice($level, $message, $file, $line) {',
        '    if ($level === 8192) { return true; }',
        '    if ($level === 16384) {',
        '        @assert_options(ASSERT_CALLBACK, null); $GLOBALS["callback"] = null;',
        '        $probe = new Exception("phase"); $trace = $probe->getTrace();',
        '        $caller = $trace[0]["function"] === "notice" && $trace[1]["function"] === "assert" && !isset($trace[2]);',
        '        echo "D:", $message === "Method Carrier::retired() is deprecated since 4, old", ":", $GLOBALS["weak_closure"]->get() === $GLOBALS["held"], ":", $GLOBALS["weak_receiver"]->get() !== null, ":", $caller, ";";',
        '        throw $GLOBALS["saved"];',
        '    }',
        '    $GLOBALS["other"]++; echo "BAD-WARNING;"; return true;',
        '}',
        '$body = 0; $other = 0; $saved = new Exception("supplied");',
        '$receiver = new Carrier(); $callback = $receiver->retired(...); $held = $callback;',
        '$weak_receiver = WeakReference::create($receiver); $weak_closure = WeakReference::create($callback); $receiver = null;',
        '@assert_options(ASSERT_EXCEPTION, 0); @assert_options(ASSERT_WARNING, 0); @assert_options(ASSERT_CALLBACK, $callback);',
        'set_error_handler("notice");',
    ], 'try { assert(false); } catch (Exception $caught) { echo "C:", $caught === $saved, ":", $body === 0, ":", $other === 0, ":", $weak_closure->get() === $held, ";"; }', [
        'restore_error_handler(); $held = null;',
        'echo "E:", $weak_closure->get() === null, ":", $weak_receiver->get() === null, ";";',
    ]),
    'assert-resumed-fresh-references-and-cached-description': at80([
        '#[\\Deprecated("cached", "5"), \\NoDiscard]',
        'function cached_assert(&$file, $line, $code, &$description) {',
        '    $GLOBALS["body"]++;',
        '    echo "B:", $file === __FILE__, ":", $line === 80, ":", $code === null, ":", $description === "original", ":", $GLOBALS["description"] === 99, ";";',
        '    $file = "fresh file"; $description = "fresh description"; return false;',
        '}',
        'function notice($level, $message, $file, $line) {',
        '    if ($level === 8192) { return true; }',
        '    if ($level === 16384) {',
        '        $GLOBALS["deprecated"]++; $GLOBALS["description"] = 99;',
        '        echo "D:", $message === "Function cached_assert() is deprecated since 5, cached", ";"; return true;',
        '    }',
        '    if ($level === 2) {',
        '        $GLOBALS["warnings"]++;',
        '        if ($GLOBALS["warnings"] === 1) { $expected = \'cached_assert(): Argument #1 ($file) must be passed by reference, value given\'; }',
        "        else { $expected = 'cached_assert(): Argument #4 ($description) must be passed by reference, value given'; }",
        '        echo "W:", $message === $expected, ":", $GLOBALS["body"] === 0, ";"; return true;',
        '    }',
        '    echo "BAD-WARNING;"; return true;',
        '}',
        '$body = 0; $deprecated = 0; $warnings = 0; $description = "original";',
        '@assert_options(ASSERT_EXCEPTION, 0); @assert_options(ASSERT_WARNING, 0); @assert_options(ASSERT_CALLBACK, "cached_assert");',
        'set_error_handler("notice");',
    ], 'assert(false, $description);', [
        'restore_error_handler();',
        'echo "E:", $deprecated === 1, ":", $warnings === 2, ":", $body === 1, ":", $description === 99, ";";',
        '@assert_options(ASSERT_CALLBACK, null);',
    ]),
    'error-handler-mask-and-moved-callback-owner': at80([
        'class OldHandler {',
        '    #[\\Deprecated("old", "6"), \\NoDiscard]',
        '    public function __invoke(&$level, $message, $file, $line) {',
        '        $GLOBALS["body"]++;',
        '        $expected = $GLOBALS["body"] === 1 ? "first" : "second";',
        '        echo "B:", $level === 512, ":", $message === $expected, ":", $GLOBALS["weak"]->get() === $this, ";";',
        '        if ($GLOBALS["body"] === 2) { restore_error_handler(); set_error_handler("next_notice"); echo "R:", $GLOBALS["weak"]->get() === $this, ";"; }',
        '        return true;',
        '    }',
        '    public function __destruct() { echo "X:", $GLOBALS["body"] === 2, ";"; }',
        '}',
        'function next_notice($level, $message, $file, $line) { echo "N:", $level === 512, ":", $message === "after", ";"; return true; }',
        '$body = 0; $handler = new OldHandler(); $weak = WeakReference::create($handler);',
        'set_error_handler($handler); $handler = null;',
    ], '@trigger_error("first", E_USER_WARNING); trigger_error("second", E_USER_WARNING);', [
        'echo "E:", $body === 2, ":", $weak->get() === null, ";";',
        'trigger_error("after", E_USER_WARNING); restore_error_handler();',
    ]),
    'unmarked-assert-active-handler-replacement-and-fresh-refs': at80([
        'function unmarked_assert(&$file, $line, &$code) {',
        '    $GLOBALS["body"]++; echo "B:", $file === __FILE__, ":", $line === 80, ":", $code === null, ":", func_num_args() === 4, ";";',
        '    $file = "fresh file"; $code = true; return false;',
        '}',
        'function first_notice($level, $message, $file, $line) {',
        '    $GLOBALS["first"]++;',
        '    echo "W1:", $level === 2 && $message === \'unmarked_assert(): Argument #1 ($file) must be passed by reference, value given\', ";";',
        '    restore_error_handler(); set_error_handler("next_notice"); return true;',
        '}',
        'function next_notice($level, $message, $file, $line) {',
        '    $GLOBALS["next"]++;',
        '    echo "W3:", $level === 2 && $message === \'unmarked_assert(): Argument #3 ($code) must be passed by reference, value given\', ":", $GLOBALS["body"] === 0, ";";',
        '    return true;',
        '}',
        '$body = 0; $first = 0; $next = 0;',
        '@assert_options(ASSERT_EXCEPTION, 0); @assert_options(ASSERT_WARNING, 0); @assert_options(ASSERT_CALLBACK, "unmarked_assert");',
        'set_error_handler("first_notice");',
    ], 'assert(false);', [
        'restore_error_handler(); echo "E:", $first === 1, ":", $next === 1, ":", $body === 1, ";";',
        '@assert_options(ASSERT_CALLBACK, null);',
    ]),
    'assert-closure-entry-retain-outlives-last-outside-alias': at80([
        'class CarrierRetained {',
        '    #[\\Deprecated("retained", "7"), \\NoDiscard]',
        '    public function retired(&$file, $line, $code, $description = null) {',
        '        $GLOBALS["body"]++; echo "B:", $GLOBALS["weak_closure"]->get() === $GLOBALS["held"], ":", $GLOBALS["weak_receiver"]->get() === $this, ";";',
        '        $GLOBALS["held"] = null;',
        '        echo "K:", $GLOBALS["weak_closure"]->get() !== null, ":", $GLOBALS["weak_receiver"]->get() === $this, ";"; return 7;',
        '    }',
        '    public function __destruct() { echo "X:", $GLOBALS["body"] === 1, ";"; }',
        '}',
        'function notice($level, $message, $file, $line) {',
        '    if ($level === 8192) { return true; }',
        '    if ($level === 16384) {',
        '        $GLOBALS["deprecated"]++; @assert_options(ASSERT_CALLBACK, null); $GLOBALS["callback"] = null;',
        '        echo "D:", $message === "Method CarrierRetained::retired() is deprecated since 7, retained", ":", $GLOBALS["weak_closure"]->get() === $GLOBALS["held"], ";"; return true;',
        '    }',
        '    $GLOBALS["warnings"]++;',
        '    echo "W:", $level === 2 && $message === \'CarrierRetained::retired(): Argument #1 ($file) must be passed by reference, value given\', ":", $GLOBALS["body"] === 0, ";"; return true;',
        '}',
        '$body = 0; $warnings = 0; $deprecated = 0; $receiver = new CarrierRetained();',
        '$callback = $receiver->retired(...); $held = $callback;',
        '$weak_closure = WeakReference::create($callback); $weak_receiver = WeakReference::create($receiver); $receiver = null;',
        '@assert_options(ASSERT_EXCEPTION, 0); @assert_options(ASSERT_WARNING, 0); @assert_options(ASSERT_CALLBACK, $callback);',
        'set_error_handler("notice");',
    ], 'assert(false);', [
        'restore_error_handler(); echo "E:", $body === 1, ":", $weak_closure->get() === null, ":", $weak_receiver->get() === null, ":", $deprecated === 1, ":", $warnings === 1, ";";',
    ]),
    'assert-early-throw-enters-live-exception-policy': at80([
        '#[\\Deprecated("policy", "8")]',
        'function policy_assert(&$file, $line, $code, $description = null) { $GLOBALS["body"]++; echo "BAD-BODY;"; }',
        'function notice($level, $message, $file, $line) {',
        '    if ($level === 8192) { return true; }',
        '    if ($level === 16384) {',
        '        $GLOBALS["deprecated"]++; @assert_options(ASSERT_EXCEPTION, 1);',
        '        echo "D:", $message === "Function policy_assert() is deprecated since 8, policy", ";";',
        '        throw $GLOBALS["saved"];',
        '    }',
        '    $GLOBALS["other"]++; echo "BAD-WARNING;"; return true;',
        '}',
        '$body = 0; $deprecated = 0; $other = 0; $saved = new Exception("saved");',
        '@assert_options(ASSERT_EXCEPTION, 0); @assert_options(ASSERT_WARNING, 0); @assert_options(ASSERT_CALLBACK, "policy_assert");',
        'set_error_handler("notice");',
    ], 'try { assert(false, "flag policy"); } catch (AssertionError $failure) { echo "C:", $failure->getPrevious() === $saved, ":", $failure->getMessage() === "flag policy", ":", $body === 0, ":", $other === 0, ":", $deprecated === 1, ";"; }', [
        'restore_error_handler(); @assert_options(ASSERT_CALLBACK, null);',
    ]),
}

EXPECTED_STDOUT = {
    'assert-borrowed-closure-throw-before-argument-copies': b'D:1:1:1:1;C:1:1:1:1;X:1;E:1:1;',
    'assert-resumed-fresh-references-and-cached-description': b'D:1;W:1:1;W:1:1;B:1:1:1:1:1;E:1:1:1:1;',
    'error-handler-mask-and-moved-callback-owner': b'B:1:1:1;B:1:1:1;R:1;X:1;E:1:1;N:1:1;',
    'unmarked-assert-active-handler-replacement-and-fresh-refs': b'W1:1;W3:1:1;B:1:1:1:1;E:1:1:1;',
    'assert-closure-entry-retain-outlives-last-outside-alias': b'D:1:1;W:1:1;B:1:1;K:1:1;X:1;E:1:1:1:1:1;',
    'assert-early-throw-enters-live-exception-policy': b'D:1;C:1:1:1:1:1;',
}

STDERR_TEMPLATES = {
    'assert-borrowed-closure-throw-before-argument-copies': b'',
    'assert-resumed-fresh-references-and-cached-description': b'',
    'error-handler-mask-and-moved-callback-owner': b'Deprecated: Method OldHandler::__invoke() is deprecated since 6, old in {file} on line 80\nWarning: OldHandler::__invoke(): Argument #1 ($level) must be passed by reference, value given in {file} on line 80\n',
    'unmarked-assert-active-handler-replacement-and-fresh-refs': b'',
    'assert-closure-entry-retain-outlives-last-outside-alias': b'',
    'assert-early-throw-enters-live-exception-policy': b'',
}

def expected_stderr(name, path):
    return STDERR_TEMPLATES[name].replace(b'{file}', bytes(path))

EXIT_CODES = {name: 0 for name in CASES}

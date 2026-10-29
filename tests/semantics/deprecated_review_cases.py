"""Frozen independent Deprecated VM phases and explicit wrapper/API boundary."""


def at80(prefix, operation, suffix):
    lines = ['<?php'] + prefix
    assert len(lines) <= 79
    lines += [''] * (79 - len(lines)) + [operation] + suffix
    assert lines[79] == operation
    return ('\n'.join(lines) + '\n').encode()


ND = 'The return value of function captured() should either be used or intentionally ignored by casting it as (void)'

CASES = {
    'inherited-reference-receiver-through-both-warnings': at80([
        'class LegacyBase {',
        '    #[\\Deprecated("old", "9"), \\NoDiscard]',
        '    public function act(&$slot) {',
        '        echo "B:", $slot === 20, ":", $GLOBALS["weak"]->get() === $this, ";";',
        '        $slot = 25; return 7;',
        '    }',
        '}',
        'class LegacyChild extends LegacyBase {',
        '    public function __destruct() { echo "R:", $GLOBALS["outside"] === 25, ";"; }',
        '}',
        'function notice($level, $message, $file, $line) {',
        '    $GLOBALS["calls"]++;',
        '    $probe = new Exception("phase"); $trace = $probe->getTrace();',
        '    $caller = $trace[0]["function"] === "notice" && !isset($trace[1]);',
        '    if ($level === 16384) {',
        '        $GLOBALS["receiver"] = null; $GLOBALS["outside"] = 9;',
        '        $GLOBALS["arg"] =& $GLOBALS["replacement"];',
        '        echo "D:", $message === "Method LegacyBase::act() is deprecated since 9, old", ":", $GLOBALS["weak"]->get() !== null, ":", $caller, ":", $line === 80, ";";',
        '    } else {',
        '        echo "N:", $level === 512, ":", $message === "The return value of method LegacyBase::act() should either be used or intentionally ignored by casting it as (void)", ":", $GLOBALS["outside"] === 9, ":", $GLOBALS["arg"] === 33, ":", $caller, ";";',
        '        $GLOBALS["outside"] = 20;',
        '    }',
        '    return true;',
        '}',
        '$receiver = new LegacyChild(); $weak = WeakReference::create($receiver);',
        '$arg = 5; $outside =& $arg; $replacement = 33;',
        '$calls = 0; set_error_handler("notice");',
    ], '$receiver->act($arg);', [
        'restore_error_handler();',
        'echo "E:", $calls === 2, ":", $outside === 25, ":", $arg === 33, ":", $weak->get() === null, ";";',
    ]),
    'direct-named-closure-deprecated-versus-result-use': at80([
        '#[\\Deprecated("old", "9"), \\NoDiscard]',
        'function captured() { $GLOBALS["body"]++; echo "B:", $GLOBALS["body"], ";"; return 7; }',
        'function notice($level, $message, $file, $line) {',
        '    if ($level === 16384) {',
        '        $GLOBALS["deprecated"]++; echo "D:", $message === "Function captured() is deprecated since 9, old", ":", $line === 80, ";";',
        '    } else {',
        '        $GLOBALS["nodiscard"]++; echo "N:", $level === 512, ":", $message === "' + ND + '", ";";',
        '    }',
        '    return true;',
        '}',
        '$body = 0; $deprecated = 0; $nodiscard = 0; $closure = captured(...);',
        'set_error_handler("notice");',
    ], '$closure(); (void) $closure(); $used = $closure();', [
        'restore_error_handler(); echo "E:", $deprecated === 3, ":", $nodiscard === 1, ":", $body === 3, ":", $used === 7, ";";',
    ]),
    'handler-replacement-retires-before-second-warning': at80([
        '#[\\NoDiscard, \\Deprecated]',
        'function selected() { $GLOBALS["body"]++; echo "B;"; return 7; }',
        'class FirstHandler {',
        '    public function __invoke($level, $message, $file, $line) {',
        '        echo "D:", $level === 16384, ":", $message === "Function selected() is deprecated", ":", $GLOBALS["weak_handler"]->get() === $this, ";";',
        '        restore_error_handler(); set_error_handler("next_notice"); return true;',
        '    }',
        '    public function __destruct() { $GLOBALS["retired"] = 1; echo "X:", $GLOBALS["body"] === 0, ";"; }',
        '}',
        'function next_notice($level, $message, $file, $line) {',
        '    echo "N:", $level === 512, ":", $message === "The return value of function selected() should either be used or intentionally ignored by casting it as (void)", ":", $GLOBALS["retired"] === 1, ":", $GLOBALS["weak_handler"]->get() === null, ":", $GLOBALS["body"] === 0, ";";',
        '    return true;',
        '}',
        '$body = 0; $retired = 0; $handler = new FirstHandler();',
        '$weak_handler = WeakReference::create($handler); set_error_handler($handler); $handler = null;',
    ], 'selected();', [
        'restore_error_handler(); echo "E:", $body === 1, ":", $retired === 1, ":", $weak_handler->get() === null, ";";',
    ]),
    'masked-handler-false-default-deprecation': at80([
        '#[\\Deprecated]',
        'function masked() { $GLOBALS["body"]++; echo "B:", $GLOBALS["body"], ";"; return 7; }',
        'function notice($level, $message, $file, $line) {',
        '    $GLOBALS["calls"]++; $reported = (error_reporting() & 16384) !== 0;',
        '    echo "H:", $level === 16384, ":", $message === "Function masked() is deprecated", ":", $reported === $GLOBALS["expected_reporting"], ":", $GLOBALS["body"], ";";',
        '    return false;',
        '}',
        '$body = 0; $calls = 0; set_error_handler("notice");',
    ], '$expected_reporting = false; @masked(); $expected_reporting = true; masked();', [
        'restore_error_handler(); echo "E:", $body === 2, ":", $calls === 2, ";";',
    ]),
    'explicit-closure-invoke-internal-then-api-boundary': at80([
        '#[\\Deprecated("old", "9"), \\NoDiscard]',
        'function captured() { $GLOBALS["body"]++; echo "B;"; return 7; }',
        'function notice($level, $message, $file, $line) {',
        '    $GLOBALS["calls"]++;',
        '    if ($GLOBALS["calls"] === 1) {',
        '        echo "W:", $level === 8192, ":", $message === "Method Closure::__invoke() is deprecated since 9, old", ";";',
        '    } else {',
        '        echo "U:", $level === 16384, ":", $message === "Function captured() is deprecated since 9, old", ";";',
        '    }',
        '    return true;',
        '}',
        '$calls = 0; $body = 0; $closure = captured(...); set_error_handler("notice");',
    ], '$closure->__invoke();', [
        'restore_error_handler(); echo "E:", $calls === 2, ":", $body === 1, ";";',
    ]),
}

EXPECTED_STDOUT = {
    'inherited-reference-receiver-through-both-warnings': b'D:1:1:1:1;N:1:1:1:1:1;B:1:1;R:1;E:1:1:1:1;',
    'direct-named-closure-deprecated-versus-result-use': b'D:1:1;N:1:1;B:1;D:1:1;B:2;D:1:1;B:3;E:1:1:1:1;',
    'handler-replacement-retires-before-second-warning': b'D:1:1:1;X:1;N:1:1:1:1:1;B;E:1:1:1;',
    'masked-handler-false-default-deprecation': b'H:1:1:1:0;B:1;H:1:1:1:1;B:2;E:1:1;',
    'explicit-closure-invoke-internal-then-api-boundary': b'W:1:1;U:1:1;B;E:1:1;',
}

EXIT_CODES = {}
STATUSES = {}
CONTROLS = set()
BOUNDARIES = {'explicit-closure-invoke-internal-then-api-boundary': 'Deprecated internal API timing'}


def expected_stderr(name, path):
    if name == 'masked-handler-false-default-deprecation':
        return b'Deprecated: Function masked() is deprecated in ' + bytes(path) + b' on line 80\n'
    return b''


# Separate native-first API-preparation refusal; zero agreement credit.
CASES.update({'assert-api-byref-throw-priority-boundary': b'<?php\n#[\\Deprecated]\nfunction retired_assert(&$file, $line, $code, $description = null) { $GLOBALS["body"]++; echo "BODY;"; }\nfunction notice($level, $message, $file, $line) {\n    if ($level === 8192) { return true; }\n    if ($level === 16384) {\n        $GLOBALS["deprecated"]++; echo "D:", $message === "Function retired_assert() is deprecated", ";"; return true;\n    }\n    if ($level === 2) {\n        echo "W:", $message === "retired_assert(): Argument #1 ($file) must be passed by reference, value given", ";";\n        throw $GLOBALS["saved"];\n    }\n    return false;\n}\n$body = 0; $deprecated = 0; $saved = new Exception("supplied"); set_error_handler("notice");\nini_set("assert.exception", "0"); ini_set("assert.warning", "0");\nassert_options(ASSERT_CALLBACK, "retired_assert");\necho "B|";\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\ntry { assert(false); } catch (Exception $caught) { echo "C:", $caught === $saved, ":", $body === 0, ":", $deprecated === 1, ";"; }\nrestore_error_handler();\n'})
EXPECTED_STDOUT.update({'assert-api-byref-throw-priority-boundary': b'B|D:1;W:1;C:1:1:1;'})
BOUNDARIES.update({'assert-api-byref-throw-priority-boundary': 'Deprecated internal API timing'})
BOUNDARY_STDOUT = {'assert-api-byref-throw-priority-boundary': b'B|'}

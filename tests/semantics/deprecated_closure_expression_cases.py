"""Native-first builtin attributes on real Closure and arrow expressions."""
from deprecated_review_cases import at80


def reference_closure():
    keyword = 'function () use (&$value) {'
    prefix = [
        'namespace ExprFlags;',
        'use Deprecated as Old;',
        'use NoDiscard as MustKeep;',
        '$body = 0; $calls = 0; $value = 1;',
        '$closure =',
        '#[Old(message: "old", since: "9"), MustKeep("consume")]',
        keyword,
        '    $GLOBALS["body"]++; echo "B:", $value === 7, ":", $GLOBALS["weak"]->get() !== null, ";"; return 7;',
        '};',
    ]
    line = prefix.index(keyword) + 2
    prefix += [
        '$expected_name = "{closure:" . __FILE__ . ":' + str(line) + '}";',
        'function notice($level, $message, $file, $line) {',
        '    $GLOBALS["calls"]++;',
        '    if ($level === 16384) {',
        '        $GLOBALS["value"] = 4; $GLOBALS["closure"] = null;',
        '        echo "D:", $message === "Function " . $GLOBALS["expected_name"] . "() is deprecated since 9, old", ":", $file === __FILE__ && $line === 80, ":", $GLOBALS["body"] === 0, ":", $GLOBALS["weak"]->get() !== null, ";"; return true;',
        '    }',
        '    if ($level === 512) {',
        '        $GLOBALS["value"] = 7;',
        '        echo "N:", $message === "The return value of function " . $GLOBALS["expected_name"] . "() should either be used or intentionally ignored by casting it as (void), consume", ":", $file === __FILE__ && $line === 80, ":", $GLOBALS["body"] === 0, ":", $GLOBALS["weak"]->get() !== null, ";"; return true;',
        '    }',
        '    echo "BAD-WARNING;"; return true;',
        '}',
        '$weak = \\WeakReference::create($closure); set_error_handler("ExprFlags\\\\notice");',
    ]
    return at80(prefix, '$closure();', [
        'restore_error_handler(); echo "E:", $calls === 2, ":", $body === 1, ":", $value === 7, ":", $weak->get() === null, ";";',
    ])


def static_arrow():
    keyword = 'fn() => record($initial);'
    prefix = [
        'function record($value) { $GLOBALS["body"]++; echo "B:", $value === 3, ";"; return $value; }',
        '$body = 0; $deprecated = 0; $nodiscard = 0; $initial = 3;',
        '$arrow =',
        '#[\\Deprecated("arrow", "2"), \\NoDiscard]',
        'static',
        keyword,
    ]
    line = prefix.index(keyword) + 2
    prefix += [
        '$expected_name = "{closure:" . __FILE__ . ":' + str(line) + '}";',
        'function notice($level, $message, $file, $line) {',
        '    if ($level === 16384) {',
        '        $GLOBALS["deprecated"]++; $GLOBALS["initial"] = 99;',
        '        echo "D:", $message === "Function " . $GLOBALS["expected_name"] . "() is deprecated since 2, arrow", ":", $file === __FILE__ && $line === 80, ":", $GLOBALS["body"] === $GLOBALS["deprecated"] - 1, ";"; return true;',
        '    }',
        '    if ($level === 512) {',
        '        $GLOBALS["nodiscard"]++;',
        '        echo "N:", $message === "The return value of function " . $GLOBALS["expected_name"] . "() should either be used or intentionally ignored by casting it as (void)", ":", $line === 80, ":", $GLOBALS["body"] === 1, ";"; return true;',
        '    }',
        '    echo "BAD-WARNING;"; return true;',
        '}',
        'set_error_handler("notice");',
    ]
    return at80(prefix, '$used = $arrow(); echo "U:", $used === 3, ";"; $arrow();', [
        'restore_error_handler(); echo "E:", $body === 2, ":", $deprecated === 2, ":", $nodiscard === 1, ":", $initial === 99, ";";',
    ])


def assert_closure():
    keyword = '        function ($file, $line, $code, $description = null) use (&$phase) {'
    prefix = [
        'class ApiOwner {',
        '    public function make(&$phase) {',
        '        return',
        '        #[\\Deprecated("api", "4"), \\NoDiscard]',
        keyword,
        '            $GLOBALS["body"]++; echo "B:", $file === __FILE__, ":", $line === 80, ":", $description === "probe", ":", $phase === 9, ":", $GLOBALS["weak"]->get() !== null, ":", $GLOBALS["weak_owner"]->get() === $this, ";"; return 7;',
        '        };',
        '    }',
        '}',
        '$body = 0; $replacement_body = 0; $deprecated = 0; $other = 0; $phase = 1;',
        '$owner = new ApiOwner(); $callback = $owner->make($phase);',
        '$weak_owner = WeakReference::create($owner); $owner = null;',
    ]
    line = prefix.index(keyword) + 2
    prefix += [
        '$expected_name = "{closure:ApiOwner::make():' + str(line) + '}";',
        'function replacement($file, $line, $code, $description = null) { $GLOBALS["replacement_body"]++; echo "BAD-REPLACEMENT;"; }',
        'function notice($level, $message, $file, $line) {',
        '    if ($level === 8192) { return true; }',
        '    if ($level === 16384) {',
        '        $GLOBALS["deprecated"]++; @assert_options(ASSERT_CALLBACK, "replacement");',
        '        $GLOBALS["callback"] = null; $GLOBALS["phase"] = 9;',
        '        echo "D:", $message === "Method ApiOwner::" . $GLOBALS["expected_name"] . "() is deprecated since 4, api", ":", $GLOBALS["body"] === 0 && $GLOBALS["replacement_body"] === 0, ":", $GLOBALS["weak"]->get() !== null, ":", $GLOBALS["weak_owner"]->get() !== null, ";"; return true;',
        '    }',
        '    $GLOBALS["other"]++; echo "BAD-WARNING;"; return true;',
        '}',
        '$weak = WeakReference::create($callback);',
        '$keep_callback = $callback;',
        '@assert_options(ASSERT_EXCEPTION, 0); @assert_options(ASSERT_WARNING, 0);',
        '@assert_options(ASSERT_CALLBACK, $callback); set_error_handler("notice");',
    ]
    return at80(prefix, 'assert(false, "probe");', [
        'restore_error_handler(); @assert_options(ASSERT_CALLBACK, null); $keep_callback = null;',
        'echo "E:", $deprecated === 1, ":", $other === 0, ":", $body === 1 && $replacement_body === 0, ":", $phase === 9, ":", $weak->get() === null, ":", $weak_owner->get() === null, ";";',
    ])


CASES = {
    'closure-expression-reference-capture-through-both-vm-warnings': reference_closure(),
    'arrow-expression-multiline-static-name-and-used-result': static_arrow(),
    'closure-expression-owned-assert-api-selection': assert_closure(),
    'arrow-expression-nodiscard-never-before-invalid-body': b'<?php\necho "BAD-RUN;";\n$arrow =\n#[\\NoDiscard]\nstatic\nfn(): never => 7;\n',
}
EXPECTED_STDOUT = {
    'closure-expression-reference-capture-through-both-vm-warnings': b'D:1:1:1:1;N:1:1:1:1;B:1:1;E:1:1:1:1;',
    'arrow-expression-multiline-static-name-and-used-result': b'D:1:1:1;B:1;U:1;D:1:1:1;N:1:1:1;B:1;E:1:1:1:1;',
    'closure-expression-owned-assert-api-selection': b'D:1:1:1:1;B:1:1:1:1:1:1;E:1:1:1:1:1:1;',
    'arrow-expression-nodiscard-never-before-invalid-body': b'',
}
EXIT_CODES = {name: 0 for name in CASES}
EXIT_CODES['arrow-expression-nodiscard-never-before-invalid-body'] = 255
STATUSES = {'arrow-expression-nodiscard-never-before-invalid-body': 'static_rejection'}


def expected_stderr(name, path):
    if name == 'arrow-expression-nodiscard-never-before-invalid-body':
        return (b'Fatal error: A never returning function does not return a value, but #[\\NoDiscard] requires a return value in ' +
                bytes(path) + b' on line 6\nStack trace:\n#0 {main}\n')
    return b''

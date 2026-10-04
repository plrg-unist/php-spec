#!/usr/bin/env python3
"""Ordinary dynamic NEW selectors, ordering, scopes and constructor admission."""
import argparse
import base64
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross

ROOT = Path(__file__).resolve().parents[2]
CASES = {
    'dynamic-new-string-namespace-alias': b"<?php\nnamespace Demo;\nuse Demo\\C as Alias;\nclass C { public function __construct($value = 0) { echo 'C', $value, '|'; } }\nfunction value() { echo 'V|'; return 9; }\n$class = '\\\\Demo\\\\C';\n$object = new $class(1);\necho $object::class, '|';\n$class = 'Alias';\ntry { new $class(value()); } catch (\\Error $e) { echo 'E|', $e->getMessage(), '|'; }\nnew Alias(2);\n",
    'dynamic-new-object-reference': b"<?php\nclass Base {}\nclass Child extends Base {\n    public function __construct($value) { echo 'C', $value, '|'; }\n    public function __toString() { echo 'S|'; return 'Missing'; }\n}\n$old = new Child(1);\n$reference =& $old;\n$copy = new $reference(2);\necho $copy::class, '/', $copy === $old ? 'same' : 'new';\n",
    'dynamic-new-reference-selection': b"<?php\nclass A { public function __construct($value) { echo 'A', $value, '|'; } }\nclass B { public function __construct($value) { echo 'B', $value, '|'; } }\nfunction value() { global $class; $class = 'A'; echo 'V|'; return 7; }\n$class = 'A';\n$reference =& $class;\n$class = 'B';\n$copy = new $reference(value());\necho $copy::class, '/', $class;\n",
    'dynamic-new-effectful-selector': b"<?php\nclass Chosen { public function __construct($value) { echo 'C', $value, '|'; } }\n$count = 0;\nfunction select_class() { global $count; $count++; echo 'P|'; return 'Chosen'; }\nfunction value() { echo 'V|'; return 4; }\n$copy = new (select_class())(value());\necho $copy::class, '/', $count;\n",
    'dynamic-new-invalid-selector-before-arguments': b"<?php\nfunction value() { echo 'V|'; return 1; }\nforeach ([null, false, true, 1, 1.5, []] as $class) {\n    try { new $class(value()); }\n    catch (Error $e) { echo $e::class, '/', $e->getMessage(), '|'; }\n}\n$class = 'Absent';\ntry { new $class(value()); } catch (Error $e) { echo $e::class, '/', $e->getMessage(); }\n",
    'dynamic-new-no-constructor-named': b"<?php\nclass Plain {}\nfunction value($number) { echo 'V', $number, '|'; return $number; }\n$class = 'Plain';\n$object = new $class(value(1), value(2));\necho $object::class, '|';\ntry { new $class(first: value(3), later: value(4)); }\ncatch (Error $e) { echo 'E|', $e->getMessage(); }\n",
    'dynamic-new-inherited-throwable': b"<?php\nclass E extends Exception { public $value = 7; }\nclass Message { public function __toString() { echo 'T|'; return 'message'; } }\n$selector = new E('seed', 1);\n$copy = new $selector(new Message, 3);\necho $copy::class, '/', $copy->getMessage(), '/', $copy->getCode(), '/', $copy->value, '/', $selector->getMessage();\n",
    'dynamic-new-undefined-handler-redefinition': b"<?php\nclass Ready {}\nset_error_handler(function($severity, $message, $file, $line) {\n    global $missing;\n    $missing = 'Ready';\n    echo 'H', $severity, '@', $line, '|';\n    return true;\n});\ntry {\n    $copy = new $missing;\n} catch (Error $e) { echo $e::class, '/', $e->getMessage(), '/', $missing; }\n",
    'dynamic-new-undefined-handler-throw': b"<?php\nclass Ready {}\nset_error_handler(function($severity, $message, $file, $line) {\n    global $missing;\n    $missing = 'Ready';\n    echo 'H|';\n    throw new Exception('stop');\n});\ntry { $copy = new $missing; }\ncatch (Throwable $e) { echo $e::class, '/', $e->getMessage(), '/', $e->getPrevious() === null ? 'none' : 'previous', '/', $missing; }\n",
    'dynamic-new-cold-class-before-arguments': b"<?php\nset_error_handler(function(...$arguments) { echo 'D', func_num_args(), '|'; return true; });\nclass Cold {\n    const X = E_STRICT;\n    public $value = 7;\n    public function __construct($argument) { echo 'C', $argument, '/', self::X, '/', $this->value, '|'; }\n}\nfunction value() { echo 'V|'; return 1; }\n$class = 'Cold';\nnew $class(value());\necho 'F';\n",
    'dynamic-new-cold-class-aborts-before-arguments': b"<?php\nclass Cold { const X = MISSING; }\nfunction value() { echo 'V|'; return 1; }\n$class = 'Cold';\ntry { new $class(value()); } catch (Error $e) { echo 'E|', $e->getMessage(); }\n",
    'dynamic-new-access-and-named-priority': b"<?php\nclass PrivateClass { private function __construct($argument) { echo 'C|'; } }\nclass Accepts { public function __construct($argument) { echo 'A|'; } }\nfunction value($number) { echo 'V', $number, '|'; return $number; }\n$class = 'PrivateClass';\ntry { new $class(missing: value(1), later: value(2)); }\ncatch (Error $e) { echo 'E|', $e->getMessage(), '|'; }\n$class = 'Accepts';\ntry { new $class(missing: value(3), later: value(4)); }\ncatch (Error $e) { echo 'E|', $e->getMessage(); }\n",
    'dynamic-new-noninstantiable-before-arguments': b"<?php\nabstract class AbstractClass {}\ninterface Contract {}\nfunction value() { echo 'V|'; return 1; }\nforeach (['AbstractClass', 'Contract'] as $class) {\n    try { new $class(value()); }\n    catch (Error $e) { echo 'E|', $e->getMessage(), '|'; }\n}\n",
    'dynamic-new-runtime-keywords-reduced': b"<?php\nclass ParentClass {}\nclass A extends ParentClass {\n    public static function run() {\n        foreach (['self', 'parent', 'static'] as $class) {\n            try { new $class; } catch (Error $e) { echo $e->getMessage(), '|'; }\n        }\n    }\n}\nclass B extends A {}\nB::run();\n",
    'dynamic-new-parser-and-folded-classnames': b"<?php\nnamespace Demo;\nuse Demo\\C as Alias;\nclass C {}\n$a = new ('Demo\\\\C');\necho $a::class, '|';\ntry { new ('Alias'); } catch (\\Error $e) { echo 'E|', $e->getMessage(), '|'; }\n$b = new ('Demo'.'\\\\C');\necho $b::class;\n",
    'dynamic-new-recursive-cold-selection': b"<?php\nfunction make($class) { return new $class; }\nset_error_handler(function() {\n    echo 'H|';\n    $inner = make('B');\n    echo 'T', $inner::class, '|';\n    return true;\n});\nclass A { const X = E_STRICT; public function __construct() { echo 'CA|'; } }\nclass B { public function __construct() { echo 'CB|'; } }\necho 'O|';\n$outer = make('A');\necho 'F', $outer::class;\n",
    'dynamic-new-closure-private-scope': b"<?php\nclass A {\n    private function __construct() { echo 'A|'; }\n    public static function maker() { return function($class) { return new $class; }; }\n}\nclass B {}\n$make = A::maker();\n$allowed = $make('A');\necho $allowed::class, '|';\n$foreign = Closure::bind($make, null, 'B');\ntry { $foreign('A'); } catch (Error $e) { echo 'E|', $e->getMessage(), '|'; }\ntry { $make->call(new B, 'A'); } catch (Error $e) { echo 'E|', $e->getMessage(); }\nunset($make, $foreign, $allowed);\n",
    'dynamic-new-ternary-keywords-runtime': b"<?php\nclass A {\n    public static function run() {\n        try { new ('se'.(true ? 'lf' : 'x')); }\n        catch (Error $e) { echo $e->getMessage(), '|'; }\n        try { new ('pa'.(true ? 'rent' : 'x')); }\n        catch (Error $e) { echo $e->getMessage(), '|'; }\n        try { new ('sta'.(true ? 'tic' : 'x')); }\n        catch (Error $e) { echo $e->getMessage(), '|'; }\n    }\n}\nA::run();\n",
    'dynamic-new-binary-folded-keywords': b'<?php\nclass ParentClass {}\nclass A extends ParentClass {\n    public static function run() {\n        $a = new (\'se\'.(\'lf\' ^ "\\0\\0"));\n        $p = new (\'pa\'.(\'rent\' ^ "\\0\\0\\0\\0"));\n        $b = new (\'sta\'.(\'tic\' ^ "\\0\\0\\0"));\n        echo $a::class, \'/\', $p::class, \'/\', $b::class;\n    }\n}\nclass B extends A {}\nB::run();\n',
    'dynamic-new-core-noninstantiable': b"<?php\nfunction value() { echo 'V|'; return 1; }\n$class = function() {};\ntry { new $class(value()); } catch (Error $e) { echo 'E|', $e->getMessage(), '|'; }\nforeach (['Closure', 'Throwable', 'Stringable', 'Iterator', 'ArrayAccess'] as $class) {\n    try { new $class(value()); } catch (Error $e) { echo 'E|', $e->getMessage(), '|'; }\n}\n",
    'dynamic-new-multiline-abstract-allocation-line': b"<?php\nabstract class AbstractClass {}\nfunction selector($value) { echo 'S|'; return $value; }\nfunction argument() { echo 'V|'; return 1; }\ntry {\n    $new = new\n        (selector(\n            'AbstractClass'\n        ))\n        (argument());\n} catch (Error $e) { echo 'E@', $e->getLine(), '/', $e->getMessage(); }\n",
    'dynamic-new-multiline-private-access-line': b"<?php\nclass PrivateClass { private function __construct($value) {} }\nfunction selector($value) { echo 'S|'; return $value; }\nfunction argument() { echo 'V|'; return 1; }\ntry {\n    $new = new\n        (selector(\n            'PrivateClass'\n        ))\n        (argument());\n} catch (Error $e) { echo 'E@', $e->getLine(), '/', $e->getMessage(); }\n",
    'dynamic-new-multiline-constructor-call-line': b"<?php\nclass Accepts { public function __construct(int $value) {} }\nfunction selector($value) { echo 'S|'; return $value; }\nfunction argument() { echo 'V|'; return []; }\ntry {\n    $new = new\n        (selector(\n            'Accepts'\n        ))\n        (argument());\n} catch (TypeError $e) {\n    $frame = $e->getTrace()[0];\n    echo 'E@', $e->getLine(), '/', $frame['line'], '/', $frame['function'], '/', $frame['class'];\n}\n",
    'dynamic-new-recursive-inherited-constructor': b"<?php\nclass Base {\n    public function __construct($depth) {\n        echo 'E', $this::class, '@', $depth, '|';\n        if ($depth < 2) {\n            $class = $depth === 0 ? 'B' : 'A';\n            $child = new $class($depth + 1);\n            echo 'R', $this::class, '/', $child::class, '|';\n        }\n    }\n}\nclass A extends Base {}\nclass B extends Base {}\n$class = 'A';\n$top = new $class(0);\necho 'F', $top::class;\n",
    'dynamic-new-selector-retirement-source': b"<?php\nclass Selected {\n    public function __construct($check = false) { if ($check) { echo 'C|'; } }\n}\n$old = new Selected;\nfunction choose() { global $old; $selected = $old; $old = null; echo 'S|'; return $selected; }\nfunction argument() { echo 'V|'; return true; }\n$new = new (choose())(argument());\necho $new::class;\n",
    'dynamic-new-binary-keyword-inherited-constructor': b'<?php\nclass ParentClass {\n    public function __construct() { echo \'P\', $this::class, \'|\'; }\n}\nclass A extends ParentClass {\n    public static function run() {\n        $a = new (\'se\'.(\'lf\' ^ "\\0\\0"));\n        $p = new (\'pa\'.(\'rent\' ^ "\\0\\0\\0\\0"));\n        $b = new (\'sta\'.(\'tic\' ^ "\\0\\0\\0"));\n        echo $a::class, \'/\', $p::class, \'/\', $b::class;\n    }\n}\nclass B extends A {}\nB::run();\n',
    'dynamic-new-stdclass-parent-core': b'<?php\nclass A extends stdClass {\n    public static function run() {\n        $dynamic = new (\'pa\'.(\'rent\' ^ "\\0\\0\\0\\0"));\n\n        echo $dynamic::class;\n    }\n}\nclass B extends A {}\nB::run();\n',
    'dynamic-new-rebound-keyword-cold-retirement': b'<?php\nclass ParentClass {\n    const X = E_STRICT;\n    public function __construct() { echo \'C\', $this::class, \'/\', self::X, \'|\'; }\n}\nclass A {\n    public static function make() {\n        return static function () { return new (\'se\'.(\'lf\' ^ "\\0\\0")); };\n    }\n}\nclass B extends ParentClass {}\n$maker = A::make();\n$bound = $maker->bindTo(null, B::class);\nunset($maker);\nset_error_handler(function () { global $bound; $bound = null; echo \'H|\'; return true; });\n$made = $bound();\necho \'F\', $made::class;\n',
    'dynamic-new-literal-self-rejection': b"<?php\necho 'unreachable|';\nnew ('self');\n",
    'dynamic-new-computed-int-rejection': b"<?php\necho 'unreachable|';\nnew (1+2);\n",
    'dynamic-new-runtime-keywords-versus-folded': b"<?php\nclass ParentClass {}\nclass A extends ParentClass {\n    public static function run() {\n        foreach (['self', 'parent', 'static'] as $class) {\n            try { new $class; } catch (Error $e) { echo $e->getMessage(), '|'; }\n        }\n        $a = new ('se'.'lf');\n        $p = new ('pa'.'rent');\n        $b = new ('sta'.'tic');\n        echo $a::class, '/', $p::class, '/', $b::class;\n    }\n}\nclass B extends A {}\nB::run();\n",
    'dynamic-new-cached-method-composition': b'<?php\ntrait Maker {\n    private static function build() {\n        $a = new (\'se\'.(\'lf\' ^ "\\0\\0"))(true);\n        $b = new (\'sta\'.(\'tic\' ^ "\\0\\0\\0"))(true);\n        echo \'S\', $a::class, \'/\', $b::class, \'|\';\n        return $b;\n    }\n    public Closure $f = self::build(...);\n    public function __construct($mark = false) {\n        if ($mark) { echo \'C\', $this::class, \'|\'; }\n    }\n}\nclass HostA { use Maker; }\n$a = new HostA;\n$first = $a->f;\n$madeA = $first();\necho \'FA\', $madeA::class, \'|\';\nif (true) { class HostB { use Maker; } }\n$b = new HostB;\n$later = clone ($b->f);\nunset($a, $b, $first);\n$made = $later();\nunset($later);\necho \'F\', $made::class;\n',
}
EXPECTED = {
    'dynamic-new-string-namespace-alias': b'C1|Demo\\C|E|Class "Alias" not found|C2|',
    'dynamic-new-object-reference': b'C1|C2|Child/new',
    'dynamic-new-reference-selection': b'V|B7|B/A',
    'dynamic-new-effectful-selector': b'P|V|C4|Chosen/1',
    'dynamic-new-invalid-selector-before-arguments': b'Error/Class name must be a valid object or a string|Error/Class name must be a valid object or a string|Error/Class name must be a valid object or a string|Error/Class name must be a valid object or a string|Error/Class name must be a valid object or a string|Error/Class name must be a valid object or a string|Error/Class "Absent" not found',
    'dynamic-new-no-constructor-named': b'V1|V2|Plain|V3|E|Unknown named parameter $first',
    'dynamic-new-inherited-throwable': b'T|E/message/3/7/seed',
    'dynamic-new-undefined-handler-redefinition': b'H2@10|Error/Class name must be a valid object or a string/Ready',
    'dynamic-new-undefined-handler-throw': b'H|Exception/stop/none/Ready',
    'dynamic-new-cold-class-before-arguments': b'D4|V|C1/2048/7|F',
    'dynamic-new-cold-class-aborts-before-arguments': b'E|Undefined constant "MISSING"',
    'dynamic-new-access-and-named-priority': b'E|Call to private PrivateClass::__construct() from global scope|V3|E|Unknown named parameter $missing',
    'dynamic-new-noninstantiable-before-arguments': b'E|Cannot instantiate abstract class AbstractClass|E|Cannot instantiate interface Contract|',
    'dynamic-new-runtime-keywords-reduced': b'Class "self" not found|Class "parent" not found|Class "static" not found|',
    'dynamic-new-parser-and-folded-classnames': b'Demo\\C|E|Class "Alias" not found|Demo\\C',
    'dynamic-new-recursive-cold-selection': b'O|H|CB|TB|CA|FA',
    'dynamic-new-closure-private-scope': b'A|A|E|Call to private A::__construct() from scope B|E|Call to private A::__construct() from scope B',
    'dynamic-new-ternary-keywords-runtime': b'Class "self" not found|Class "parent" not found|Class "static" not found|',
    'dynamic-new-binary-folded-keywords': b'A/ParentClass/B',
    'dynamic-new-core-noninstantiable': b'E|Instantiation of class Closure is not allowed|E|Instantiation of class Closure is not allowed|E|Cannot instantiate interface Throwable|E|Cannot instantiate interface Stringable|E|Cannot instantiate interface Iterator|E|Cannot instantiate interface ArrayAccess|',
    'dynamic-new-multiline-abstract-allocation-line': b'S|E@8/Cannot instantiate abstract class AbstractClass',
    'dynamic-new-multiline-private-access-line': b'S|E@8/Call to private PrivateClass::__construct() from global scope',
    'dynamic-new-multiline-constructor-call-line': b'S|V|E@2/7/__construct/Accepts',
    'dynamic-new-recursive-inherited-constructor': b'EA@0|EB@1|EA@2|RB/A|RA/B|FA',
    'dynamic-new-selector-retirement-source': b'S|V|C|Selected',
    'dynamic-new-binary-keyword-inherited-constructor': b'PA|PParentClass|PB|A/ParentClass/B',
    'dynamic-new-stdclass-parent-core': b'stdClass',
    'dynamic-new-rebound-keyword-cold-retirement': b'H|CB/2048|FB',
    'dynamic-new-literal-self-rejection': b'',
    'dynamic-new-computed-int-rejection': b'',
    'dynamic-new-runtime-keywords-versus-folded': b'',
    'dynamic-new-cached-method-composition': b'CHostA|CHostA|SHostA/HostA|FAHostA|CHostA|CHostB|SHostA/HostB|FHostB',
}
COMPILED = {'dynamic-new-literal-self-rejection': (b"'\\self' is an invalid class name", 3), 'dynamic-new-computed-int-rejection': (b'Illegal class name', 3), 'dynamic-new-runtime-keywords-versus-folded': (b"'\\self' is an invalid class name", 8)}


def compile_source(info, directory, path):
    message, line = info
    observed = cross.invoke.process([str(ROOT / '.tools/php/bin/php'), '-n', *cross.invoke.types.FLAGS,
        str(path)], directory / 'native', 30, directory)
    assert observed.returncode == 255 and observed.stdout == b''
    assert observed.stderr == b'Fatal error: ' + message + b' in ' + os.fsencode(path) + b' on line ' + str(line).encode() + b'\nStack trace:\n#0 {main}\n'
    facts = {'version': 2, 'main': cross.invoke.b64(os.fsencode(path)),
             'cwd': cross.invoke.b64(os.fsencode(directory)), 'include_path': cross.invoke.b64(b'.:'),
             'entries': [], 'chdir_entries': []}
    facts_path = directory / 'snapshot.json'
    facts_path.write_text(json.dumps(facts, sort_keys=True) + '\n')
    result = cross.invoke.process([str(ROOT / 'bin/php-semantics'), str(path), '--file-snapshot',
        str(facts_path), '--steps', '100000', '--timeout', '60'], directory / 'model', 90, directory)
    assert result.returncode == 0 and not result.stderr
    outcome = json.loads(result.stdout)
    assert outcome['frontend'] == 'accepted' and outcome['checked'] == 'program'
    assert outcome['status'] == 'static_rejection' and outcome['exit_status'] == 255
    assert outcome['reason'] is None
    assert outcome['diagnostic']['class'] == 'CompileError' and outcome['diagnostic']['line'] == line
    assert base64.b64decode(outcome['diagnostic']['message'], validate=True) == message
    assert base64.b64decode(outcome['stdout'], validate=True) == observed.stdout
    assert base64.b64decode(outcome['stderr'], validate=True) == observed.stderr
    return {'status': 'static_rejection', 'exit_status': 255}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--select', help='Comma-separated exact case IDs')
    parser.add_argument('--freeze', type=Path)
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else list(CASES)
    assert selected and len(selected) == len(set(selected)) and all(name in CASES for name in selected)
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(args.freeze)
    out = Path(tempfile.mkdtemp(prefix='dynamic-new-sources-', dir=ROOT / '.tools'))
    report = {'passed': False, 'completed': False, 'before': before,
              'profile': cross.invoke.types.PROFILE, 'selected': selected, 'records': []}
    print(out, flush=True)
    try:
        for name in selected:
            directory = out / name; directory.mkdir()
            source = directory / 'source.php'; source.write_bytes(CASES[name])
            row = {'case': name, 'source_sha256': cross.invoke.sha(source), 'completed': False}
            report['records'].append(row)
            row['outcome'] = compile_source(COMPILED[name], directory, source) if name in COMPILED else cross.source(
                {'abrupt': False, 'expected_exit_status': 0, 'expected_stdout': EXPECTED[name].decode()}, directory, source)
            assert cross.snapshot(args.freeze) == before
            row['completed'] = True
            print(name, row['outcome']['status'], flush=True)
        report.update(passed=True, completed=True)
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after'] = cross.snapshot(args.freeze)
        report['passed'] = report['passed'] and report['before'] == report['after']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)
    assert report['passed'] and report['completed']


if __name__ == '__main__':
    main()

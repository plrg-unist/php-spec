#!/usr/bin/env python3
"""Ordinary named keyword NEW scope, priority and constructors."""
import argparse
import base64
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross

ROOT = Path(__file__).resolve().parents[2]
CASES = {
    'dynamic-new-stdclass-parent': b'<?php\nclass A extends stdClass {\n    public static function run() {\n        $dynamic = new (\'pa\'.(\'rent\' ^ "\\0\\0\\0\\0"));\n        $named = new parent;\n        echo $dynamic::class, \'/\', $named::class;\n    }\n}\nclass B extends A {}\nB::run();\n',
    'named-keyword-inherited-constructor': b"<?php\nclass P { public function __construct($value) { echo 'C', $this::class, $value, '|'; } }\nclass A extends P {\n    public static function run() {\n        $self = new self(1);\n        $parent = new parent(2);\n        $static = new static(3);\n        echo $self::class, '/', $parent::class, '/', $static::class;\n    }\n}\nclass B extends A {}\nB::run();\n",
    'named-keyword-main-no-scope': b"<?php\nfunction argument() { echo 'V|'; return 1; }\ntry { new SeLf(argument()); } catch (Error $e) { echo $e->getMessage(), '|'; }\ntry { new parent(argument()); } catch (Error $e) { echo $e->getMessage(), '|'; }\ntry { new static(argument()); } catch (Error $e) { echo $e->getMessage(), '|'; }\n",
    'named-keyword-rebound-trio': b"<?php\nclass P { public function __construct($mark = false) { if ($mark) echo 'C', $this::class, '|'; } }\nclass Q { public function __construct($mark = false) { if ($mark) echo 'C', $this::class, '|'; } }\nclass A extends P {\n    public static function maker() {\n        return static function () {\n            $self = new self(true); $parent = new parent(true); $static = new static(true);\n            echo $self::class, '/', $parent::class, '/', $static::class;\n            return $static;\n        };\n    }\n}\nclass B extends Q {}\n$maker = A::maker(); $bound = $maker->bindTo(null, B::class); unset($maker);\n$made = $bound(); unset($bound);\necho '|F', $made::class;\n",
    'named-keyword-temporary-call': b"<?php\nclass P { public function __construct($mark = false) { if ($mark) echo 'C', $this::class, '|'; } }\nclass B extends P {}\n$maker = function () {\n    $self = new self(true); $parent = new parent(true); $static = new static(true);\n    echo $self::class, '/', $parent::class, '/', $static::class;\n    return $static;\n};\n$receiver = new B;\n$made = $maker->call($receiver);\necho '|F', $made::class;\n",
    'named-keyword-unrelated-called': b"<?php\nclass A {\n    private function __construct() { echo 'A|'; }\n    public static function maker() { return function () {\n        $self = new self; $static = new static(true);\n        echo $self::class, '/', $static::class;\n    }; }\n}\nclass B { public function __construct($mark = false) { if ($mark) echo 'B|'; } }\n$maker = A::maker(); $receiver = new B;\n$bound = $maker->bindTo($receiver, A::class); unset($maker, $receiver);\n$bound();\n",
    'named-keyword-internal-parent': b"<?php\nclass Message { public function __toString() { echo 'T|'; return 'm'; } }\nclass E extends Exception { public static function make() { return new parent(new Message, 7); } }\n$made = E::make();\necho $made::class, '/', $made->getMessage(), '/', $made->getCode();\n",
    'named-keyword-noctor-named-priority': b"<?php\nfunction argument($value) { echo 'V', $value, '|'; return $value; }\nclass Plain {}\nclass A extends Plain { public static function run() {\n    try { new parent(first: argument(1), later: argument(2)); }\n    catch (Error $e) { echo 'E|', $e->getMessage(); }\n} }\nA::run();\n",
    'named-keyword-private-access': b"<?php\nfunction argument() { echo 'V|'; return 1; }\nclass P { private function __construct($value) {} }\nclass A extends P { public static function run() {\n    try { new parent(argument()); }\n    catch (Error $e) { echo 'E|', $e->getMessage(); }\n} }\nA::run();\n",
    'named-keyword-multiline-access': b"<?php\nfunction argument() { echo 'V|'; return 1; }\nclass P { private function __construct($value) {} }\nclass A extends P {\n    public static function run() {\n        try {\n            $made = new\n                parent\n                (argument());\n        } catch (Error $e) { echo 'E@', $e->getLine(), '/', $e->getMessage(); }\n    }\n}\nA::run();\n",
    'named-keyword-multiline-type-trace': b"<?php\nclass Base { public function __construct(int $value) {} }\nclass A extends Base {\n    public static function run() {\n        try {\n            $made = new\n                self\n                (argument());\n        } catch (TypeError $e) {\n            $frame = $e->getTrace()[0];\n            echo 'E@', $e->getLine(), '/', $frame['line'], '/', $frame['function'], '/', $frame['class'];\n        }\n    }\n}\nfunction argument() { echo 'V|'; return []; }\nA::run();\n",
    'named-keyword-trait-trio': b"<?php\nclass P { public function __construct() { echo 'C', $this::class, '|'; } }\ntrait Maker { public static function run() {\n    $self = new self; $static = new static; $parent = new parent;\n    echo $self::class, '/', $static::class, '/', $parent::class;\n} }\nclass A extends P { use Maker; }\nclass B extends A {}\nB::run();\n",
    'named-keyword-trait-no-parent': b"<?php\nfunction argument() { echo 'V|'; return 1; }\ntrait Maker { public static function run() {\n    try { new parent(argument()); }\n    catch (Error $e) { echo $e->getMessage(); }\n} }\nclass A { use Maker; }\nA::run();\n",
    'named-keyword-arrow-rebound': b"<?php\nclass A { public static function maker() { return static fn() => new self; } }\nclass B { public function __construct() { echo 'B|'; } }\n$maker = A::maker(); $bound = $maker->bindTo(null, B::class); unset($maker);\n$made = $bound(); echo $made::class;\n",
    'named-keyword-cold-maker-retirement': b"<?php\nclass P {\n    public const X = E_STRICT;\n    public function __construct($value) { echo 'C', $this::class, $value, '/', self::X, '|'; }\n}\nclass A { public static function maker() { return static function () { return new self(argument()); }; } }\nclass B extends P {}\nfunction argument() { echo 'V|'; return 1; }\n$maker = A::maker(); $bound = $maker->bindTo(null, B::class); unset($maker);\nset_error_handler(function ($errno, $message) { global $bound; $bound = null; echo 'H|'; return true; });\n$made = $bound(); echo 'F', $made::class;\n",
    'named-keyword-eval-inherited-scope': b"<?php\nclass P { public function __construct() { echo 'C', $this::class, '|'; } }\nclass A extends P { public static function run() {\n    $made = eval('return [new self, new parent, new static];');\n    echo $made[0]::class, '/', $made[1]::class, '/', $made[2]::class;\n} }\nclass B extends A {}\nB::run();\n",
    'named-keyword-eval-no-parent': b"<?php\nfunction argument() { echo 'V|'; return 1; }\nclass A { public static function run() {\n    try { eval('return new parent(argument());'); }\n    catch (Error $e) { echo $e->getMessage(); }\n} }\nA::run();\n",
    'named-keyword-recursive-factory': b"<?php\nclass Base {\n    public function __construct($depth) {\n        echo 'C', $this::class, '|';\n        if ($depth === 0) {\n            $child = B::make(1);\n            echo 'R', $child::class, '|';\n        }\n    }\n    public static function make($depth) {\n        $made = new static($depth);\n        echo 'F', $made::class, '|';\n        return $made;\n    }\n}\nclass A extends Base {}\nclass B extends Base {}\nA::make(0);\n",
    'named-keyword-free-self-rejection': b"<?php\necho 'unreachable|';\nfunction factory() { return new self(argument()); }\nfunction argument() { echo 'V|'; return 1; }\n",
    'named-keyword-free-parent-rejection': b"<?php\necho 'unreachable|';\nfunction factory() { return new parent(argument()); }\nfunction argument() { echo 'V|'; return 1; }\n",
    'named-keyword-free-static-rejection': b"<?php\necho 'unreachable|';\nfunction factory() { return new static(argument()); }\nfunction argument() { echo 'V|'; return 1; }\n",
    'named-keyword-known-parent-rejection': b"<?php\necho 'unreachable|';\nclass A {\n    public static function run() {\n        return new parent(argument());\n    }\n}\nfunction argument() { echo 'V|'; return 1; }\n",
    'named-keyword-null-bound-current-composition': b"<?php\nclass A {\n    private function __construct($mark) { echo 'CA', $mark, '|'; }\n    public static function maker() { return function () {\n        $self = new self(1);\n        $static = new static(2);\n        echo $self::class, '/', $static::class, '|';\n        return Closure::getCurrent();\n    }; }\n}\nclass B { public function __construct() {} }\n$maker = A::maker(); $receiver = new B;\n$bound = $maker->bindTo($receiver, A::class);\n$null = $bound->bindTo(null);\nunset($maker, $receiver, $bound);\n$returned = $null();\necho $returned === $null ? 'same' : 'foreign';\nunset($returned, $null);\n",
    'named-keyword-constant-method-cold-retirement': b'<?php\ntrait ConstantNewFactory {\n    private static function maker() {\n        $lexical = new (\'se\'.(\'lf\' ^ "\\0\\0"))(1);\n        $late = new static(2);\n        echo \'S\', $lexical::class, \'/\', $late::class, \'|\';\n        return $late;\n    }\n    public const array F = [self::maker(...), ConstantNewLate::X];\n}\nclass ConstantNewA {\n    use ConstantNewFactory;\n    private function __construct($mark) { echo \'A\', $mark, \'|\'; }\n}\ntry {\n    $first = ConstantNewA::F;\n} catch (Error $e) {\n    echo \'F|\';\n}\nif (true) {\n    class ConstantNewLate { public const X = 7; }\n    class ConstantNewB {\n        use ConstantNewFactory;\n        public function __construct($mark) { echo \'B\', $mark, \'|\'; }\n    }\n}\n$values = ConstantNewB::F;\n$maker = $values[0];\n$makerClone = clone $maker;\nunset($values, $maker);\n$made = $makerClone();\nunset($makerClone);\necho \'R\', $made::class, \'|\';\nunset($made);\n$retry = ConstantNewA::F;\n$retryMaker = $retry[0];\nunset($retry);\n$again = $retryMaker();\nunset($retryMaker);\necho \'R\', $again::class;\n',
}
EXPECTED = {
    'dynamic-new-stdclass-parent': b'stdClass/stdClass',
    'named-keyword-inherited-constructor': b'CA1|CP2|CB3|A/P/B',
    'named-keyword-main-no-scope': b'Cannot access "self" when no class scope is active|Cannot access "parent" when no class scope is active|Cannot access "static" when no class scope is active|',
    'named-keyword-rebound-trio': b'CB|CQ|CB|B/Q/B|FB',
    'named-keyword-temporary-call': b'CB|CP|CB|B/P/B|FB',
    'named-keyword-unrelated-called': b'A|B|A/B',
    'named-keyword-internal-parent': b'T|Exception/m/7',
    'named-keyword-noctor-named-priority': b'V1|E|Unknown named parameter $first',
    'named-keyword-private-access': b'E|Call to private P::__construct() from scope A',
    'named-keyword-multiline-access': b'E@8/Call to private P::__construct() from scope A',
    'named-keyword-multiline-type-trace': b'V|E@2/7/__construct/Base',
    'named-keyword-trait-trio': b'CA|CB|CP|A/B/P',
    'named-keyword-trait-no-parent': b'Cannot access "parent" when current class scope has no parent',
    'named-keyword-arrow-rebound': b'B|B',
    'named-keyword-cold-maker-retirement': b'H|V|CB1/2048|FB',
    'named-keyword-eval-inherited-scope': b'CA|CP|CB|A/P/B',
    'named-keyword-eval-no-parent': b'Cannot access "parent" when current class scope has no parent',
    'named-keyword-recursive-factory': b'CA|CB|FB|RB|FA|',
    'named-keyword-null-bound-current-composition': b'CA1|CA2|A/A|same',
    'named-keyword-constant-method-cold-retirement': b'F|A1|B2|SConstantNewA/ConstantNewB|RConstantNewB|A1|A2|SConstantNewA/ConstantNewA|RConstantNewA',
}
COMPILED = {
    'named-keyword-free-self-rejection': (b'Cannot use "self" when no class scope is active', 3),
    'named-keyword-free-parent-rejection': (b'Cannot use "parent" when no class scope is active', 3),
    'named-keyword-free-static-rejection': (b'Cannot use "static" when no class scope is active', 3),
    'named-keyword-known-parent-rejection': (b'Cannot use "parent" when current class scope has no parent', 5),
}

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
    out = Path(tempfile.mkdtemp(prefix='named-keyword-new-sources-', dir=ROOT / '.tools'))
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

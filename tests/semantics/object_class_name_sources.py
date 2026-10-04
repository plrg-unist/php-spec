#!/usr/bin/env python3
"""Dynamic object class names, parser literals, compiler rejection and read callbacks."""
import argparse
import base64
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross

ROOT = Path(__file__).resolve().parents[2]
CASES = {
    'dynamic-class-cv-reference': b"<?php\nclass BaseClass {}\nclass CaseChild extends BaseClass {}\n$obj = new casechild;\n$ref =& $obj;\necho $obj::class, '/', $ref::class;\n$obj = new BaseClass;\necho '/', $ref::class;\n",
    'dynamic-class-container-reference': b"<?php\nclass BaseClass {}\nclass ChildClass extends BaseClass {}\nclass Holder { public $value; }\n$holder = new Holder;\n$items = [new ChildClass];\n$holder->value =& $items[0];\necho ($holder->value)::class, '/', $items[0]::class;\n$items[0] = new BaseClass;\necho '/', ($holder->value)::class;\n",
    'dynamic-class-no-string-conversion': b'<?php\nclass Message {\n    public function __toString(): string { echo "T|"; throw new Exception(\'bad\'); }\n}\necho (new Message)::class;\n$message = new Message;\necho \'|\', $message::class;\n',
    'dynamic-class-child-once': b"<?php\nclass ChildClass {}\n$times = 0;\nfunction make() { global $times; echo 'M', ++$times, '|'; return new ChildClass; }\necho (make())::class, '/', $times;\n",
    'dynamic-class-assignment-child': b"<?php\nclass FirstClass {}\nclass SecondClass {}\n$value = new FirstClass;\necho ($value = new SecondClass)::class, '/', $value::class;\n",
    'dynamic-class-scalar-errors': b"<?php\nclass Existing {}\nforeach ([null, false, true, 0, 1.0, 'Existing', []] as $value) {\n    try { echo $value::class; }\n    catch (TypeError $error) { echo $error->getMessage(), '|'; }\n}\n",
    'dynamic-class-undefined-handler-line': b"<?php\nset_error_handler(function($number, $message, $file, $line) { echo 'H', $number, '@', $line, '|'; return true; });\ntry {\n    echo $missing::class;\n} catch (TypeError $error) { echo $error->getMessage(); }\n",
    'dynamic-class-handler-redefines-cv': b"<?php\nclass Ready {}\nfunction handler() { global $missing; $missing = new Ready; echo 'H|'; return true; }\nset_error_handler('handler');\ntry { echo $missing::class; }\ncatch (TypeError $error) { echo $error->getMessage(); }\necho '/', $missing::class;\n",
    'dynamic-class-returned-string': b"<?php\nclass Existing {}\nfunction make() { echo 'R|'; return 'Existing'; }\ntry { echo (make())::class; }\ncatch (TypeError $error) { echo $error->getMessage(); }\n",
    'dynamic-class-literal-name': b"<?php\nnamespace Probe;\nuse Missing\\Elsewhere as Alias;\necho Alias::class, '|', ('Ghost')::class;\n",
    'dynamic-class-pruned-constant': b"<?php\nconst SAFE = false ? ($missing)::class : 'safe';\nconst COMPUTED_SAFE = false ? ('Gh'.'ost')::class : 'computed';\nconst COALESCE_SAFE = 'selected' ?? ($missing)::class;\necho SAFE, '|', COMPUTED_SAFE, '|', COALESCE_SAFE;\n",
    'anonymous-default-unrelated-called-scope': b'<?php\nclass A{\n    private function __construct(){echo "A|";}\n    static function make(){return function($a=new self){echo get_called_class(),"/",$a::class;};}\n}\nclass B{}\n$f=A::make();\n$g=$f->bindTo(new B,A::class);\nunset($f);\n$g();\n',
    'anonymous-default-target-class-name-argument': b'<?php\nclass A{function __construct($name){echo "A(",$name,")|";}static function make(){return function($a=new self(self::class)){echo get_called_class(),"/",$a::class,";";};}}\nclass B{function __construct($name){echo "B(",$name,")|";}}\n$f=A::make();$g=$f->bindTo(null,B::class);\n$f();$g();$f();\n',
    'anonymous-default-bound-arrow': b"<?php\nclass A {\n    public static function make() {\n        return fn($a = new self) => $a::class;\n    }\n}\nclass B {}\n$f = A::make();\n$g = $f->bindTo(null, B::class);\nunset($f);\necho $g(), '|';\n$r = $g->bindTo(null, A::class);\nunset($g);\necho $r();\n",
    'anonymous-default-trait-maker-rebound': b"<?php\ntrait Maker {\n    public static function make() {\n        return function($a = new self, $b = new parent) {\n            echo $a::class, '/', $b::class, ';';\n        };\n    }\n}\nclass ParentOne {}\nclass A extends ParentOne { use Maker; }\nclass ParentTwo {}\nclass B extends ParentTwo {}\n$f = A::make();\n$g = $f->bindTo(null, B::class);\nunset($f);\n$g();\n$r = $g->bindTo(null, A::class);\nunset($g);\n$r();\n",
    'dynamic-class-undefined-handler-throw-previous': b"<?php\nclass Ready {}\nset_error_handler(function() { echo 'H|'; throw new Exception('stop'); });\ntry { echo $missing::class; }\ncatch (TypeError $error) { echo 'E/', $error->getMessage(), '/', $error->getPrevious()->getMessage(), '|'; }\n$missing = new Ready;\necho $missing::class;\n",
    'dynamic-class-dimension-handler-throw': b"<?php\n$values = [];\nset_error_handler(function() { echo 'H|'; throw new Exception('stop'); });\ntry { echo $values['missing']::class; }\ncatch (Exception $error) { echo 'E/', $error->getMessage(); }\n",
    'dynamic-class-parser-concat-keywords': b"<?php\nclass A { static function run() { echo ('se'.'lf')::class, '/', ('Gh'.'ost')::class; } }\nA::run();\nconst NAME = ('Gh'.'ost')::class;\necho '/', NAME;\n",
    'dynamic-class-supported-internal-objects': b"<?php\n$plain = new stdClass;\n$closure = fn() => 0;\n$error = new Exception('message');\necho $plain::class, '/', $closure::class, '/', $error::class;\n",
    'dynamic-class-compiled-lines': b"<?php\nfunction make($argument) { echo 'R|'; return 'Existing'; }\nset_error_handler(function($number, $message, $file, $line) { echo 'H@', $line, '|'; return true; });\ntry {\n    echo (\n        $missing\n    )::class;\n} catch (TypeError $error) { echo 'E@', $error->getLine(), '|'; }\ntry {\n    echo (make(\n        1\n    ))::class;\n} catch (TypeError $error) { echo 'E@', $error->getLine(); }\n",
    'computed-class-true': b'<?php\necho "unreachable|";\necho (1 < 2)::class;\n',
    'computed-class-false': b'<?php\necho "unreachable|";\necho (1 > 2)::class;\n',
    'computed-class-array': b'<?php\necho "unreachable|";\necho ([1 + 2])::class;\n',
    'computed-class-int': b'<?php\necho "unreachable|";\necho (1 + 2)::class;\n',
    'literal-class-int': b'<?php\necho "unreachable|";\necho (1)::class;\n',
    'constant-class-dynamic': b'<?php\necho "unreachable|";\nconst INVALID = ($missing)::class;\n',
    'computed-class-nonparser-string': b"<?php\necho 'unreachable|';\necho ('Gh'.true)::class;\n",
    'dynamic-class-interpolation-owner-composition': b'<?php\nclass First {\n    public function __toString() {\n        global $left, $right;\n        $left = null;\n        $right = new Later;\n        echo $this::class, \'|\';\n        return \'first\';\n    }\n}\nclass Later {\n    public function __toString() { echo $this::class, \'|\'; return \'last\'; }\n}\n$left = new First;\n$right = \'old\';\necho "pre:{$left}/{$right}", \'|\', $right::class;\nunset($left, $right);\n',
}
EXPECTED = {
    'dynamic-class-cv-reference': b'CaseChild/CaseChild/BaseClass',
    'dynamic-class-container-reference': b'ChildClass/ChildClass/BaseClass',
    'dynamic-class-no-string-conversion': b'Message|Message',
    'dynamic-class-child-once': b'M1|ChildClass/1',
    'dynamic-class-assignment-child': b'SecondClass/SecondClass',
    'dynamic-class-scalar-errors': b'Cannot use "::class" on null|Cannot use "::class" on false|Cannot use "::class" on true|Cannot use "::class" on int|Cannot use "::class" on float|Cannot use "::class" on string|Cannot use "::class" on array|',
    'dynamic-class-undefined-handler-line': b'H2@4|Cannot use "::class" on null',
    'dynamic-class-handler-redefines-cv': b'H|Cannot use "::class" on null/Ready',
    'dynamic-class-returned-string': b'R|Cannot use "::class" on string',
    'dynamic-class-literal-name': b'Missing\\Elsewhere|Ghost',
    'dynamic-class-pruned-constant': b'safe|computed|selected',
    'anonymous-default-unrelated-called-scope': b'A|B/A',
    'anonymous-default-target-class-name-argument': b'A(A)|A/A;B(B)|B/B;A(A)|A/A;',
    'anonymous-default-bound-arrow': b'B|A',
    'anonymous-default-trait-maker-rebound': b'B/ParentTwo;A/ParentOne;',
    'dynamic-class-undefined-handler-throw-previous': b'H|E/Cannot use "::class" on null/stop|Ready',
    'dynamic-class-dimension-handler-throw': b'H|E/stop',
    'dynamic-class-parser-concat-keywords': b'A/Ghost/Ghost',
    'dynamic-class-supported-internal-objects': b'stdClass/Closure/Exception',
    'dynamic-class-compiled-lines': b'H@6|E@6|R|E@11',
    'dynamic-class-interpolation-owner-composition': b'First|Later|pre:first/last|Later',
}
COMPILED = {
    'computed-class-true': b'Cannot use "::class" on true',
    'computed-class-false': b'Cannot use "::class" on false',
    'computed-class-array': b'Cannot use "::class" on array',
    'computed-class-int': b'Cannot use "::class" on int',
    'literal-class-int': b'Illegal class name',
    'constant-class-dynamic': b'(expression)::class cannot be used in constant expressions',
    'computed-class-nonparser-string': b'Cannot use "::class" on string',
}


def compile_source(message, directory, path):
    observed = cross.invoke.process([str(ROOT / '.tools/php/bin/php'), '-n', *cross.invoke.types.FLAGS,
        str(path)], directory / 'native', 30, directory)
    assert observed.returncode == 255 and observed.stdout == b''
    assert observed.stderr == b'Fatal error: ' + message + b' in ' + os.fsencode(path) + b' on line 3\nStack trace:\n#0 {main}\n'
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
    assert outcome['diagnostic']['class'] == 'CompileError' and outcome['diagnostic']['line'] == 3
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
    out = Path(tempfile.mkdtemp(prefix='object-class-names-', dir=ROOT / '.tools'))
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

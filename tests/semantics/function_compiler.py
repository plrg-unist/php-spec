#!/usr/bin/env python3
"""Named function body compiler checks with pinned native lint observations."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import static_types as types
import source_compiler as compiler
import source_context as context

ROOT = Path(__file__).resolve().parents[2]
CASES = {
    'import-around-function': b'<?php use A; function f(){} use B;',
    'ordinary': b'<?php echo f(3); function f($n) { $x=$n+1; return $x; }',
    'recursive': b'<?php function f($n) { if ($n) return $n*f($n-1); return 1; } echo f(4);',
    'nested': b'<?php function f($a) { function g($b) {$z=1;return $b;} $x=2;return g($a); } echo f(3);',
    'cv': b'<?php $before=1; function f($arg) { $local=1; $_GET; ${"_SERVER"|""}; $name="_GET"; $$name; return $arg; } $after=2;',
    'magic': b'<?php namespace N; function f(){echo __FUNCTION__,__METHOD__,__NAMESPACE__,__CLASS__;} f();',
    'header': b'<?php $http_response_header=1;function f(){echo $http_response_header;} echo $http_response_header;',
    'header-reverse': b'<?php function f(){$http_response_header=1;} echo $http_response_header;',
    'dead-break': b'<?php while(false){ function f(){break;} }',
    'dead-body': b'<?php if(false){ function f(){[,$x];} }',
    'return': b'<?php $a=[1,2];foreach($a as &$x){foreach($a as &$y){echo $x,$y;return 7;}} echo "bad";',
    'global': b'<?php $a=2;function f(){global $a;$a++;return $a;}echo f(),$a;',
    'duplicate': b'<?php function f(){} function F(){}',
    'dup-badbody': b'<?php function f(){} function F(){break;}',
    'conditional': b'<?php if(true){function f(){return 3;}}echo f();',
    'block': b'<?php echo f();{function f(){return 3;}}',
    'import': b'<?php namespace N;use function A as f;function f(){}',
    'import-after': b'<?php namespace N;function f(){} use function A as f;',
    'signature': b'<?php function f($a,$a){}',
    'bare-return': b'<?php function f(){return;} f();',
    'function-globals': b'<?php function f(){global $GLOBALS;}',
    'import-assert': b'<?php use function A as assert;function assert(){}',
    'import-autoload': b'<?php use function A as __autoload;function __autoload(){}',
    'assert': b'<?php function assert(){}',
    'autoload': b'<?php function __autoload(){}',
    'namespace-case': b'<?php namespace N;function F(){}use function A as f;',
    'header-param': b'<?php function f($http_response_header){echo $http_response_header;}',
    'global-header': b'<?php function f(){global $http_response_header;echo $http_response_header;}',
    'global-this': b'<?php function f(){global $this;}',
    'global-name-effects': b'<?php function f(){global ${($x="a")};return $x;}',
    'multiline-body-hole': b'<?php\nfunction f($x)\n{\n [ ,$x];\n}',
    'multiline-return': b'<?php\nfunction f() {\n return\n [ ,$x];\n}',
    'nested-seen': b'<?php namespace N;function f(){function g(){}}use function A as g;',
    'builtin-redeclare': b'<?php function strlen(){}',
    'call-priority-hole': b'<?php f([,1], x:2);',
    'call-priority-globals': b'<?php f($GLOBALS=1, x:2);',
    'builtin-body-priority': b'<?php function strlen(){break;}',
    'builtin-case': b'<?php function STRLEN(){}',
    'builtin-namespace': b'<?php namespace N;function strlen(){}',
}
PENDING = {
    'void-return': b'<?php function f():void{return 1;}',
    'never-return': b'<?php function f():never{return;}',
    'default-invalid': b'<?php function f($a=[[]=>1]){}',
    'byref-return': b'<?php function &f(){return 1;}',
    'param-default': b'<?php function f($a=1){}',
    'param-type': b'<?php function f(int $a){}',
    'variadic': b'<?php function f(...$a){}',
}

CONTEXTS = {'ordinary': ['P.CVS = eps', 'P.FUNCTIONS = [pfunction]', 'pfunction.CVS = [([110]),([120])]', 'pfunction.EARLY', 'pfunction.ORIGIN = PORIGIN 91 ([PCINDEX 1])', 'pfunction.BODY = [PCINDEX 1, PCFIELD 5]', 'pfunction.CODE.UNIT = 91', 'P.FOLD.FUNCTION = eps'], 'nested': ['P.CVS = eps', 'P.FUNCTIONS = [pfunction_g,pfunction_f]', 'pfunction_f.CVS = [([97]),([120])]', 'pfunction_g.CVS = [([98]),([122])]', 'pfunction_f.EARLY', '~pfunction_g.EARLY', 'pfunction_f.CODE.EXPRESSIONS = $ppownexpr([pfunction_g], pfunction_f.CODE.EXPRESSIONS)', 'pfunction_g.CODE.EXPRESSIONS =/= eps', 'P.FOLD.FUNCTION = eps'], 'cv': ['P.CVS = [([98,101,102,111,114,101]),([97,102,116,101,114])]', 'P.FUNCTIONS = [pfunction]', 'pfunction.CVS = [([97,114,103]),([108,111,99,97,108]),([110,97,109,101])]', 'P.AUTOGLOBALS = [([95,71,69,84]),([95,83,69,82,86,69,82])]', '|pfunction.CODE.GLOBALS| = 2', 'pfunction.CODE.GLOBALS = P.GLOBALS'], 'magic': ['P.FUNCTIONS = [pfunction]', 'pfunction.NAME = [78,92,102]', 'pfunction.ENV.NAMESPACE = [78]', 'P.FOLD.FUNCTION = eps'], 'block': ['P.FUNCTIONS = [pfunction]', 'pfunction.EARLY'], 'conditional': ['P.FUNCTIONS = [pfunction]', '~pfunction.EARLY'], 'global': ['P.CVS = [([97])]', 'P.FUNCTIONS = [pfunction]', 'pfunction.CVS = [([97])]'], 'function-globals': ['P.FUNCTIONS = [pfunction]', 'pfunction.CVS = eps', 'P.AUTOGLOBALS = [([71,76,79,66,65,76,83])]']}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    specs = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    adapter_path = ROOT / '_build/default/adapter/main.exe'
    files = [*specs, runner, adapter_path, types.PHP, Path(__file__),
             ROOT / 'frontend/worker.php', ROOT / '.tools/php-file.so',
             ROOT / 'vendor/php-src/Zend/zend_compile.c']
    before = {str(path.relative_to(ROOT)): digest(path) for path in files}
    out = Path(tempfile.mkdtemp(prefix='function-compiler-', dir=ROOT / '.tools'))
    frontend = types.Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
                            'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')])
    adapter = types.Worker([str(adapter_path), str(ROOT)])
    records, assertions = [], []
    try:
        for index, (name, source) in enumerate([*CASES.items(), *PENDING.items()]):
            file = out / (name + '.php')
            file.write_bytes(source)
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
            assert parsed['accepted'], parsed
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            command = [str(types.PHP), '-n', *types.FLAGS, '-l', str(file)]
            (out / (name + '.command.json')).write_text(json.dumps(command) + '\n')
            try:
                native = subprocess.run(command, capture_output=True, timeout=30, env=types.ENV)
            except subprocess.TimeoutExpired as error:
                (out / (name + '.stdout')).write_bytes(error.stdout or b'')
                (out / (name + '.stderr')).write_bytes(error.stderr or b'')
                (out / (name + '.failure')).write_text('native timeout\n')
                raise
            (out / (name + '.stdout')).write_bytes(native.stdout)
            (out / (name + '.stderr')).write_bytes(native.stderr)
            events = context.events(native)
            record = {'name': name, 'source': base64.b64encode(source).decode(),
                      'checked': checked, 'lint_exit': native.returncode, 'events': events,
                      'status': 'pending signature activation' if name in PENDING else 'compiler comparison'}
            records.append(record)
            (out / 'records.json').write_text(json.dumps(records, indent=2) + '\n')
            assertion = (f'dec $case{index}() : bool\ndef $case{index}() = true\n'
                         f'  -- if P = $ppstart(91, {checked["fixture"]}, {types.byte_expr(str(file))})\n')
            if name in PENDING:
                reason = ("nonliteral parameter default requires constant-expression compilation" if name == "default-invalid" else "function type, default, reference or variadic activation")
                assertion += '  -- if P.COMPLETION = PPCABRUPT (UNSUPPORTED ' + json.dumps(reason) + ')\n'
            else:
                assertion += '  -- if $pptrace(P) = ' + context.expected_events(events, file) + '\n'
                if native.returncode == 0:
                    assertion += '  -- if P.COMPLETION = PPCNORMAL\n'
                    assertion += '  -- if $ppconstants(P) = PPCCONSTANTS (pcpath, pvalue)*\n'
                    assertion += ''.join('  -- if ' + condition + '\n' for condition in CONTEXTS.get(name, []))
            assertions.append(assertion)
            state = f'dec $main() : ppstate\ndef $main() = $ppstart(91, {checked["fixture"]}, {types.byte_expr(str(file))})\n'
            (out / (name + '.state.watsup')).write_text(state)
        fixture = out / 'compiler.watsup'
        fixture.write_text(compiler.PREFIX + '\n'.join(assertions) +
                           '\ndec $main() : bool\ndef $main() = true\n' +
                           ''.join(f'  -- if $case{index}()\n' for index in range(len(assertions))))
        command = [str(runner), *map(str, specs), str(fixture)]
        (out / 'spectec-command.json').write_text(json.dumps(command) + '\n')
        try:
            result = subprocess.run(command, capture_output=True, timeout=120)
        except subprocess.TimeoutExpired as error:
            (out / 'spectec.stdout').write_bytes(error.stdout or b'')
            (out / 'spectec.stderr').write_bytes(error.stderr or b'')
            (out / 'failure.txt').write_text('SpecTec timeout\n')
            raise
        (out / 'spectec.stdout').write_bytes(result.stdout)
        (out / 'spectec.stderr').write_bytes(result.stderr)
        (out / 'spectec-status.json').write_text(json.dumps({'exit': result.returncode}) + '\n')
        assert result.returncode == 0 and result.stdout.strip() == b'true' and not result.stderr, result
    finally:
        frontend.close()
        adapter.close()
    assert before == {str(path.relative_to(ROOT)): digest(path) for path in files}
    report = {'scope': 'named function compilation; runtime invocation evidence is separate',
              'result': 'pass', 'compiler_comparisons': len(CASES),
              'explicit_pending_signatures': len(PENDING),
              'context_programs': len(CONTEXTS),
              'context_assertions': sum(map(len, CONTEXTS.values())), 'inputs': before,
              'raw': str(out.relative_to(ROOT)), 'fixture_sha256': digest(fixture),
              'cases': records}
    (ROOT / 'coverage/semantics/function-compiler.json').write_text(json.dumps(report, indent=2) + '\n')
    print(str(len(CASES)) + ' compiler comparisons; ' + str(len(PENDING)) + ' explicit pending signature controls')


if __name__ == '__main__':
    main()

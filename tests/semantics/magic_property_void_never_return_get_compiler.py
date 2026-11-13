#!/usr/bin/env python3
"""Check illegal void/never Get returns at the original statement line."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

import static_types as types
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CASES = (
    ('void-value', 'void', 'return null;',
     'A void method must not return a value (did you mean "return;" instead of "return null;"?)'),
    ('void-nonnull', 'void', 'return 1;', 'A void method must not return a value'),
    ('never-bare', 'never', 'return;', 'A never-returning method must not return'),
)


def main():
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    adapter = ROOT / '_build/default/adapter/main.exe'
    watched = [*modules, runner, adapter, types.PHP, Path(__file__),
               ROOT / 'spec/semantics/modules.json', ROOT / 'tests/semantics/profile.json',
               ROOT / 'frontend/worker.php', ROOT / '.tools/php-file.so',
               ROOT / 'tests/semantics/recorded_worker.py', ROOT / 'tests/semantics/static_types.py']
    fingerprint = lambda: {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
    before = fingerprint()
    output = Path(tempfile.mkdtemp(prefix='void-never-get-compiler-', dir=ROOT / '.tools'))
    print(output, flush=True)
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], output / 'frontend')
    checker = Worker([str(adapter), str(ROOT)], output / 'adapter')
    records, clauses = [], []
    try:
        for index, (name, kind, statement, message) in enumerate(CASES):
            source = '<?php\nclass InvalidReturnGet {\n    public function __get($incoming): ' + kind + ' {\n        ' + statement + '\n    }\n}\n'
            path = output / (name + '.php')
            path.write_text(source)
            command = [str(types.PHP), '-n', *types.FLAGS, '-l', str(path)]
            native = subprocess.run(command, capture_output=True, env=types.ENV, timeout=30)
            (output / (name + '.stdout')).write_bytes(native.stdout)
            (output / (name + '.stderr')).write_bytes(native.stderr)
            records.append({'id': name, 'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
                            'native_command': command, 'native_exit': native.returncode,
                            'message': message, 'line': 4, 'native_executions': 1})
            (output / 'native.json').write_text(json.dumps(records, indent=2) + '\n')
            assert native.returncode == 255 and message.encode() in native.stderr and b'on line 4' in native.stderr
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.encode()).decode()})
            assert parsed['accepted'], parsed
            checked = checker.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], checked
            clauses.append('dec $case' + str(index) + '() : bool\ndef $case' + str(index) + '() = true\n'
                           '  -- if P = $ppstart(91,' + checked['fixture'] + ',' + types.byte_expr(str(path)) + ')\n'
                           '  -- if P.COMPLETION = PPCABRUPT (STATICBYTES $ptascii(' + json.dumps(message) + ') 4)\n'
                           '  -- if P.DIAGNOSTICS = eps\n')
        fixture = output / 'compiler.watsup'
        fixture.write_text('\n'.join(clauses) + '\ndec $main() : bool\ndef $main() = true\n'
                           + ''.join('  -- if $case' + str(i) + '()\n' for i in range(len(CASES))))
        command = [str(runner), '--sl', *map(str, modules), str(fixture)]
        result = subprocess.run(command, capture_output=True, env=types.ENV, timeout=280)
        (output / 'compiler.stdout').write_bytes(result.stdout)
        (output / 'compiler.stderr').write_bytes(result.stderr)
    finally:
        frontend.close()
        checker.close()
    after = fingerprint()
    passed = before == after and result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
    report = {'result': 'pass' if passed else 'fail', 'mode': 'production SL_mode', 'modules': len(modules),
              'source_credit': 0, 'compiler_controls': records, 'assertions': 3 * len(CASES),
              'command': command, 'exit_status': result.returncode,
              'inputs_before': before, 'inputs_after': after, 'stable': before == after}
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(output / 'report.json', report['result'], flush=True)
    assert passed


if __name__ == '__main__':
    main()

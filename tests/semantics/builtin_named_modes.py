"""Check configured fixed-name lookup independently of generated rule grouping."""
from pathlib import Path
import hashlib
import json
import subprocess
import tempfile
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
MODULES = ['spec/php.watsup', 'spec/semantics/00-numeric.watsup',
           'spec/semantics/10-bytes.watsup', 'spec/semantics/16-static-types.watsup',
           'spec/semantics/25-builtin-argument-modes.watsup',
           'spec/semantics/106-builtin-named-compiler.watsup']


def main():
    report_path = ROOT / 'coverage/semantics/builtin-argument-modes.json'
    records = json.loads(report_path.read_text())['arguments']
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    files = [*[ROOT / p for p in MODULES], report_path, runner, Path(__file__),
             ROOT / 'scripts/generate-builtin-argument-modes.py']
    before = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    out = Path(tempfile.mkdtemp(prefix='builtin-named-modes-', dir=ROOT / '.tools'))
    print(out, flush=True)
    rows, checks = [], []
    for record in records:
        fixed = [p['name'] for p in record['parameters'] if not p['variadic']]
        names = fixed + ['__absent_parameter__']
        names += [p['name'] for p in record['parameters'] if p['variadic']]
        for parameter in names:
            for function, spelling in [(record['name'], parameter),
                                       (record['name'].upper(), parameter),
                                       (record['name'], parameter.swapcase())]:
                expected = fixed.index(spelling) if spelling in fixed else None
                rows.append({'function': function, 'parameter': spelling, 'index': expected})
                checks.append('($pfunction_builtin_fixed_index(' + types.byte_expr(function) + ', ' + types.byte_expr(spelling) + ') = ' + ('eps' if expected is None else '(' + str(expected) + ')') + ')')
    for function, parameter in [('__unknown_builtin__', 'array'), ('sort', ''),
                                ('sort', '\x00array'), ('sort', 'array\x00'),
                                ('sort', '\u00ff'), ('sort', 'array_'), ('\\sort', 'array')]:
        checks.append('($pfunction_builtin_fixed_index(' + types.byte_expr(function) + ', ' + types.byte_expr(parameter) + ') = eps)')
        rows.append({'function': function, 'parameter': parameter, 'index': None})
    fixture = out / 'names.watsup'
    fixture.write_text('dec $main() : bool\ndef $main() = ' + ' /\\\n '.join(checks) + '\n')
    (out / 'expected.json').write_text(json.dumps(rows, indent=2) + '\n')
    command = [str(runner), *[str(ROOT / p) for p in MODULES], str(fixture)]
    (out / 'command.json').write_text(json.dumps(command) + '\n')
    try:
        result = subprocess.run(command, capture_output=True, env=types.ENV, timeout=120)
    except subprocess.TimeoutExpired as error:
        (out / 'stdout').write_bytes(error.stdout or b'')
        (out / 'stderr').write_bytes(error.stderr or b'')
        (out / 'status.json').write_text(json.dumps({'status': 'timeout'}))
        raise
    (out / 'stdout').write_bytes(result.stdout)
    (out / 'stderr').write_bytes(result.stderr)
    (out / 'status.json').write_text(json.dumps({'status': 'exit', 'exit_status': result.returncode}))
    assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr, result
    assert before == {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    report = {'scope': 'Configured fixed-name indices and case/unknown/variadic exclusions; no builtin execution.',
              'result': 'pass', 'functions': len(records), 'assertions': len(checks), 'inputs': before,
              'raw': str(out.relative_to(ROOT)), 'fixture_sha256': hashlib.sha256(fixture.read_bytes()).hexdigest()}
    (ROOT / 'coverage/semantics/builtin-named-modes-test.json').write_text(json.dumps(report, indent=2) + '\n')
    print(len(records), len(checks), flush=True)


if __name__ == '__main__':
    main()

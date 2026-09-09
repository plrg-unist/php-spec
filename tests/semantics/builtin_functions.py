#!/usr/bin/env python3
"""Check source-derived builtin occupancy against pinned native registration.

PHP only enumerates its existing registration metadata. SpecTec alone computes
membership, case folding and negative lookup answers.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / 'tests/semantics'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bytes_term(text):
    return '([' + ','.join(str(x) for x in text.encode()) + '])'


def main():
    php = ROOT / '.tools/php/bin/php'
    runner = HERE / '_build/default/numeric_runner.exe'
    specs = [ROOT / p for p in ['spec/php.watsup', 'spec/semantics/10-bytes.watsup',
                              'spec/semantics/16-static-types.watsup',
                              'spec/semantics/24-builtin-functions.watsup']]
    source_report = ROOT / 'coverage/semantics/builtin-function-sources.json'
    source = json.loads(source_report.read_text())
    expected = [name for table in source['tables'] for name in table['names']]
    watched = [Path(__file__), php, runner, source_report, *specs]
    before = {str(path.relative_to(ROOT)): digest(path) for path in watched}
    out = Path(tempfile.mkdtemp(prefix='builtin-functions-', dir=ROOT / '.tools'))
    code = ('echo json_encode([PHP_VERSION,PHP_SAPI,PHP_INT_SIZE,PHP_ZTS,'
            'ini_get("disable_functions"),get_loaded_extensions(),'
            'get_defined_functions()["internal"]]);')
    command = [str(php), '-n', '-r', code]
    (out / 'native-command.json').write_text(json.dumps(command) + '\n')
    try:
        native = subprocess.run(command, capture_output=True, timeout=30)
    except subprocess.TimeoutExpired as error:
        (out / 'native.stdout').write_bytes(error.stdout or b'')
        (out / 'native.stderr').write_bytes(error.stderr or b'')
        (out / 'native-status.json').write_text(json.dumps({'status': 'timeout'}) + '\n')
        raise
    (out / 'native.stdout').write_bytes(native.stdout)
    (out / 'native.stderr').write_bytes(native.stderr)
    (out / 'native-status.json').write_text(json.dumps({'status': 'completed', 'exit': native.returncode}) + '\n')
    assert native.returncode == 0 and native.stderr == b'', native
    identity = json.loads(native.stdout)
    assert identity[:5] == ['8.5.10', 'cli', 8, False, ''], identity[:5]
    assert sorted(identity[6]) == sorted(expected), {
        'source_only': sorted(set(expected) - set(identity[6])),
        'native_only': sorted(set(identity[6]) - set(expected))}
    positive = expected + [name.upper() for name in expected]
    negative = ['', 'missing_function', 'N\\strlen', 'N\\exit', 'strlen\0',
                'STRLEN\0', '\\strlen', 'php_spec_parse_file', 'mb_ereg']
    assert not (set(negative) & set(expected))
    body = '''dec $all_builtins(ptbytes*) : bool
def $all_builtins(eps) = true
def $all_builtins(ptbytes :: ptbytes_tail*) = $pfunction_builtin(ptbytes) /\\ $all_builtins(ptbytes_tail*)
dec $no_builtins(ptbytes*) : bool
def $no_builtins(eps) = true
def $no_builtins(ptbytes :: ptbytes_tail*) = ~$pfunction_builtin(ptbytes) /\\ $no_builtins(ptbytes_tail*)
dec $main() : bool
def $main() = true
'''
    body += '  -- if $all_builtins([' + ','.join(map(bytes_term, positive)) + '])\n'
    body += '  -- if $no_builtins([' + ','.join(map(bytes_term, negative)) + '])\n'
    fixture = out / 'membership.watsup'
    fixture.write_text(body)
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
    (out / 'spectec-status.json').write_text(json.dumps({'status': 'completed', 'exit': result.returncode}) + '\n')
    assert result.returncode == 0 and result.stdout.strip() == b'true' and not result.stderr, result
    assert before == {str(path.relative_to(ROOT)): digest(path) for path in watched}
    report = {'scope': 'initial configured function namespace occupancy only',
              'result': 'pass', 'registered_names': len(expected),
              'membership_assertions': len(positive) + len(negative),
              'identity': identity[:6], 'inputs': before,
              'raw': str(out.relative_to(ROOT)), 'fixture_sha256': digest(fixture)}
    (ROOT / 'coverage/semantics/builtin-functions.json').write_text(json.dumps(report, indent=2) + '\n')
    print(str(len(expected)) + ' exact registered names; ' + str(report['membership_assertions']) + ' pure membership assertions')


if __name__ == '__main__':
    main()

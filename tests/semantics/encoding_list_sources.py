#!/usr/bin/env python3
"""Original-source encoding directive lists, bodies and ordered diagnostics."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import recorded

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('encoding_lists')
ORACLE = 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
HASHES = {
    'order.php': '66c11809eec4f53cc0b99caadc5bc0daed67333ddc83b734bded1322ac329d2c',
    'ticks.php': '7407fdbb918412e5586a85b7f4579f7a3b55a44cdeee06da210a197847a2468e',
    'nonliteral.php': '67fa248bb61da45b7229478e9a13b745f28b683ed80c1efae0f5d20a5866ef45',
    'body.php': '7ec0f2a2181a699b66a5a44ca25668fe7efad00b34fc321eadc0fc032b602822',
    'child.php': 'fb6c061e61a65eac1a262a7065a4f5fd9b013e311b9614574f0adc4421ad425a',
    'eval.php': '3894b543bb947b6d18bbe248a8d4809a9f64dcdd86c2d52e450ecb1d190b3572',
    'include-main.php': 'a6f842d93c9cb77d8227f3af22b8a980b9cdd8f22e832ef4b02ac4ddb9c8bdcb',
    'late-prefix.php': '396217fd2ea012eb98f1c68d7f19d96de16e1b479a2e0b3563f3c6cffc975808',
    'lists.php': 'c0468a872fd830c6b98670cd8d255237667f3fc553c912d07172956af4f36105',
    'multiline-body.php': '5740f34a463588a355ffa08ade49c169262a4a387844fdbf5f7e0d9a5b2f98df',
    'multiline-header.php': 'cf3effae4e60d07441932630805e264e1ded4853277d5d8b4764339831895a60',
    'nested.php': '45d2851dba45f7ea0c52fae40e54052f24921cc9c67cd08cc1b9f4d7a1b351f6',
    'strict.php': 'da119b9d35402c2874395d38540ad4d1c0420071ca834d04b69e2720fcbb3985',
}
CASES = ['lists', 'body', 'nested', 'late-prefix', 'strict', 'nonliteral', 'ticks', 'order', 'include-main', 'eval',
         'multiline-header', 'multiline-body']
CONTROLS = {'multiline-header', 'multiline-body'}
MESSAGE = b'declare(encoding=...) ignored because Zend multibyte feature is turned off by settings'
FATAL = b'Encoding declaration pragma must be the very first statement in the script'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
b64 = lambda data: base64.b64encode(data).decode()


def expected(name):
    path = bytes(SOURCE / (name + '.php'))
    def warning(message, line, filename=path):
        return b'Warning: ' + message + b' in ' + filename + b' on line ' + str(line).encode() + b'\n'
    def encoding(line, filename=path):
        return warning(MESSAGE, line, filename)
    def fatal(message, line):
        return b'Fatal error: ' + message + b' in ' + path + b' on line ' + str(line).encode() + b'\nStack trace:\n#0 {main}\n'
    if name == 'lists':
        return 0, b'L|T|', encoding(2) * 2 + encoding(3) + warning(b"Unsupported declare 'Foo'", 2) + warning(b"Unsupported declare 'Bar'", 2), 'normal'
    if name == 'body':
        return 0, b'B|S|C|Z|', encoding(2) + encoding(3) * 2 + encoding(4), 'normal'
    if name == 'nested':
        return 255, b'', encoding(2) * 2 + warning(b"Unsupported declare 'Foo'", 2) + fatal(FATAL, 2), 'static_rejection'
    if name == 'late-prefix':
        return 255, b'', encoding(4) * 2 + warning(b"Unsupported declare 'Foo'", 2) + fatal(FATAL, 4), 'static_rejection'
    if name == 'strict':
        return 255, b'', encoding(2) + fatal(b'strict_types declaration must not use block mode', 2), 'static_rejection'
    if name == 'nonliteral':
        return 255, b'', encoding(2) + fatal(b'declare(Foo) value must be a literal', 2), 'static_rejection'
    if name == 'ticks':
        return 0, b'T|A|T|Z|', encoding(2), 'normal'
    if name == 'order':
        return 255, b'', encoding(3) + encoding(5) + fatal(FATAL, 5), 'static_rejection'
    if name == 'include-main':
        child = bytes(SOURCE / 'child.php')
        return 0, b'M|C|7|A|', encoding(2, child) * 2 + warning(b"Unsupported declare 'Foo'", 2, child), 'normal'
    if name == 'eval':
        child = path + b"(3) : eval()'d code"
        return 0, b'M|E|8|A|', encoding(1, child) * 2 + warning(b"Unsupported declare 'Foo'", 1, child), 'normal'
    if name == 'multiline-header':
        return 0, b'H|', encoding(3), 'unsupported'
    assert name == 'multiline-body'
    return 0, b'B|', encoding(2), 'unsupported'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--select', help='comma-separated case names')
    args = parser.parse_args()
    names = args.select.split(',') if args.select else CASES
    assert names and len(set(names)) == len(names) and set(names) <= set(CASES)
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    assert {name: sha(SOURCE / name) for name in HASHES} == HASHES
    assert sha(ROOT / '.tools/php/bin/php') == ORACLE
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text()); profile['include_path'] = '.:'
    flags = [x for key, value in profile.items() for x in ('-d', key + '=' + value)]
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    watched = [Path(__file__), ROOT / 'spec/semantics/92-strict-compiler.watsup',
               ROOT / 'spec/semantics/93-strict-declarations.watsup', ROOT / 'spec/semantics/modules.json',
               ROOT / 'spec/semantics/194-compiler-preflight.watsup',
               ROOT / 'bin/php-semantics', ROOT / 'frontend/worker.php', ROOT / '.tools/php-file.so',
               ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php/bin/php',
               ROOT / 'tests/semantics/profile.json', ROOT / 'tests/semantics/error_handler_run.py',
               *(SOURCE / name for name in HASHES)]
    inputs = {str(path.relative_to(ROOT)): sha(path) for path in watched}
    report = {'head': head, 'inputs': inputs, 'profile': profile, 'oracle_sha256': ORACLE,
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}, 'selected': names,
              'records': [], 'agreements': 0, 'controls': 0, 'passed': False}
    try:
        for name in names:
            path = SOURCE / (name + '.php'); case = out / name; case.mkdir()
            exit_status, stdout, stderr, status = expected(name)
            row = {'id': name, 'source_sha256': sha(path), 'control': name in CONTROLS}; report['records'].append(row)
            native = recorded([str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(path)], case / 'native', 15)
            row['native'] = native
            assert native['exit'] == exit_status and not native['timeout'] and not native['group_after']
            assert (case / 'native.stdout').read_bytes() == stdout and (case / 'native.stderr').read_bytes() == stderr
            (case / 'startup.json').write_text(json.dumps({'error_reporting': b64(b'30719'), 'include_path': b64(b'.:')}) + '\n')
            extra = []
            if name == 'include-main':
                child = SOURCE / 'child.php'
                snapshot = {'version': 2, 'main': b64(bytes(path)), 'cwd': b64(bytes(ROOT)),
                    'include_path': b64(b'.:'), 'chdir_entries': [], 'entries': [
                    {'caller': b64(bytes(path)), 'requested': b64(bytes(child)),
                     'cwd': b64(bytes(ROOT)), 'include_path': b64(b'.:'), 'status': 'opened',
                     'resolved': b64(bytes(child)), 'opened': b64(bytes(child)), 'source': b64(child.read_bytes())}]}
                (case / 'snapshot.json').write_text(json.dumps(snapshot) + '\n')
                extra = ['--file-snapshot', str(case / 'snapshot.json')]
            model = recorded([str(ROOT / 'bin/php-semantics'), str(path), '--startup-ini',
                              str(case / 'startup.json'), *extra, '--steps', '100000', '--timeout', '120'],
                             case / 'model', 140)
            row['model'] = model
            outcome = json.loads((case / 'model.stdout').read_bytes())
            row['status'] = outcome.get('status'); row['reason'] = outcome.get('reason')
            valid = (model['exit'] == 0 and not model['timeout'] and not model['group_after']
                and (case / 'model.stderr').read_bytes() == b'' and outcome['frontend'] == 'accepted'
                and outcome['checked'] == 'program' and outcome['status'] == status)
            if name in CONTROLS:
                row['passed'] = valid and outcome['reason'] == 'encoding parser warning source shape'
                report['controls'] += int(row['passed'])
            else:
                row['passed'] = (valid and outcome['reason'] is None and outcome['exit_status'] == exit_status
                    and outcome['stdout'] == b64(stdout) and outcome['stderr'] == b64(stderr))
                report['agreements'] += int(row['passed'])
            print(name, 'pass' if row['passed'] else 'fail', flush=True)
        report['passed'] = all(row['passed'] for row in report['records'])
    finally:
        report['inputs_stable'] = inputs == {str(path.relative_to(ROOT)): sha(path) for path in watched}
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['passed'] = report['passed'] and report['inputs_stable'] and report['head_stable']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']


if __name__ == '__main__':
    main()

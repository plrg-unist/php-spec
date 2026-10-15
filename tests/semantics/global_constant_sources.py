#!/usr/bin/env python3
"""Native-first global constant() values and API failures from original bytes."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

import error_handler_run as recorder

ROOT = Path(__file__).resolve().parents[2]
recorder.ROOT = ROOT
b64 = lambda data: base64.b64encode(data).decode()
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
ORACLE_SHA256 = 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'

CASES = {
    'names-and-scalars': br'''<?php
namespace GlobalQuery21;
const LocalOnly = 17;
const Mixed = 23;
const mixed = 29;
const UserFloat = 1.5;
const UserFalse = false;
const UserNull = null;
\define('OutsideGlobal21', 31);
echo 'B|', \constant('OutsideGlobal21'), '|', \constant('gLoBaLqUeRy21\\Mixed'), '|', \constant('\\GlobalQuery21\\mixed');
echo '|', \constant('GlobalQuery21\\UserFloat') === 1.5 ? 'D' : 'BAD', \constant('GlobalQuery21\\UserFalse') === false ? 'F' : 'BAD', \constant('GlobalQuery21\\UserNull') === null ? 'N' : 'BAD';
echo '|', \constant('TrUe') === true ? 'T' : 'BAD', \constant('FaLsE') === false ? 'F' : 'BAD', \constant('NuLl') === null ? 'N' : 'BAD';
try { \constant('LocalOnly'); echo '|BAD'; } catch (\Error $e) { echo '|', $e->getMessage(); }
try { \constant('globalquery21\\MIXED'); echo '|BAD'; } catch (\Error $e) { echo '|', $e->getMessage(); }
''',
    'captured-query-and-strings': br'''<?php
const GlobalLiteral21 = 'literal';
$prefix = 'request';
define('GlobalRequest21', $prefix . '-value');
$call = 'constant';
function changeGlobalCallee21() { global $call; $call = 'defined'; return 'GlobalRequest21'; }
echo 'B|', $call(name: changeGlobalCallee21()), '|', $call, '|', constant('GlobalLiteral21');
''',
    'captured-define-query-and-strings': br'''<?php
define('GlobalLiteral21', 'literal');
$prefix = 'request';
define('GlobalRequest21', $prefix . '-value');
$call = 'constant';
function changeGlobalCallee21() { global $call; $call = 'defined'; return 'GlobalRequest21'; }
echo 'B|', $call(name: changeGlobalCallee21()), '|', $call, '|', constant('GlobalLiteral21');
''',
    'missing-api-error': br'''<?php
function missingGlobal21() {
    $result = 91;
    try {
        $result = constant(name: '\\MissingGlobal21');
        echo 'BAD';
    } catch (Error $e) {
        $trace = $e->getTrace();
        echo $result === 91 ? 'kept|' : 'BAD|';
        echo $e->getMessage(), '|', $e->getLine(), '|', $trace[0]['function'], '|', $trace[0]['args'][0];
    } finally { echo '|F'; }
}
echo 'B|'; missingGlobal21();
''',
    'array-result-boundary': br'''<?php
const GlobalArray21 = [1];
echo 'B|'; constant('GlobalArray21'); echo 'after';
''',
}
UNSUPPORTED = {'array-result-boundary': ('global constant value query', b'B|')}
BASELINE = ('class constant value query', b'B|')


def fingerprint():
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())
    names = [*modules, 'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json',
        'bin/php-semantics', '_build/default/adapter/main.exe', '.tools/php/bin/php',
        '.tools/php-file.so', 'frontend/worker.php', 'frontend/target.php',
        'frontend/FileLexer.php', 'frontend/EvalLexer.php', 'frontend/wire.php',
        'frontend/wire.py', 'tests/semantics/profile.json', 'tests/semantics/error_handler_run.py',
        str(Path(__file__).relative_to(ROOT))]
    return {name: sha(ROOT / name) for name in names}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['preflight', 'native', 'baseline', 'model'], required=True)
    parser.add_argument('--case', action='append', default=[])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = args.case or list(CASES)
    assert len(selected) == len(set(selected)) and set(selected) <= CASES.keys()
    assert args.phase != 'baseline' or len(selected) == 1
    assert sha(ROOT / '.tools/php/bin/php') == ORACLE_SHA256
    if args.phase == 'preflight':
        print(json.dumps({'script_sha256': sha(__file__), 'oracle_sha256': ORACLE_SHA256,
            'sources': {name: hashlib.sha256(CASES[name]).hexdigest() for name in selected}}, indent=2))
        return
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=True)
    suffix = '-' + '-'.join(args.case) if args.phase == 'model' and args.case else ''
    report_path = out / (args.phase + suffix + '-report.json')
    assert not report_path.exists()
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    flags = [piece for key, value in profile.items() for piece in ('-d', key + '=' + value)]
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    semantic_diff = subprocess.check_output(['git', 'diff', 'HEAD', '--', 'spec/semantics'], cwd=ROOT)
    if args.phase in ('native', 'baseline'):
        assert semantic_diff == b''
        assert subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT) == b''
    report = {'phase': args.phase, 'revision': revision, 'inputs': fingerprint(),
        'semantic_diff_sha256': hashlib.sha256(semantic_diff).hexdigest(),
        'target': 'PHP 8.5.10 CLI NTS 64-bit',
        'engine_revision': '34308a6666b2d489c509541ea9befea9e2b42348',
        'profile': profile, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'},
        'records': [], 'source_agreements': 0, 'passed': False}
    print(out, flush=True)
    try:
        for name in selected:
            directory = out / name; directory.mkdir(exist_ok=True)
            source = directory / 'main.php'
            if args.phase == 'native':
                assert not source.exists(); source.write_bytes(CASES[name])
            assert source.read_bytes() == CASES[name]
            row = {'id': name, 'source_sha256': sha(source), 'passed': False}
            report['records'].append(row)
            if args.phase == 'native':
                command = [str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(source)]
                row['process'] = recorder.recorded(command, directory / 'native', 15)
                row['stdout'] = b64((directory / 'native.stdout').read_bytes())
                row['stderr'] = b64((directory / 'native.stderr').read_bytes())
                assert not row['process']['timeout'] and not row['process']['group_after']
                row['passed'] = True
            else:
                native = json.loads((out / 'native-report.json').read_bytes())
                assert native['passed'] and native['inputs_stable']
                original, = [r for r in native['records'] if r['id'] == name]
                assert original['source_sha256'] == row['source_sha256']
                command = [str(ROOT / 'bin/php-semantics'), str(source), '--steps', '10000', '--timeout', '45']
                row['process'] = recorder.recorded(command, directory / args.phase, 60)
                outcome = json.loads((directory / (args.phase + '.stdout')).read_bytes()); row['outcome'] = outcome
                assert not row['process']['timeout'] and not row['process']['group_after']
                assert (directory / (args.phase + '.stderr')).read_bytes() == b''
                assert outcome['frontend'] == 'accepted' and outcome['checked'] == 'program'
                if args.phase == 'baseline':
                    assert row['process']['exit'] == 1 and outcome['status'] == 'unsupported'
                    reason, prefix = BASELINE
                    assert outcome['reason'] == reason and outcome['stdout'] == b64(prefix)
                elif name in UNSUPPORTED:
                    assert row['process']['exit'] == 1 and outcome['status'] == 'unsupported'
                    reason, prefix = UNSUPPORTED[name]
                    assert outcome['reason'] == reason and outcome['stdout'] == b64(prefix)
                else:
                    assert row['process']['exit'] == 0 and outcome['status'] == 'normal' and outcome['reason'] is None
                    assert outcome['exit_status'] == original['process']['exit']
                    assert outcome['stdout'] == original['stdout'] and outcome['stderr'] == original['stderr']
                    report['source_agreements'] += 1
                row['passed'] = True
            print(name, row['passed'], flush=True)
        report['passed'] = True
    finally:
        report['inputs_stable'] = report['inputs'] == fingerprint()
        report['head_stable'] = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['passed'] = report['passed'] and report['inputs_stable'] and report['head_stable']
        report_path.write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']


if __name__ == '__main__':
    main()

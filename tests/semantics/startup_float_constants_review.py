#!/usr/bin/env python3
"""Independent model-only constant resolution and runtime API controls."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import ENV, recorded

ROOT = Path(__file__).resolve().parents[2]
CASES = {
    'qualified-errors': (b'''<?php
namespace Startup\\Independent {
    use const Missing\\PHP_FLOAT_MIN as MissingLimit;
    try { echo MissingLimit; } catch (\\Error $error) { echo 'A'; }
    try { echo namespace\\PHP_FLOAT_MAX; } catch (\\Error $error) { echo 'R'; }
    try { echo \\php_float_EPSILON; } catch (\\Error $error) { echo 'C'; }
}
''', b'ARC'),
    'float-shadow': (b'''<?php
namespace Startup\\IndependentShadow {
    use const PHP_FLOAT_MAX as Largest;
    const PHP_FLOAT_EPSILON = 3;
    echo PHP_FLOAT_EPSILON === 3, ':',
        \\PHP_FLOAT_EPSILON === 2.220446049250313e-16, ':',
        PHP_FLOAT_DIG === \\PHP_FLOAT_DIG, ':', Largest === \\PHP_FLOAT_MAX;
}
''', b'1:1:1:1'),
    'runtime-queries': (b'''<?php
echo defined('PHP_FLOAT_DIG'), defined('PHP_FLOAT_EPSILON'),
    defined('PHP_FLOAT_MAX'), defined('PHP_FLOAT_MIN'), ':',
    defined('php_float_dig'), defined('PHP_float_MAX'), ':',
    constant('PHP_FLOAT_DIG') === 15, ':',
    constant('PHP_FLOAT_EPSILON') === 2.220446049250313e-16;
''', b'1111::1:1'),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    output = parser.parse_args().output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())
    watched = [Path(__file__), *[ROOT / path for path in modules],
               *[ROOT / path for path in ('spec/semantics/modules.json', 'tests/semantics/profile.json',
                 'tests/semantics/error_handler_run.py', 'bin/php-semantics',
                 '_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so',
                 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py')]]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path.relative_to(ROOT)): digest(path) for path in watched}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    rows = []
    for name, (source_bytes, expected) in CASES.items():
        directory = output / name
        directory.mkdir()
        source = directory / 'source.php'
        source.write_bytes(source_bytes)
        result = recorded([str(ROOT / 'bin/php-semantics'), str(source), '--steps', '100000',
                           '--timeout', '90'], directory / 'model', 120)
        data = (directory / 'model.stdout').read_bytes()
        outcome = json.loads(data) if data else None
        passed = (result['exit'] == 0 and not result['timeout'] and result['interruption'] is None
                  and result['group_after'] == [] and not (directory / 'model.stderr').read_bytes()
                  and outcome is not None and outcome['frontend'] == 'accepted'
                  and outcome['checked'] == 'program' and outcome['status'] == 'normal'
                  and outcome['exit_status'] == 0 and outcome['reason'] is None
                  and base64.b64decode(outcome['stdout']) == expected
                  and base64.b64decode(outcome['stderr']) == b'')
        rows.append({'id': name, 'source': str(source), 'source_sha256': digest(source),
                     'model': result, 'outcome': outcome, 'passed': passed})
        print(name, passed, result['elapsed'], flush=True)
    assert before == {str(path.relative_to(ROOT)): digest(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = all(row['passed'] for row in rows)
    (output / 'report.json').write_text(json.dumps({
        'revision': revision, 'mode': 'production SL model-only controls', 'module_entries': len(modules),
        'selection': list(CASES), 'rows': rows, 'inputs': before,
        'profile': json.loads((ROOT / 'tests/semantics/profile.json').read_bytes()),
        'environment': {key: ENV.get(key) for key in ('LC_ALL', 'TZ', 'PHP_SPEC_SCRIPT_ENCODING')},
        'scope': 'Imported missing targets, explicit relative names and wrong final case raise caught Error. A namespaced FLOAT name shadows the global value with a different scalar type; FQN/import/fallback retain the genuine global values. Runtime defined/constant APIs preserve exact case and primitive types. These independent engine-contract controls have no native execution or source-agreement credit.',
        'native_executions': 0, 'source_credit': 0, 'passed': passed}, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

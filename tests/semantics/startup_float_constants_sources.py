#!/usr/bin/env python3
"""Original-source startup float limits, with reusable native observations."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import ENV, recorded
import startup_float_constants_cases as cases

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--baseline', action='store_true')
    parser.add_argument('--native-baseline', type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True)
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    paths = [Path(__file__), Path(cases.__file__), ROOT / '.tools/php/bin/php',
             ROOT / '_build/default/adapter/main.exe', ROOT / 'bin/php-semantics',
             ROOT / 'tests/semantics/profile.json', ROOT / 'tests/semantics/error_handler_run.py',
             ROOT / 'spec/semantics/modules.json', ROOT / 'spec/semantics/20-machine.watsup',
             ROOT / 'spec/semantics/23-named-constants.watsup',
             ROOT / 'spec/semantics/45-constant-context.watsup',
             ROOT / 'spec/semantics/46-source-compiler.watsup',
             ROOT / 'spec/semantics/89-user-constants.watsup']
    paths += [ROOT / path for path in getattr(cases, 'WATCHED', ())]
    before = {str(path.relative_to(ROOT)): digest(path) for path in paths}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
    saved = None
    if args.native_baseline:
        saved = json.loads((args.native_baseline / 'report.json').read_bytes())
        assert saved['profile'] == profile
        assert saved['inputs']['.tools/php/bin/php'] == before['.tools/php/bin/php']
    rows = []
    for name, source_bytes in cases.CASES.items():
        directory = args.output / name
        directory.mkdir()
        native_directory = args.native_baseline / name if saved else directory
        source = native_directory / 'source.php'
        if saved:
            assert source.read_bytes() == source_bytes
            native = next(row['native'] for row in saved['rows'] if row['id'] == name)
        else:
            source.write_bytes(source_bytes)
            native = recorded([str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(source)],
                              native_directory / 'native', 30)
        native_ok = (native['exit'] == 0 and not native['timeout'] and native['interruption'] is None
                     and not native['group_after'] and not (native_directory / 'native.stderr').read_bytes()
                     and (native_directory / 'native.stdout').read_bytes() == cases.OUTPUTS[name])
        model = recorded([str(ROOT / 'bin/php-semantics'), str(source), '--steps', '100000',
                          '--timeout', '90'], directory / 'model', 120)
        outcome = json.loads((directory / 'model.stdout').read_bytes())
        common = (native_ok and not model['timeout'] and model['interruption'] is None
                  and not model['group_after'] and not (directory / 'model.stderr').read_bytes()
                  and outcome['frontend'] == 'accepted' and outcome['checked'] == 'program')
        if args.baseline:
            passed = common and model['exit'] == 1 and outcome['status'] == 'unsupported'
        else:
            passed = (common and model['exit'] == 0 and outcome['status'] == 'normal'
                      and outcome['exit_status'] == native['exit'] and outcome['reason'] is None
                      and base64.b64decode(outcome['stdout']) == (native_directory / 'native.stdout').read_bytes()
                      and base64.b64decode(outcome['stderr']) == (native_directory / 'native.stderr').read_bytes())
        rows.append({'id': name, 'source': str(source), 'source_sha256': digest(source),
                     'native': native, 'native_reused': bool(saved), 'model': model, 'outcome': outcome,
                     'passed': passed, 'agreement_credit': int(passed and not args.baseline)})
        print(name, passed, outcome['status'], outcome['reason'], flush=True)
        (args.output / 'report.json').write_text(json.dumps({
            'revision': revision, 'inputs': before, 'profile': profile,
            'environment': {key: ENV.get(key) for key in ('LC_ALL', 'TZ', 'PHP_SPEC_SCRIPT_ENCODING')},
            'scope': 'current Unsupported baseline' if args.baseline else 'production-SL original-source comparisons',
            'rows': rows}, indent=2) + '\n')
    assert before == {str(path.relative_to(ROOT)): digest(path) for path in paths}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    return all(row['passed'] for row in rows)


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

#!/usr/bin/env python3
"""Startup precision is captured before parser FLOAT CONCAT folding."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import subprocess
import tempfile

from error_handler_run import recorded
from output_final_selected_parser_float_concat_cast_chain_return_modulo_error_sources import PRECISION_CASE

ROOT = Path(__file__).resolve().parents[2]


def main(output=None):
    out = output or Path(tempfile.mkdtemp(prefix='output-final-parser-float-concat-precision-', dir=ROOT / '.tools'))
    out.mkdir(exist_ok=True)
    assert not (out / 'report.json').exists()
    source = out / 'source.php'
    assert not source.exists()
    source.write_bytes(PRECISION_CASE)
    startup = out / 'startup.json'
    startup.write_text(json.dumps({'precision': 'MQ=='}) + '\n')
    profile = dict(json.loads((ROOT / 'tests/semantics/profile.json').read_text()), precision='1')
    watched = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched += [Path(__file__), Path(__file__).with_name('output_final_selected_parser_float_concat_cast_chain_return_modulo_error_sources.py'),
                ROOT / 'tests/semantics/error_handler_run.py', ROOT / 'tests/semantics/profile.json',
                ROOT / 'spec/php.watsup', ROOT / 'spec/semantics/modules.json', ROOT / 'bin/php-semantics',
                ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so', source, startup]
    fingerprint = lambda: {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    head = lambda: subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    before, revision = fingerprint(), head()
    flags = [arg for key, value in profile.items() for arg in ['-d', key + '=' + value]]
    native = recorded([str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(source)], out / 'native', 10)
    model = recorded([str(ROOT / 'bin/php-semantics'), str(source), '--startup-ini', str(startup),
                      '--steps', '100000', '--timeout', '90'], out / 'model', 120)
    outcome = json.loads((out / 'model.stdout').read_bytes())
    passed = (native['exit'] == 255 and model['exit'] == 0 and not native['timeout'] and not model['timeout']
              and not (out / 'model.stderr').read_bytes() and outcome.get('frontend') == 'accepted'
              and outcome.get('checked') == 'program' and outcome.get('status') == 'php_error'
              and outcome.get('exit_status') == 255 and outcome.get('reason') is None
              and base64.b64decode(outcome['stdout'], validate=True) == (out / 'native.stdout').read_bytes() == b'P'
              and base64.b64decode(outcome['stderr'], validate=True) == (out / 'native.stderr').read_bytes()
              and outcome.get('diagnostic') == {'class': 'DivisionByZeroError', 'message': 'TW9kdWxvIGJ5IHplcm8=', 'line': 6}
              and not [event for event in outcome['events'] if event['tag'] == 'DIAGNOSTIC'])
    after, after_revision = fingerprint(), head()
    stable = before == after and revision == after_revision
    passed &= stable
    report = {'revision': revision, 'after_revision': after_revision, 'before': before, 'after': after,
              'target': 'PHP8.5.10 CLI NTS64/vendor34308a6666b2d489c509541ea9befea9e2b42348',
              'cwd': str(ROOT), 'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': 'absent'},
              'profile': profile, 'startup': {'precision': 'MQ=='}, 'native': native, 'model': model,
              'outcome': outcome, 'stable': stable, 'passed': passed, 'source_credit': 1 if passed else 0,
              'scope': 'One original startup-precision1 parser FLOAT CONCAT and strict STRING/FLOAT witnesses.'}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, passed, flush=True)
    return passed


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    raise SystemExit(0 if main(args.output) else 1)

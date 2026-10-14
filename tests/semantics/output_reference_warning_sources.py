#!/usr/bin/env python3
"""Output callback reference-warning Throwables before callee entry."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import output_api_failure_sources as common

ROOT = common.ROOT
CASES = {
    'api-reference-warning-throw': (b'<?php echo "P";$e=new Exception;$x=99;$called=0;$warnings=0;set_error_handler(function($n){global $e,$warnings;$warnings++;throw $e;});function h(&$b,$p){global $called;$called++;return "X";}ob_start("h");echo "A";try{$x=ob_flush();}catch(Exception $c){$s=ob_get_status();$report=($c===$e?"C":"N").":".$x.":".$called.":".$warnings.":".$s["flags"].":".$s["buffer_used"];}ob_end_clean();echo "|".$report."Z";', b'PA|C:99:0:1:12401:0Z'),
}


def fingerprint():
    inputs = common.fingerprint()
    inputs['tests/semantics/output_reference_warning_sources.py'] = common.sha(Path(__file__))
    return inputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--select', help='comma-separated exact source IDs')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else list(CASES)
    assert selected and len(set(selected)) == len(selected) and all(name in CASES for name in selected)
    out = args.output or Path(tempfile.mkdtemp(prefix='output-reference-warning-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    report = {'revision': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip(),
              'before': fingerprint(), 'profile': common.PROFILE, 'selected': selected,
              'records': [], 'passed': False, 'completed': False}
    print(out, flush=True)
    try:
        for name in selected:
            directory = out / name; directory.mkdir()
            source, expected = CASES[name]; path = directory / 'source.php'; path.write_bytes(source)
            native = common.run([str(ROOT / '.tools/php/bin/php'), '-n', *common.FLAGS, str(path)], directory, 'native', 10)
            assert native.returncode == 0 and native.stdout == expected and not native.stderr, (name, native.stdout, native.stderr)
            modeled = common.run([str(ROOT / 'bin/php-semantics'), str(path), '--timeout', '60'], directory, 'model', 90)
            assert not modeled.stderr, (name, modeled.stderr)
            outcome = json.loads(modeled.stdout)
            assert modeled.returncode == 0 and outcome['status'] == 'normal' and outcome['reason'] is None, (name, outcome)
            assert base64.b64decode(outcome['stdout'], validate=True) == native.stdout, (name, outcome, native.stdout)
            assert base64.b64decode(outcome['stderr'], validate=True) == native.stderr, (name, outcome, native.stderr)
            assert outcome['exit_status'] == native.returncode
            report['records'].append({'case': name, 'source_sha256': common.sha(path),
                                      'stdout_sha256': hashlib.sha256(native.stdout).hexdigest(),
                                      'stderr_sha256': hashlib.sha256(native.stderr).hexdigest(), 'native_credit': True,
                                      'status': outcome['status']})
            print(name, outcome['status'], flush=True)
        report.update(passed=True, completed=True)
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after'] = fingerprint()
        report['passed'] = report['passed'] and report['before'] == report['after']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)
    assert report['passed'] and report['completed']


if __name__ == '__main__':
    main()

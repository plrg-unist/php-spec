#!/usr/bin/env python3
"""Independent second reference-warning failure before output callback entry."""
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
    'second-reference-warning-trace': (b'''<?php
$hits=0;$warnings=0;$x=99;
function e($n,$m){global $warnings;if(++$warnings===2){throw new Exception("F");}return true;}
function h(&$b,&$p){global $hits;$hits++;return "X";}
set_error_handler("e");
ob_start("h");echo "A";
try{$x=ob_get_flush();}catch(Exception $c){
$t=$c->getTrace();
echo "C:".$warnings.":".$hits.":".$x.":".ob_get_level().":".$t[0]["function"].":".(isset($t[0]["file"])?"F":"I").":".$t[1]["function"].":".($t[1]["file"]===__FILE__?"F":"N").":".$t[1]["line"].":".(isset($t[2])?"E":"-")."Z";}
''', b'AC:2:0:99:0:e:I:ob_get_flush:F:7:-Z'),
    'reference-warning-output-failure': (b'<?php $e=new Exception;$x=99;$called=0;$levels="";set_error_handler(function($n){global $e,$levels;$levels.=$n.";";echo "H";throw $e;});function h(&$b,$p){global $called;$called++;return "X";}ob_start("h");echo "A";try{$x=ob_flush();}catch(Exception $c){$s=ob_get_status();$report=($c===$e?"C":"N").":".$x.":".$called.":".$s["flags"].":".$s["buffer_used"];}ob_end_clean();echo "|".$report."|".$levels."Z";', b'AH|C:99:0:45169:0|2;Z'),
}


def fingerprint():
    inputs = common.fingerprint()
    inputs['tests/semantics/output_reference_warning_review_sources.py'] = common.sha(Path(__file__))
    return inputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--select', help='comma-separated exact source IDs')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else list(CASES)
    assert selected and len(set(selected)) == len(selected) and all(name in CASES for name in selected)
    out = args.output or Path(tempfile.mkdtemp(prefix='output-reference-warning-review-', dir=ROOT / '.tools'))
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
                                      'stderr_sha256': hashlib.sha256(native.stderr).hexdigest(), 'native_credit': True})
            print(name, 'exact', flush=True)
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

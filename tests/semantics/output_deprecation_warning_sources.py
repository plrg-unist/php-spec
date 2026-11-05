#!/usr/bin/env python3
"""Defined output-handler returns survive produced-output warning throws."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

import output_api_failure_sources as common

ROOT = common.ROOT


def source(retval, operation, chunk):
    return (b'<?php echo "P";$e=new Exception;$once=true;$x=99;'
            b'set_error_handler(function(){global $e;echo "W";throw $e;});'
            b'function h($b,$p){global $once;if($once){$once=false;echo "H";}return '
            + retval + b';}ob_start("h",' + str(chunk).encode() + b');'
            + (b'echo "A";' if chunk == 0 else b'')
            + b'try{$x=' + operation + b';}catch(Exception $c){'
            b'$r=($c===$e?"C":"N").":".$x.":".ob_get_level();'
            b'if(ob_get_level()){$s=ob_get_status();'
            b'$r.=":".$s["flags"].":".$s["buffer_used"];}}'
            b'if(ob_get_level()){ob_end_clean();}echo "|".$r;')


CASES = {
    'vm-string': (source(b'"X".$b', b'print "A"', 1), b'PWXA|C:99:1:20593:0'),
    'vm-false': (source(b'false', b'print "A"', 1), b'PWAH|C:99:1:12401:0'),
    'vm-true': (source(b'true', b'print "A"', 1), b'PW|C:99:1:20593:0'),
    'vm-null': (source(b'null', b'print "A"', 1), b'PW|C:99:1:20593:0'),
    'api-flush': (source(b'"X".$b', b'ob_flush()', 0), b'PWXA|C:99:1:20593:0'),
    'api-clean': (source(b'"X".$b', b'ob_clean()', 0), b'PW|C:99:1:20593:0'),
    'api-end-flush': (source(b'"X".$b', b'ob_end_flush()', 0), b'PWXA|C:99:0'),
    'api-end-clean': (source(b'"X".$b', b'ob_end_clean()', 0), b'PW|C:99:0'),
    'api-get-flush': (source(b'"X".$b', b'ob_get_flush()', 0), b'PWXA|C:99:0'),
    'api-get-clean': (source(b'"X".$b', b'ob_get_clean()', 0), b'PW|C:99:0'),
}
CASES['vm-warning-return-destructor'] = (
    source(b'"X".$b', b'print "A"', 1).replace(
        b'set_error_handler(function(){global $e;echo "W";throw $e;});',
        b'class R{function __destruct(){global $e;echo "R";throw $e;}}'
        b'set_error_handler(function(){echo "W";return new R;});'),
    b'PWRXA|C:99:1:20593:0')
CASES['vm-owned-producer-reentry'] = (
    source(b'"X".$b', b'print new O', 1).replace(
        b'<?php ', b'<?php class O{function __toString(){return "A";}'
        b'function __destruct(){echo "D".ob_get_level();}}'),
    b'PWXAXD1|C:99:1:20593:0')
CASES['vm-float-current-precision'] = (
    source(b'1.234567', b'print "A"', 1).replace(
        b'echo "W";throw $e;', b'ini_set("precision","3");echo "W";throw $e;'),
    b'PW1.23|C:99:1:20593:0')
CASES['vm-normal-warning-return-trace'] = (b'''<?php
echo "P";$log="";$x=99;
class D{function __destruct(){global $log;$e=new Exception;$t=$e->getTrace();$log=$t[0]["function"].":".(isset($t[0]["file"])?"F":"I").":".(isset($t[0]["line"])?$t[0]["line"]:-1);echo "D";}}
set_error_handler(function(){return new D;});
function h($b,$p){echo "H";return false;}
ob_start("h",1);
$x=print "A";
ob_end_clean();echo "|".$x.":".$log;
''', b'PDAH|1:__destruct:F:7')
for name, lower, expected in (
    ('vm-lower-user-pending', b'function l($b,$p){return "L".$b;}ob_start("l",1);',
     b'PWXA|C:99:2:45169:20593'),
    ('vm-lower-default-pending', b'ob_start(null,1);',
     b'PWXA|C:99:2:53360:20593'),
):
    CASES[name] = (source(b'"X".$b', b'print "A"', 1)
        .replace(b'ob_start("h",1);', lower + b'ob_start("h",1);')
        .replace(b'$s=ob_get_status();$r.=":".$s["flags"].":".$s["buffer_used"];',
                 b'$a=ob_get_status(true);$r.=":".$a[0]["flags"].":".$a[1]["flags"];')
        .replace(b'if(ob_get_level()){ob_end_clean();}echo',
                 b'if(ob_get_level()){ob_end_clean();}if(ob_get_level()){ob_end_clean();}echo'), expected)
CONTROLS = {
    'final-warning-throw': b'<?php echo "P";set_error_handler(function(){throw new Exception;});function h($b,$p){echo "H";return $b;}ob_start("h");echo "A";',
    'lower-api-warning-throw': b'<?php echo "P";set_error_handler(function(){throw new Exception;});function h($b,$p){echo "H";return $b;}ob_start("h",1);ob_start();echo "A";ob_flush();',
}


def fingerprint():
    inputs = common.fingerprint()
    inputs['tests/semantics/output_deprecation_warning_sources.py'] = common.sha(Path(__file__))
    return inputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--select', help='comma-separated exact source IDs')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else list(CASES) + list(CONTROLS)
    assert selected and len(set(selected)) == len(selected)
    assert all(name in CASES or name in CONTROLS for name in selected)
    out = args.output or Path(tempfile.mkdtemp(prefix='output-deprecation-warning-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    report = {'revision': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip(),
              'before': fingerprint(), 'profile': common.PROFILE, 'selected': selected,
              'records': [], 'passed': False, 'completed': False}
    print(out, flush=True)
    try:
        for name in selected:
            directory = out / name; directory.mkdir()
            raw = CASES[name][0] if name in CASES else CONTROLS[name]
            path = directory / 'source.php'; path.write_bytes(raw)
            native = common.run([str(ROOT / '.tools/php/bin/php'), '-n', *common.FLAGS, str(path)], directory, 'native', 10)
            if name in CASES:
                assert native.returncode == 0 and native.stdout == CASES[name][1] and not native.stderr, (name, native.stdout, native.stderr)
            modeled = common.run([str(ROOT / 'bin/php-semantics'), str(path), '--timeout', '90'], directory, 'model', 120)
            assert not modeled.stderr, (name, modeled.stderr)
            outcome = json.loads(modeled.stdout)
            if name in CASES:
                assert modeled.returncode == 0 and outcome['status'] == 'normal' and outcome['reason'] is None, (name, outcome)
                assert base64.b64decode(outcome['stdout'], validate=True) == native.stdout, (name, outcome, native.stdout)
                assert base64.b64decode(outcome['stderr'], validate=True) == native.stderr, (name, outcome, native.stderr)
                assert outcome['exit_status'] == native.returncode
            else:
                assert modeled.returncode == 1 and outcome['status'] == 'unsupported', (name, outcome)
                assert outcome['reason'] == 'abrupt user output-handler deprecation callback cleanup', (name, outcome)
                assert base64.b64decode(outcome['stdout'], validate=True) == b'P', (name, outcome)
            report['records'].append({'case': name, 'source_sha256': common.sha(path),
                                      'stdout_sha256': hashlib.sha256(native.stdout).hexdigest(),
                                      'stderr_sha256': hashlib.sha256(native.stderr).hexdigest(),
                                      'status': outcome['status'], 'native_credit': name in CASES})
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

#!/usr/bin/env python3
"""Independent raw-return, cleanup mutation, callback demand and trace checks."""
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
    'complete-unused-print-demand': (
        b'<?php echo "P";$r=true;$e=new Exception;$first=true;function &h($b,$p){'
        b'global $r,$e,$first;if($first){$first=false;return $r;}throw $e;}'
        b'ob_start("h",1);print "A";$s=ob_get_status();try{ob_end_clean();}'
        b'catch(Exception $c){}echo "|".$s["flags"].":".($r===true?"T":"N");',
        b'P1|20593:T'),
    'value-return-reference-backed-false': (
        b'<?php echo "P";$r=false;$alias=&$r;function h($b,$p){global $r;return $r;}'
        b'ob_start("h",1);$x=print "A";$s=ob_get_status();ob_end_clean();'
        b'echo "|".$x.":".$s["flags"].":".($r===false?"F":"N").":".($alias===false?"F":"N");',
        b'PA|1:12401:F:F'),
    'warning-retval-destructor-mutates-false-api': (
        b'''<?php
echo "P";$r=true;$x=99;
class D{function __destruct(){global $r;$r=false;echo "D";throw new Exception("F");}}
set_error_handler(function(){return new D;});
function &h($b,$p){global $r;echo "H";return $r;}
ob_start("h");echo "A";
try{$x=ob_get_flush();}catch(Exception $c){$t=$c->getTrace();echo "|".$x.":".($r===false?"F":"N").":".ob_get_level().":".$t[0]["function"].":".(isset($t[0]["file"])?"F":"I").":".(isset($t[1]["function"])?$t[1]["function"]:"missing").":".(isset($t[1]["file"])&&$t[1]["file"]===__FILE__?"F":"N").":".(isset($t[1]["line"])?$t[1]["line"]:-1);}
''',
        b'PD|99:F:0:__destruct:I:ob_get_flush:F:7'),
    'warning-retval-destructor-mutates-false-vm': (
        b'''<?php
echo "P";$r=true;$x=99;$once=true;
class D{function __destruct(){global $r;$r=false;echo "D";throw new Exception("F");}}
set_error_handler(function(){return new D;});
function &h($b,$p){global $r,$once;if($once){$once=false;echo "H";}return $r;}
ob_start("h",1);
try{$x=print "A";}catch(Exception $c){$t=$c->getTrace();$s=ob_get_status();$report=$x.":".($r===false?"F":"N").":".$s["flags"].":".$t[0]["function"].":".(isset($t[0]["file"])?"F":"I").":".(isset($t[0]["line"])?$t[0]["line"]:-1).":".(isset($t[1])?"E":"-");}
ob_end_clean();echo "|".$report;
''',
        b'PD|99:F:20593:__destruct:F:7:-'),
    'warning-rebinds-global-and-throws': (
        b'<?php echo "P";$r=true;$q=false;$e=new Exception;$x=99;'
        b'set_error_handler(function(){global $e;$GLOBALS["r"]=&$GLOBALS["q"];echo "W";throw $e;});'
        b'function &h($b,$p){global $r;echo "H";return $r;}ob_start("h");echo "A";'
        b'try{$x=ob_get_flush();}catch(Exception $c){echo "|".($c===$e?"C":"N").":".$x.":".'
        b'($r===false?"F":"N").":".($q===false?"F":"N").":".ob_get_level();}',
        b'PW1|C:99:F:F:0'),
    'callee-cleanup-rebinds-global-and-throws': (
        b'<?php echo "P";$r=true;$q=false;$x=99;'
        b'class D{function __destruct(){$GLOBALS["r"]=&$GLOBALS["q"];throw new Exception("D");}}'
        b'function &h($b,$p){global $r;$d=new D;return $r;}ob_start("h");echo "A";'
        b'try{$x=ob_get_flush();}catch(Exception $c){echo "|".$x.":".($r===false?"F":"N").":".'
        b'($q===false?"F":"N").":".ob_get_level().":".$c->getMessage();}',
        b'P1|99:F:F:0:D'),
    'implicit-null-materializes-reference': (
        b'<?php echo "P";$n=0;set_error_handler(function(){global $n;$n++;return true;});'
        b'function &h($b,$p){}ob_start("h");echo "A";$v=ob_get_flush();echo "|".$v.":".$n;',
        b'P|A:1'),
    'literal-false-notice-fresh-throw': (
        b'<?php echo "P";$x=99;set_error_handler(function(){throw new Exception("N");});'
        b'function &h($b,$p){return false;}ob_start("h");echo "A";'
        b'try{$x=ob_get_flush();}catch(Exception $c){echo "|".$x.":".ob_get_level().":".$c->getMessage();}',
        b'P|99:0:N'),
}


def fingerprint():
    inputs = common.fingerprint()
    inputs['tests/semantics/output_reference_return_review_sources.py'] = common.sha(Path(__file__))
    for name in ('vendor/php-src/Zend/zend_operators.c', 'vendor/php-src/Zend/zend_operators.h'):
        inputs[name] = common.sha(ROOT / name)
    return inputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--select', help='comma-separated exact source IDs')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else list(CASES)
    assert selected and len(set(selected)) == len(selected) and all(name in CASES for name in selected)
    out = args.output or Path(tempfile.mkdtemp(prefix='output-reference-return-review-', dir=ROOT / '.tools'))
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
            modeled = common.run([str(ROOT / 'bin/php-semantics'), str(path), '--timeout', '90'], directory, 'model', 120)
            assert not modeled.stderr, (name, modeled.stderr)
            outcome = json.loads(modeled.stdout)
            assert modeled.returncode == 0 and outcome['status'] == 'normal' and outcome['reason'] is None, (name, outcome)
            assert base64.b64decode(outcome['stdout'], validate=True) == native.stdout, (name, outcome, native.stdout)
            assert base64.b64decode(outcome['stderr'], validate=True) == native.stderr, (name, outcome, native.stderr)
            assert outcome['exit_status'] == native.returncode
            report['records'].append({'case': name, 'source_sha256': common.sha(path),
                                      'stdout_sha256': hashlib.sha256(native.stdout).hexdigest(),
                                      'stderr_sha256': hashlib.sha256(native.stderr).hexdigest(),
                                      'native_credit': True, 'status': outcome['status']})
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

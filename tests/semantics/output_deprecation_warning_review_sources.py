#!/usr/bin/env python3
"""Independent normal retval, lower routing and ownership after deprecation throws."""
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
    'false-result-default-lower': (
        b'<?php echo "P";$e=new Exception;$x=99;set_error_handler(function(){global $e;echo "W";throw $e;});function h($b,$p){echo "H";return false;}ob_start(null,1);ob_start("h",1);try{$x=print "A";}catch(Exception $c){$s=ob_get_status(true);$r=($c===$e?"C":"N").":".$x.":".$s[1]["flags"].":".$s[0]["flags"].":".$s[0]["buffer_used"];}ob_end_clean();ob_end_clean();echo "|".$r;',
        b'PWAH|C:99:12401:53360:0'),
    'string-result-pending-user-lower': (
        b'<?php echo "P";$e=new Exception;$x=99;$once=true;$lower=0;set_error_handler(function(){global $e;echo "W";throw $e;});function h($b,$p){global $once;if($once){$once=false;echo "H";}return "X".$b;}function low($b,$p){global $lower;$lower++;return "L".$b;}ob_start("low",1);ob_start("h",1);try{$x=print "A";}catch(Exception $c){$s=ob_get_status(true);$r=($c===$e?"C":"N").":".$x.":".$s[1]["flags"].":".$s[0]["flags"].":".$lower;}ob_end_clean();ob_end_clean();echo "|".$r;',
        b'PWXA|C:99:20593:45169:0'),
    'suppressed-result-retains-lower-warning-output': (
        b'<?php echo "P";$e=new Exception;$once=true;$first=true;$lower=0;set_error_handler(function(){global $e,$first;if($first){$first=false;echo "W";throw $e;}return true;});function h($b,$p){global $once;if($once){$once=false;echo "H";}return null;}function low($b,$p){global $lower;$lower++;return "L".$b;}ob_start("low",1);ob_start("h",1);try{echo "A";}catch(Exception $c){$s=ob_get_status(true);$r=($c===$e?"C":"N").":".$s[1]["flags"].":".$s[0]["flags"].":".$s[0]["buffer_used"].":".$lower;}ob_end_clean();$v=ob_get_clean();echo "|".$v.":".$lower.":".$r;',
        b'P|W:1:C:20593:32881:1:0'),
    'get-flush-owner-throw-replaces-pending': (
        b'<?php echo "P";$e=new Exception;$f=new Exception;$x=99;class H{function h($b,$p){echo "H";return "X".$b;}function __destruct(){global $f;echo "D".ob_get_level();throw $f;}}set_error_handler(function(){global $e;echo "W";throw $e;});ob_start([new H,"h"]);echo "A";try{$x=ob_get_flush();}catch(Exception $c){echo "|".($c===$f?"F":"N").($c->getPrevious()===$e?"P":"N").":".$x.":".ob_get_level();}',
        b'PWXAD0|FP:99:0'),
    'clean-false-discards-live-buffer': (
        b'<?php echo "P";$e=new Exception;$x=99;set_error_handler(function(){global $e;echo "W";throw $e;});function h($b,$p){echo "H";return false;}ob_start(null,1);ob_start("h");echo "A";try{$x=ob_clean();}catch(Exception $c){$s=ob_get_status(true);$r=($c===$e?"C":"N").":".$x.":".$s[1]["flags"].":".$s[0]["flags"].":".$s[0]["buffer_used"];}ob_end_clean();$v=ob_get_flush();echo "|".$v.":".$r;',
        b'PW|W:C:99:12401:32880:1'),
    'warning-retval-destructor-fresh-getter-trace': (
        b'''<?php
echo "P";$x=99;$log="";
class D{function __destruct(){global $log;$s=ob_get_status();$log="D".$s["flags"].":".ob_get_contents();echo "D";throw new Exception("F");}}
set_error_handler(function(){return new D;});
function h($b,$p){echo "H";return "X".$b;}
ob_start("h");echo "A";
try{$x=ob_get_flush();}catch(Exception $c){$t=$c->getTrace();echo "|".$x.":".$log.":".ob_get_level().":".$t[0]["function"].":".(isset($t[0]["file"])?"F":"I").":".(isset($t[1]["function"])?$t[1]["function"]:"missing").":".(isset($t[1]["file"])&&$t[1]["file"]===__FILE__?"F":"N").":".(isset($t[1]["line"])?$t[1]["line"]:-1).":".($c->getPrevious()===null?"0":"P");}
''',
        b'PDXA|99:D8305:AH:0:__destruct:I:ob_get_flush:F:7:0'),
    'warning-retval-destructor-fresh-vm-trace': (
        b'''<?php
echo "P";$x=99;$once=true;
class D{function __destruct(){echo "D";throw new Exception("F");}}
set_error_handler(function(){return new D;});
function h($b,$p){global $once;if($once){$once=false;echo "H";}return "X".$b;}
ob_start("h",1);
try{$x=print "A";}catch(Exception $c){$t=$c->getTrace();$r=$x.":".$t[0]["function"].":".(isset($t[0]["file"])?"F":"I").":".(isset($t[0]["line"])?$t[0]["line"]:-1).":".(isset($t[1])?"E":"-");}
ob_end_clean();echo "|".$r;
''',
        b'PDXA|99:__destruct:F:7:-'),
}


def fingerprint():
    inputs = common.fingerprint()
    inputs['tests/semantics/output_deprecation_warning_review_sources.py'] = common.sha(Path(__file__))
    for name in ('vendor/php-src/Zend/zend.c', 'vendor/php-src/Zend/zend_objects.c'):
        inputs[name] = common.sha(ROOT / name)
    return inputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--select', help='comma-separated exact source IDs')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else list(CASES)
    assert selected and len(set(selected)) == len(selected) and all(name in CASES for name in selected)
    out = args.output or Path(tempfile.mkdtemp(prefix='output-deprecation-warning-review-', dir=ROOT / '.tools'))
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

#!/usr/bin/env python3
"""Independent original-source automatic output reference-warning throws."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

import output_reference_warning_sources as prior

common = prior.common
ROOT = common.ROOT
CASES = {
    'produced-deprecation-cursor-disable': (
        b'<?php echo "P";$log="";set_error_handler(function(){global $log;$s=ob_get_status();$log=$s["flags"];return true;});function h($b,$p){echo "H";return false;}ob_start("h",1);echo "A";ob_end_clean();echo "|".$log;',
        b'PAH|8305'),
    'echo-first-warning-produced': (
        b'<?php echo "P";$e=new Exception;$called=0;$warnings=0;set_error_handler(function(){global $e,$warnings;$warnings++;echo "W";throw $e;});function h(&$b,$p){global $called;$called++;return "X";}ob_start("h",1);try{echo "A","B";}catch(Exception $c){$s=ob_get_status();$r=($c===$e?"C":"N").":".$called.":".$warnings.":".$s["flags"].":".$s["buffer_used"];}ob_end_clean();echo "|".$r;',
        b'PAW|C:0:1:45169:0'),
    'print-second-warning-typed-prefix': (
        b'<?php declare(strict_types=1);echo "P";$e=new Exception;$x=99;$called=0;$warnings=0;set_error_handler(function(){global $e,$warnings;$warnings++;echo $warnings;if($warnings===2){throw $e;}return true;});function h(int &$b,int &$p){global $called;$called++;return "X";}ob_start("h",1);try{$x=print "7";}catch(Exception $c){$s=ob_get_status();$r=($c===$e?"C":"N").":".$x.":".$called.":".$warnings.":".$s["flags"];}ob_end_clean();echo "|".$r;',
        b'P712|C:99:0:2:45169'),
    'echo-phase-warning-known-prefix': (
        b'<?php echo "P";$e=new Exception;$called=0;set_error_handler(function(){global $e;throw $e;});function h($b,&$p){global $called;$called++;return "X";}function emit(){echo "A";echo "B";}ob_start("h",1);try{emit();}catch(Exception $c){$s=ob_get_status();$r=($c===$e?"C":"N").":".$called.":".$s["flags"];}ob_end_clean();echo "|".$r;',
        b'PA|C:0:12401'),
    'lower-default-threshold': (
        b'<?php echo "P";$e=new Exception;set_error_handler(function(){global $e;echo "W";throw $e;});function h(&$b,$p){return "X";}ob_start(null,1);ob_start("h",1);try{echo "A";}catch(Exception $c){$s=ob_get_status(true);$r=($c===$e?"C":"N").":".$s[0]["flags"].":".$s[0]["buffer_used"].":".$s[1]["flags"];}ob_end_clean();ob_end_clean();echo "|".$r;',
        b'PAW|C:20592:0:45169'),
    'lower-user-threshold-skips-reference-warning': (
        b'<?php echo "P";$e=new Exception;$warnings=0;$lower=0;set_error_handler(function(){global $e,$warnings;$warnings++;throw $e;});function h(&$b,$p){return "X";}function low(&$b,&$p){global $lower;$lower++;return "L".$b;}ob_start("low",1);ob_start("h",1);try{echo "A";}catch(Exception $c){$s=ob_get_status(true);$r=($c===$e?"C":"N").":".$warnings.":".$lower.":".$s[0]["flags"].":".$s[1]["flags"];}ob_end_clean();ob_end_clean();echo "|".$r;',
        b'PA|C:1:0:12401:12401'),
    'lower-user-below-threshold-remains-enabled': (
        b'<?php echo "P";$e=new Exception;$lower=0;set_error_handler(function(){global $e;throw $e;});function h(&$b,$p){return "X";}function low($b,$p){global $lower;$lower++;return "L".$b;}ob_start("low",99);ob_start("h",1);try{echo "A";}catch(Exception $c){$s=ob_get_status(true);$r=($c===$e?"C":"N").":".$s[0]["flags"].":".$s[0]["buffer_used"].":".$lower;echo "C";}ob_end_clean();$v=ob_get_flush();echo "|".$v.":".$lower.":".$r;',
        b'PLAC|AC:1:C:113:1:0'),
    'warning-retires-borrowed-receiver': (
        b'<?php echo "P";$e=new Exception;$log="";$warnings=0;$called=0;class H{function h(&$b,&$p){global $called;$called++;return "X";}function __destruct(){global $log;$log.="D".ob_get_level();}}$r=new H;$cb=[&$r,"h"];set_error_handler(function(){global $e,$warnings,$r;$warnings++;if($warnings===1){$r=null;return true;}throw $e;});ob_start($cb,1);unset($cb);try{echo "A";}catch(Exception $c){$s=ob_get_status();$report=($c===$e?"C":"N").":".$log.":".$warnings.":".$called.":".$s["flags"];}ob_end_clean();echo "|".$report;',
        b'PA|C:D1:2:0:12401'),
    'owned-stringable-retires-before-print-catch': (
        b'<?php echo "P";$e=new Exception;$x=99;$log="";class O{function __toString(){return "A";}function __destruct(){global $log;$s=ob_get_status();$log.="D".ob_get_level().":".$s["flags"];echo "D";}}set_error_handler(function(){global $e;echo "W";throw $e;});function h(&$b,$p){return "X";}ob_start("h",1);try{$x=print new O;}catch(Exception $c){$r=($c===$e?"C":"N").":".$x.":".$log;}ob_end_clean();echo "|".$r;',
        b'PAWD|C:99:D1:45169'),
    'borrowed-stringable-survives-echo-catch': (
        b'<?php echo "P";$e=new Exception;$log="";class O{function __toString(){return "A";}function __destruct(){global $log;$log.="D".ob_get_level();echo "D";}}$o=new O;set_error_handler(function(){global $e;throw $e;});function h(&$b,$p){return "X";}ob_start("h",1);try{echo $o;}catch(Exception $c){$r=($c===$e?"C":"N").":".$log;}ob_end_clean();unset($o);echo "|".$r.":".$log;',
        b'PAD|C::D0'),
    'inline-html-stops-following-statement': (
        b'<?php echo "P";$e=new Exception;$called=0;set_error_handler(function(){global $e;throw $e;});function h(&$b,$p){global $called;$called++;return "X";}ob_start("h",1);try{?>A<?php echo "B";}catch(Exception $c){$r=($c===$e?"C":"N").":".$called;}ob_end_clean();echo "|".$r;',
        b'PA|C:0'),
}


def fingerprint():
    inputs = prior.fingerprint()
    inputs['tests/semantics/output_automatic_reference_warning_review_sources.py'] = common.sha(Path(__file__))
    inputs['vendor/php-src/Zend/zend_execute_API.c'] = common.sha(ROOT / 'vendor/php-src/Zend/zend_execute_API.c')
    return inputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--select', help='comma-separated exact source IDs')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else list(CASES)
    assert selected and len(set(selected)) == len(selected) and all(name in CASES for name in selected)
    out = args.output or Path(tempfile.mkdtemp(prefix='output-automatic-reference-review-', dir=ROOT / '.tools'))
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

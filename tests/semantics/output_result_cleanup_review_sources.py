#!/usr/bin/env python3
"""Independent normal-output-result wrapper and receiver cleanup cases."""
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
    'normal-wrapper-destructor-before-deprecation': (b'<?php $log="";$warnings="";set_error_handler(function($n){global $warnings;$warnings.=($n===E_DEPRECATED?"P":"W");return true;});class D{function __destruct(){global $log;$s=ob_get_status();$log.="D".ob_get_level().":".$s["flags"].":".$s["buffer_used"].";";echo "H";}}function h(&$b,$p){$b=new D;return "X";}ob_start("h");echo "A";$x=ob_get_flush();echo "|".$x."|".$log."|".$warnings."Z";', b'X|A|D1:113:1;|WPZ'),
    'normal-wrapper-before-alias-receiver-release': (b'<?php $e=new Exception;$x=99;$log="";set_error_handler(function(){return true;});class D{function __destruct(){global $e,$log;$log.="D".ob_get_level();throw $e;}}class C{function h(&$b,$p){global $r;$r=null;$b=new D;return "X";}function __destruct(){global $log;$log.="R".ob_get_level();}}$r=new C;$cb=[&$r,"h"];ob_start($cb);unset($cb);echo "A";try{$x=ob_get_flush();}catch(Exception $c){echo ($c===$e?"C":"N").":".$x.":".ob_get_level();}echo "|".$log."Z";', b'XC:99:0|R1D1Z'),
    'normal-wrapper-fresh-destructor-trace': (b'<?php\n$x=99;set_error_handler(function(){return true;});\nclass D{\nfunction __destruct(){throw new Exception("F");}\n}\nfunction h(&$b,$p){$b=new D;return "X";}\nob_start("h");echo "A";\ntry{$x=ob_get_flush();}catch(Exception $c){$t=$c->getTrace();echo "|".$t[0]["function"].":".(isset($t[0]["file"])?"F":"I").":".$t[1]["function"].":".($t[1]["file"]===__FILE__?"F":"N").":".$t[1]["line"].":".$x."Z";}', b'X|__destruct:I:ob_get_flush:F:8:99Z'),
}
JOIN_CASES = {
    'join-weakmap-borrowed-receiver': (b'<?php $e=new Exception;$x=99;$log="";set_error_handler(function(){return true;});class D{function __destruct(){global $e,$log;$log.="D".ob_get_level();throw $e;}}class C{function h(&$b,$p){global $r;$r=null;$b=new D;return "X";}function __destruct(){global $log;$log.="R".ob_get_level();}}$r=new C;$wm=new WeakMap;$wm[$r]=7;$wr=WeakReference::create($r);$cb=[&$r,"h"];ob_start($cb);unset($cb);echo "A";try{$x=ob_get_flush();}catch(Exception $c){echo ($c===$e?"C":"N").":".$x.":".ob_get_level().":".($wr->get()===null?"W":"L");}echo "|".$log."Z";', b'XC:99:0:W|R1D1Z'),
}


def fingerprint():
    inputs = common.fingerprint()
    inputs['tests/semantics/output_result_cleanup_review_sources.py'] = common.sha(Path(__file__))
    return inputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--select', help='comma-separated exact source IDs')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else list(CASES)
    available = CASES | JOIN_CASES
    assert selected and len(set(selected)) == len(selected) and all(name in available for name in selected)
    out = args.output or Path(tempfile.mkdtemp(prefix='output-result-cleanup-review-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    report = {'revision': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip(),
              'before': fingerprint(), 'profile': common.PROFILE, 'selected': selected,
              'records': [], 'passed': False, 'completed': False}
    print(out, flush=True)
    try:
        for name in selected:
            directory = out / name
            directory.mkdir()
            source, expected = available[name]
            path = directory / 'source.php'
            path.write_bytes(source)
            native = common.run([str(ROOT / '.tools/php/bin/php'), '-n', *common.FLAGS, str(path)], directory, 'native', 10)
            assert native.returncode == 0 and native.stdout == expected and native.stderr == b'', (name, native.stdout, native.stderr)
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

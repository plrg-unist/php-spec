#!/usr/bin/env python3
"""Default output buffers: native-first original-source differential cases."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PROFILE = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
FLAGS = [arg for key, value in PROFILE.items() for arg in ('-d', key + '=' + value)]
CASES = {
    'basic-bytes': (b'<?php ob_start(); echo "A\\0B"; print "C"; ?>D<?php $s=ob_get_clean(); echo $s === "A\\0BCD" ? "bytes" : "bad";', b'bytes'),
    'nested': (b'<?php ob_start(); echo "A"; ob_start(); echo "B"; ob_flush(); echo "C"; $s=ob_get_clean(); echo "D"; $p=ob_get_clean(); echo $p,"/",$s;', b'ABD/C'),
    'chunk-whole': (b'<?php ob_start(); ob_start(null,3); echo "abcdef"; $s=ob_get_status(); echo $s["buffer_used"],"/",$s["flags"]; ob_end_flush(); $v=ob_get_clean(); echo $v;', b'abcdef0/20592'),
    'clean-flags': (b'<?php ob_start(null,0,16); echo "A"; $r=ob_clean(); $s=ob_get_status(); echo $r ? "clean" : "bad", "/",$s["flags"];', b'clean/20496'),
    'pop-capabilities': (b'<?php ob_start(null,0,64); echo "A"; $r=ob_end_clean(); echo $r ? "removed" : "bad"; ob_start(null,0,64); echo "B"; ob_end_flush();', b'removedB'),
    'copy-get': (b'<?php ob_start(); echo "A"; $x=ob_get_contents(); echo "B"; $y=ob_get_clean(); echo $x,"/",$y;', b'A/AB'),
    'empty': (b'<?php echo ob_get_level(),"/",ob_get_contents() === false ? "false" : "bad","/",ob_get_length() === false ? "false" : "bad","/",ob_get_clean() === false ? "false" : "bad"; ob_start(); $s=ob_get_clean(); echo "/",$s === "" ? "empty" : "bad";', b'0/false/false/false/empty'),
    'status-order': (b'<?php ob_start(); $s=ob_get_status(); ob_end_clean(); foreach($s as $k=>$v) echo $k,"=",$v,";";', b'name=default output handler;type=0;flags=112;level=0;chunk_size=0;buffer_size=16384;buffer_used=0;'),
    'nested-status': (b'<?php ob_start(null,0,16); ob_start(null,1,32); $s=ob_get_status(true); $h=ob_list_handlers(); ob_end_clean(); ob_end_clean(); echo $s[0]["level"],"/",$s[1]["level"],"/",$s[1]["buffer_size"],"/",$h[0],"/",$h[1];', b'0/1/4096/default output handler/default output handler'),
    'flags': (b'<?php ob_start(null,-2,4294967408); $s=ob_get_status(); ob_end_clean(); echo $s["flags"],"/",$s["chunk_size"]; ob_start(null,0,-1); $s=ob_get_status(); ob_end_clean(); echo "/",$s["flags"];', b'112/0/-61456'),
    'empty-flush': (b'<?php ob_start(); ob_flush(); $s=ob_get_status(); ob_end_clean(); echo $s["flags"];', b'20592'),
    'notice-empty': (b'<?php set_error_handler(function($n,$s){echo $n,":",$s,"|"; return true;}); echo ob_flush() === false ? "false|" : "bad|",ob_end_flush() === false ? "false" : "bad";', b'8:ob_flush(): Failed to flush buffer. No buffer to flush|false|8:ob_end_flush(): Failed to delete and flush buffer. No buffer to delete or flush|false'),
    'get-clean-handler': (b'<?php set_error_handler(function(){echo "H"; return true;}); ob_start(null,0,0); echo "A"; $s=ob_get_clean(); $live=ob_get_contents(); echo "|",$s,"/",$live;', b'AHH|A/AHH'),
    'get-flush-handler': (b'<?php set_error_handler(function(){echo "H"; return true;}); ob_start(null,0,0); echo "A"; $s=ob_get_flush(); $live=ob_get_contents(); echo "|",$s,"/",$live;', b'AHH|A/AHH'),
    'notice-throw': (b'<?php $e=new Exception("same"); set_error_handler(function() {global $e; throw $e;}); ob_start(null,0,0); echo "A"; try {ob_get_clean();} catch(Exception $x){echo $x === $e ? "same" : "bad";}', b'Asame'),
    'shutdown': (b'<?php ob_start(null,0,0); echo "A"; register_shutdown_function(function(){echo "S",ob_get_level();});', b'AS1'),
    'destructor': (b'<?php class C{function __destruct(){echo "D",ob_get_level();}} ob_start(); $c=new C; echo "A";', b'AD1'),
    'exit': (b'<?php ob_start(); echo "A"; register_shutdown_function(function(){echo "S",ob_get_level();}); exit("E");', b'AES1'),
    'named-unpack': (b'<?php ob_start(flags:112,chunk_size:0); echo "N"; $s=ob_get_clean(); $f="ob_start"; $f(...["callback"=>null,"chunk_size"=>0]); echo "U"; $t=ob_get_clean(); echo $s,$t;', b'NU'),
    'weak-parameters': (b'<?php ob_start(null,"3",true); $s=ob_get_status("yes"); ob_end_clean(); echo $s[0]["chunk_size"],"/",$s[0]["flags"]; ob_implicit_flush(false); ob_implicit_flush();', b'3/0'),
    'strict-error': (b'<?php declare(strict_types=1); try{ob_start(null,"2");}catch(TypeError $e){echo $e->getMessage(),"/",$e->getTrace()[0]["function"];} ', b'ob_start(): Argument #2 ($chunk_size) must be of type int, string given/ob_start'),
    'null-deprecation': (b'<?php set_error_handler(function($n,$m){echo $n,":",$m,"|"; return true;}); ob_start(null,null); echo "A"; $s=ob_get_clean(); echo $s;', b'8192:ob_start(): Passing null to parameter #2 ($chunk_size) of type int is deprecated|A'),
    'allocation-boundary': (b'<?php ob_start(); echo "' + b'a' * 16384 + b'"; $s=ob_get_status(); ob_end_clean(); echo $s["buffer_size"],"/",$s["buffer_used"];', b'32768/16384'),
}
CONTROLS = {
    'handler-dependency': b'<?php echo "P"; ob_start(function($s){return $s;}); echo "A";',
    'empty-handler': b'<?php echo "P"; ob_start(""); echo "A";',
    'stdout-warning': b'<?php ini_set("display_errors","stdout"); echo "P"; ob_start(); echo $missing;',
    'stdout-fatal': b'<?php ini_set("display_errors","stdout"); echo "P"; ob_start(); echo "A"; throw new Exception("E");',
}
EXTRA = {
    'stdout-masked': (b'<?php ini_set("display_errors","stdout"); ob_start(); @$missing; $s=ob_get_clean(); echo $s === "" ? "empty" : "bad";', b'empty'),
    'stdout-handler': (b'<?php ini_set("display_errors","stdout"); set_error_handler(function(){echo "H"; return true;}); ob_start(); echo $missing; $s=ob_get_clean(); echo $s;', b'H'),
    'float-string': (b'<?php set_error_handler(function($n,$m){echo $n,":",$m,"|"; return true;}); ob_start(null,"2.5"); echo "A"; $s=ob_get_clean(); echo $s;', b'8192:Implicit conversion from float-string "2.5" to int loses precision|A'),
}
CASES.update(EXTRA)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprint():
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    names = ['spec/php.watsup', 'spec/semantics/modules.json', *modules,
             'adapter/main.ml', 'bin/php-semantics', '.tools/php/bin/php',
             '.tools/php-file.so', '_build/default/adapter/main.exe',
             'vendor/php-src/main/output.c', 'vendor/php-src/main/php_output.h',
             'tests/semantics/profile.json', 'tests/semantics/output_buffer_sources.py']
    return {name: sha(ROOT / name) for name in names}


def run(argv, directory, name, timeout):
    environment = {'LC_ALL': 'C', 'TZ': 'UTC', 'PATH': '/usr/bin:/bin'}
    (directory / (name + '.command.json')).write_text(json.dumps(
        {'argv': argv, 'cwd': str(directory), 'env': environment}) + '\n')
    result = subprocess.run(argv, cwd=directory, env=environment,
                            capture_output=True, timeout=timeout)
    for channel, raw in [('stdout', result.stdout), ('stderr', result.stderr)]:
        (directory / (name + '.' + channel)).write_bytes(raw)
    (directory / (name + '.exit')).write_text(str(result.returncode) + '\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--select', help='comma-separated exact IDs')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else list(CASES) + list(CONTROLS)
    assert selected and len(set(selected)) == len(selected)
    assert all(name in CASES or name in CONTROLS for name in selected)
    out = args.output or Path(tempfile.mkdtemp(prefix='output-buffer-sources-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    report = {'revision': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip(),
              'before': fingerprint(), 'profile': PROFILE, 'selected': selected, 'records': [],
              'completed': False, 'passed': False}
    print(out, flush=True)
    try:
        for name in selected:
            source = CASES[name][0] if name in CASES else CONTROLS[name]
            directory = out / name; directory.mkdir()
            path = directory / 'source.php'; path.write_bytes(source)
            native = run([str(ROOT / '.tools/php/bin/php'), '-n', *FLAGS, str(path)], directory, 'native', 10)
            if name in CASES:
                assert native.stdout == CASES[name][1], (name, native.stdout, CASES[name][1])
                assert native.returncode == 0, (name, native.returncode, native.stderr)
            modeled = run([str(ROOT / 'bin/php-semantics'), str(path), '--timeout', '60'], directory, 'model', 90)
            assert not modeled.stderr, (name, modeled.stdout, modeled.stderr)
            outcome = json.loads(modeled.stdout)
            if name in CASES:
                status = 'explicit_exit' if name == 'exit' else 'normal'
                assert modeled.returncode == 0 and outcome['status'] == status, (name, outcome)
                assert outcome['reason'] is None
                assert base64.b64decode(outcome['stdout'], validate=True) == native.stdout, (name, outcome, native.stdout)
                assert base64.b64decode(outcome['stderr'], validate=True) == native.stderr, (name, outcome, native.stderr)
                assert outcome['exit_status'] == native.returncode
            else:
                assert modeled.returncode == 1 and outcome['status'] == 'unsupported', (name, outcome)
                assert base64.b64decode(outcome['stdout'], validate=True) == b'P', (name, outcome)
                assert base64.b64decode(outcome['stderr'], validate=True) == b'', (name, outcome)
                assert outcome['reason'] and not any(event['tag'] == 'DISPLAY_STDOUT' for event in outcome['events'])
            report['records'].append({'case': name, 'source_sha256': sha(path), 'status': outcome['status'],
                                      'native_credit': name in CASES, 'native_exit': native.returncode,
                                      'stdout_sha256': hashlib.sha256(native.stdout).hexdigest(),
                                      'stderr_sha256': hashlib.sha256(native.stderr).hexdigest()})
            print(name, outcome['status'], flush=True)
        report.update(completed=True, passed=True)
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

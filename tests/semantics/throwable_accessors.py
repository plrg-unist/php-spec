#!/usr/bin/env python3
"""Original-source Throwable comparisons and separate unsupported controls."""
from pathlib import Path
import base64
import hashlib
import json
import os
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]


CASES = [{'id': 'five',
  'kind': 'agreement',
  'source': '<?php try{1/0;}catch(Throwable $e){} echo '
            '$e->getMessage(),"|",$e->getCode(),"|",$e->getFile(),"|",$e->getLine(),"|",$e->getPrevious()===null;'},
 {'id': 'case',
  'kind': 'agreement',
  'source': '<?php try{1/0;}catch(Throwable $e){} echo $e->GeTmEsSaGe();'},
 {'id': 'computed',
  'kind': 'agreement',
  'source': '<?php try{1/0;}catch(Throwable $e){} $m="getMessage";echo $e->$m();'},
 {'id': 'nullsafe',
  'kind': 'agreement',
  'source': '<?php try{1/0;}catch(Throwable $e){} echo $e?->getMessage();$e=null;echo '
            '$e?->getMessage();'},
 {'id': 'unknown',
  'kind': 'agreement',
  'source': '<?php try{1/0;}catch(Throwable $e){} function f(){echo '
            '"ARG";}try{$e->missing(f());}catch(Throwable $x){echo $x->getMessage();}'},
 {'id': 'severity-absent',
  'kind': 'agreement',
  'source': '<?php try{1/0;}catch(Throwable $e){} try{$e->getSeverity();}catch(Throwable $x){echo '
            '$x->getMessage();}'},
 {'id': 'positional',
  'kind': 'agreement',
  'source': '<?php try{1/0;}catch(Throwable $e){} function f($s){echo $s;return '
            '1;}try{$e->getMessage(f("A"),f("B"));}catch(Throwable $x){echo $x->getMessage();}'},
 {'id': 'positional-uncaught',
  'kind': 'agreement',
  'source': '<?php try{1/0;}catch(Throwable $e){} $e->getMessage(1,2);'},
 {'id': 'named',
  'kind': 'agreement',
  'source': '<?php try{1/0;}catch(Throwable $e){} function f($s){echo $s;return '
            '1;}try{$e->getMessage(x:f("A"),y:f("B"));}catch(Throwable $x){echo $x->getMessage();}'},
 {'id': 'named-cv',
  'kind': 'agreement',
  'source': '<?php try{1/0;}catch(Throwable $e){} try{$e->getMessage(x:$missing);}catch(Throwable '
            '$x){echo $x->getMessage();}'},
 {'id': 'positional-cv',
  'kind': 'agreement',
  'source': '<?php try{1/0;}catch(Throwable $e){} try{$e->getMessage($missing);}catch(Throwable '
            '$x){echo $x->getMessage();}'},
 {'id': 'empty-unpack',
  'kind': 'agreement',
  'source': '<?php try{1/0;}catch(Throwable $e){} echo $e->getMessage(...[]);'},
 {'id': 'positional-unpack',
  'kind': 'agreement',
  'source': '<?php try{1/0;}catch(Throwable $e){} try{$e->getMessage(...[1,2]);}catch(Throwable '
            '$x){echo $x->getMessage();}'},
 {'id': 'named-unpack',
  'kind': 'agreement',
  'source': '<?php try{1/0;}catch(Throwable $e){} try{$e->getMessage(...["x"=>1]);}catch(Throwable '
            '$x){echo $x->getMessage();}'},
 {'id': 'multiple-unpack',
  'kind': 'agreement',
  'source': '<?php try{1/0;}catch(Throwable $e){} '
            'try{$e->getMessage(...[],...[1],...[2,3]);}catch(Throwable $x){echo $x->getMessage();}'},
 {'id': 'unpack-type',
  'kind': 'agreement',
  'source': '<?php try{1/0;}catch(Throwable $e){} try{$e->getMessage(...1);}catch(Throwable $x){echo '
            '$x->getMessage();}'},
 {'id': 'ref-result',
  'kind': 'agreement',
  'source': '<?php try{1/0;}catch(Throwable $e){} $r=&$e->getMessage();$r="changed";echo '
            '$e->getMessage();'},
 {'id': 'call-chain',
  'kind': 'agreement',
  'source': '<?php try{1/0;}catch(Throwable $e){} function get(){try{1/0;}catch(Throwable $x){return '
            '$x;}}echo get()->getMessage();'},
 {'id': 'owner-release',
  'kind': 'agreement',
  'source': '<?php try{1/0;}catch(Throwable $e){} function kill(&$x){$x=null;return '
            '1;}try{$e->getMessage(kill($e));}catch(Throwable $x){echo $x->getMessage();}'},
 {'id': 'sent-object-rebind',
  'kind': 'agreement',
  'source': '<?php try{1/0;}catch(Error $e){} try{2/0;}catch(Error $other){} function '
            'kill(&$x){$x=null;return 1;} $e->getMessage($other,kill($other));'},
 {'id': 'send-throw',
  'kind': 'agreement',
  'source': '<?php try{1/0;}catch(Throwable $e){} function f(){echo "F";throw '
            '1;}try{$e->getMessage(f());}catch(Throwable $x){echo $x->getMessage();}'},
 {'id': 'nested',
  'kind': 'agreement',
  'source': '<?php try{1/0;}catch(Throwable $e){} echo '
            '$e->getPrevious()===null;try{$e->getMessage($e->getCode());}catch(Throwable $x){echo '
            '$x->getMessage();}'},
 {'id': 'finally-previous-getter',
  'kind': 'agreement',
  'source': '<?php try{try{first();}finally{second();}}catch(Throwable $e){echo '
            '$e->getPrevious()->getMessage();}'},
 {'id': 'finally-previous-uncaught',
  'kind': 'agreement',
  'source': '<?php try{first();}finally{second();}'},
 {'id': 'finally-getter-return',
  'kind': 'agreement',
  'source': '<?php function f(){try{missing();}catch(Error $e){try{return '
            '$e->getMessage();}finally{echo "F";}}} echo f();'},
 {'id': 'finally-getter-reference-return',
  'kind': 'agreement',
  'source': '<?php function &f(){try{missing();}catch(Error $e){$m=$e->getMessage();'
            'try{return $m;}finally{echo "F";}}} $r=&f();echo $r;'},
 {'id': 'unsupported-getTrace',
  'kind': 'unsupported',
  'source': '<?php try{1/0;}catch(Throwable $e){} $e->getTrace();'},
 {'id': 'unsupported-getTraceAsString',
  'kind': 'unsupported',
  'source': '<?php try{1/0;}catch(Throwable $e){} $e->getTraceAsString();'},
 {'id': 'unsupported-__construct',
  'kind': 'agreement',
  'source': '<?php try{1/0;}catch(Throwable $e){} $e->__construct();'},
 {'id': 'unsupported-__toString',
  'kind': 'unsupported',
  'source': '<?php try{1/0;}catch(Throwable $e){} $e->__toString();'},
 {'id': 'unsupported-__wakeup',
  'kind': 'unsupported',
  'source': '<?php try{1/0;}catch(Throwable $e){} $e->__wakeup();'},
 {'id': 'unsupported-__clone',
  'kind': 'unsupported',
  'source': '<?php try{1/0;}catch(Throwable $e){} $e->__clone();'},
 {'id': 'unsupported-firstclass',
  'kind': 'unsupported',
  'source': '<?php try{1/0;}catch(Throwable $e){} $f=$e->getMessage(...);'}]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    cases = CASES
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    watched = [*modules, 'spec/semantics/modules.json', 'bin/php-semantics',
               'frontend/worker.php', 'frontend/wire.php', '.tools/php-file.so',
               'tests/semantics/profile.json', 'tests/semantics/throwable_accessors.py',
               '.tools/php/bin/php', '_build/default/adapter/main.exe']
    before = {name: digest(ROOT / name) for name in watched}
    out = Path(tempfile.mkdtemp(prefix='getter-probes-', dir=ROOT / '.tools'))
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    env = dict(os.environ, LC_ALL='C', TZ='UTC')
    rows = []
    for case in cases:
        directory = out / case['id']
        directory.mkdir()
        source = directory / 'source.php'
        source.write_bytes(case['source'].encode())
        native_command = [str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(source)]
        model_command = [str(ROOT / 'bin/php-semantics'), str(source), '--timeout', '60']
        native = subprocess.run(native_command, cwd=directory, env=env, capture_output=True, timeout=65)
        model = subprocess.run(model_command, cwd=directory, env=env, capture_output=True, timeout=65)
        for name, process in [('native', native), ('model', model)]:
            (directory / (name + '.stdout')).write_bytes(process.stdout)
            (directory / (name + '.stderr')).write_bytes(process.stderr)
            (directory / (name + '.status')).write_text(str(process.returncode) + '\n')
        actual = json.loads(model.stdout)
        expected = {'stdout': base64.b64encode(native.stdout).decode(),
                    'stderr': base64.b64encode(native.stderr).decode(), 'exit_status': native.returncode}
        if case['kind'] == 'agreement':
            passed = model.returncode == 0 and not model.stderr and all(actual.get(k) == v for k, v in expected.items())
        else:
            passed = model.returncode == 1 and not model.stderr and actual.get('status') == 'unsupported'
        rows.append({'id': case['id'], 'kind': case['kind'], 'pass': passed,
                     'source_sha256': digest(source), 'actual': actual, 'native': expected,
                     'native_command': native_command, 'model_command': model_command})
        print(case['id'], passed, actual.get('status'), flush=True)
    assert before == {name: digest(ROOT / name) for name in watched}, 'inputs changed'
    report = {'result': 'pass' if all(row['pass'] for row in rows) else 'fail',
              'agreements': sum(row['kind'] == 'agreement' for row in rows),
              'unsupported_controls': sum(row['kind'] == 'unsupported' for row in rows),
              'inputs': before, 'profile': profile, 'cwd': 'each retained source directory',
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}, 'records': rows, 'raw': str(out)}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'])
    assert report['result'] == 'pass'


if __name__ == '__main__':
    main()

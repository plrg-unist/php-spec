#!/usr/bin/env python3
"""Typed declared static assignments resume through their current row."""
import base64
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
GUARD = (b'<?php class V{}class A{public static V|string $p;}'
         b'class D{public V $guard;public function __toString():string{echo "T";'
         b'$this->guard=&A::$p;unset($GLOBALS["d"]);return "s";}}A::$p=new V;')
END = b'echo "|",A::$p instanceof V?"V":A::$p;'
CASES = [
    ('direct-result', b'<?php class A{public static string $p="old";}'
     b'class D{public function __toString():string{echo "T";return "s";}}'
     b'echo (A::$p=new D),"|",A::$p;'),
    ('shared-string-sources', b'<?php class A{public static string $p="old";}'
     b'class B{public static string $p="old";}'
     b'class D{public function __toString():string{echo "T";return "s";}}'
     b'B::$p=&A::$p;echo (A::$p=new D),"|",A::$p,"|",B::$p;'),
    ('callback-new-source', b'<?php class A{public static string $p="old";}'
     b'class B{public static string $p="old";}'
     b'class D{public function __toString():string{B::$p=&A::$p;echo "T";return "s";}}'
     b'echo (A::$p=new D),"|",A::$p,"|",B::$p;'),
    ('callback-row-rebind', b'<?php class A{public static string $p="old";}'
     b'class B{public static string $p="new";}'
     b'class D{public function __toString():string{A::$p=&B::$p;echo "T";return "s";}}'
     b'$old=&A::$p;echo (A::$p=new D),"|",$old,"|",A::$p,"|",B::$p;'),
    ('callback-row-reject', b'<?php class V{}class A{public static V|string $p="old";}'
     b'class B{public static V $p;}B::$p=new V;'
     b'class D{public function __toString():string{A::$p=&B::$p;echo "T";return "s";}}'
     b'$old=&A::$p;try{A::$p=new D;}catch(TypeError $e){echo "E";}'
     b'$old="free";echo "|",$old,"|",A::$p instanceof V?"V":A::$p,"|",B::$p instanceof V?"V":B::$p;'),
    ('temporary-owner', GUARD + b'try{A::$p=new D;echo "W";}catch(TypeError $e){echo "E";}' + END),
    ('borrowed-cv-owner', GUARD + b'$d=new D;try{A::$p=$d;echo "W";}catch(TypeError $e){echo "E";}' + END),
    ('retained-cv-owner', GUARD + b'$d=new D;$keep=$d;try{A::$p=$d;echo "W";}catch(TypeError $e){echo "E";}' + END),
    ('returned-reference-owner', GUARD + b'$d=new D;function &ref(){global $d;return $d;}'
     b'try{A::$p=ref();echo "W";}catch(TypeError $e){echo "E";}' + END),
    ('returned-reference-payload', GUARD.replace(b'unset($GLOBALS["d"]);', b'$GLOBALS["d"]=null;')
     + b'$d=new D;function &ref(){global $d;return $d;}'
     b'try{A::$p=ref();echo "W";}catch(TypeError $e){echo "E";}' + END),
    ('strict-no-callback', b'<?php declare(strict_types=1);class A{public static string $p="old";}'
     b'class D{public function __toString():string{echo "T";return "s";}}'
     b'try{A::$p=new D;}catch(TypeError $e){echo "E";}echo "|",A::$p;'),
    ('nominal-no-callback', b'<?php class A{public static Stringable|string $p;}'
     b'class D{public function __toString():string{echo "T";return "s";}}'
     b'A::$p=new D;echo A::$p instanceof D?"O":"S";'),
    ('selected-class-name', b'<?php class A{public static string $p="old";}'
     b'class B{public static string $q="other";}'
     b'class D{public function __toString():string{global $c,$n;$c="B";$n="q";echo "T";return "s";}}'
     b'$c="A";$n="p";echo ($c::${$n}=new D),"|",A::$p,"|",B::$q;'),
    ('computed-name-order', b'<?php class A{public static string $p="old";}'
     b'class D{public function __toString():string{echo "T";return "s";}}'
     b'function nm(){echo "N";return "p";}function rhs(){echo "V";return new D;}'
     b'echo (A::${nm()}=rhs()),"|",A::$p;'),
    ('private-self-context', b'<?php class A{private static string $p="old";'
     b'public static function set(){echo (self::$p=new D);}'
     b'public static function get(){return self::$p;}}'
     b'class D{public function __toString():string{echo "T";return "s";}}'
     b'A::set();echo "|",A::get();'),
    ('inherited-cast', b'<?php class A{public static string $p="old";}'
     b'class P{public function __toString():string{echo "T";return "s";}}class D extends P{}'
     b'echo (A::$p=new D),"|",A::$p;'),
    ('this-temporary-owner', b'<?php class A{public static string $p="old";}'
     b'class D{public function __toString():string{echo "T";return "s";}'
     b'public function put(){return A::$p=$this;}}'
     b'$d=new D;echo $d->put(),"|",A::$p;'),
    ('nested-cast', b'<?php class A{public static string $p="old";}'
     b'class B{public static string $p="old";}'
     b'class E{public function __toString():string{echo "E";return "b";}}'
     b'class D{public function __toString():string{echo "D";B::$p=new E;return "a";}}'
     b'echo (A::$p=new D),"|",B::$p;'),
    ('callback-throw-finally', b'<?php class A{public static string $p="old";}'
     b'class D{public function __toString():string{A::$p="inner";throw new Exception("cast");}}'
     b'try{A::$p=new D;}catch(Exception $e){echo get_class($e),"|",$e->getMessage(),"|",'
     b'$e->getPrevious()===null?"none":"previous";}finally{echo "|F";}echo "|",A::$p;'),
    ('multiline-target-line', b'<?php\nclass A{public static string $p="old";}\n'
     b'class D{public function __toString():string{throw new Exception("cast");}}\n'
     b'try{\nA\n::\n$p =\nnew D;\n}catch(Exception $e){echo $e->getMessage(),"|",$e->getTrace()[0]["line"];}'),
    ('multiline-rhs-line', b'<?php\nclass A{public static string $p="old";}\n'
     b'class D{public function __toString():string{throw new Exception("cast");}}\n'
     b'try{\nA::$p =\nnew D;\n}catch(Exception $e){echo $e->getMessage(),"|",$e->getTrace()[0]["line"];}'),
]

REQUEST_CASES = {'temporary-owner', 'borrowed-cv-owner', 'retained-cv-owner',
                 'returned-reference-owner', 'returned-reference-payload'}


def request_facts(path):
    encode = lambda value: base64.b64encode(value).decode()
    entries = [b'LC_ALL=C', b'TZ=UTC']
    facts = {'env': [[encode(key), encode(value)] for key, value in
                     (entry.split(b'=', 1) for entry in entries)],
             'argv': [encode(os.fsencode(path))], 'file': encode(os.fsencode(path)),
             'seconds': '1700000000', 'microseconds': 125000,
             'variables': encode(b'EGPCS'), 'jit': True, 'cwd': encode(os.fsencode(ROOT))}
    payload = (b'PHPRQ001' + struct.pack('<qII', 1700000000, 125000, len(entries))
               + b''.join(struct.pack('<I', len(entry)) + entry for entry in entries))
    return facts, payload


def initial_fixture(checked, path, name):
    filename = json.dumps(base64.b64encode(os.fsencode(path)).decode())
    if name not in REQUEST_CASES:
        return '$php_run(' + checked['fixture'] + ',0,' + filename + ')'
    facts, _ = request_facts(path)
    sequence = lambda value: '([' + ','.join(map(str, base64.b64decode(value))) + '])'
    environment = '[' + ','.join('(' + sequence(key) + ',' + sequence(value) + ')'
                                  for key, value in facts['env']) + ']'
    argv = '[' + ','.join(sequence(value) for value in facts['argv']) + ']'
    record = ('{ENV (' + environment + '),ARGV (' + argv + '),FILE ' + sequence(facts['file'])
              + ',SECONDS (' + facts['seconds'] + '),MICROSECONDS ' + str(facts['microseconds'])
              + ',VARIABLES ' + sequence(facts['variables']) + ',JIT true,CWD ('
              + sequence(facts['cwd']) + ')}')
    return '$php_request_run(' + checked['fixture'] + ',0,' + filename + ',' + record + ')'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    names = [*modules, 'spec/semantics/modules.json', 'bin/php-semantics',
             'frontend/worker.php', 'frontend/wire.php', 'frontend/wire.py', '.tools/php-file.so',
             '.tools/php/bin/php', '_build/default/adapter/main.exe',
             '.tools/request-clock.so', 'native/request_clock.c', 'scripts/build-request-provider.sh',
             'tests/semantics/profile.json', str(Path(__file__).relative_to(ROOT))]
    before = {name: digest(ROOT / name) for name in names}
    out = Path(tempfile.mkdtemp(prefix='typed-static-string-', dir=ROOT / '.tools'))
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    environment = dict(os.environ, LC_ALL='C', TZ='UTC')
    records = []
    for name, source in CASES:
        directory = out / name
        directory.mkdir()
        path = directory / 'source.php'
        path.write_bytes(source)
        native_command = [str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(path)]
        model_command = [str(ROOT / 'bin/php-semantics'), str(path), '--timeout', '60']
        request = None
        payload_sha256 = None
        request_sha256 = None
        if name in REQUEST_CASES:
            request, payload = request_facts(path)
            context = directory / 'request.json'
            context.write_text(json.dumps(request, indent=2) + '\n')
            request_sha256 = digest(context)
            payload_path = directory / 'request.input'
            payload_path.write_bytes(payload)
            payload_sha256 = digest(payload_path)
            native_command = [*native_command[:-1], '-d', 'variables_order=EGPCS',
                              '-d', 'auto_globals_jit=1', native_command[-1]]
            with payload_path.open('rb') as stream:
                os.dup2(stream.fileno(), 198)
                try:
                    native = subprocess.run(native_command, cwd=ROOT, capture_output=True,
                                            env={'LD_PRELOAD': str(ROOT / '.tools/request-clock.so')},
                                            pass_fds=(198,), timeout=30)
                finally:
                    os.close(198)
            model_command += ['--request-context', str(context)]
        else:
            native = subprocess.run(native_command, cwd=ROOT, env=environment,
                                    capture_output=True, timeout=30)
        timed_out = False
        try:
            model = subprocess.run(model_command, cwd=ROOT, env=environment,
                                   capture_output=True, timeout=65)
            stdout, stderr, code = model.stdout, model.stderr, model.returncode
        except subprocess.TimeoutExpired as error:
            stdout, stderr, code, timed_out = error.stdout or b'', error.stderr or b'', None, True
        for label, value in [('native.stdout', native.stdout), ('native.stderr', native.stderr),
                             ('model.stdout', stdout), ('model.stderr', stderr)]:
            (directory / label).write_bytes(value)
        try:
            actual = json.loads(stdout)
        except (ValueError, UnicodeDecodeError):
            actual = {'status': 'timeout' if timed_out else 'runner_failure'}
        expected = {'stdout': base64.b64encode(native.stdout).decode(),
                    'stderr': base64.b64encode(native.stderr).decode(), 'exit_status': native.returncode}
        passed = (not timed_out and code == 0 and not stderr
                  and actual.get('status') in {'normal', 'php_error', 'static_rejection', 'explicit_exit'}
                  and all(actual.get(key) == value for key, value in expected.items()))
        records.append({'id': name, 'pass': passed, 'source_sha256': digest(path),
                        'native_command': native_command, 'model_command': model_command,
                        'request': request, 'payload_sha256': payload_sha256,
                        'request_json_sha256': request_sha256,
                        'execution_profile': 'explicit-request' if request else 'ordinary',
                        'model_exit_status': code, 'timeout': timed_out,
                        'actual': actual, 'native': expected})
        print(name, passed, actual.get('status'), flush=True)
        if not passed:
            break
    assert before == {name: digest(ROOT / name) for name in names}, 'inputs changed during run'
    report = {'result': 'pass' if len(records) == len(CASES) and all(row['pass'] for row in records) else 'fail',
              'exact': sum(row['pass'] for row in records), 'selected': len(CASES), 'inputs': before,
              'profile': profile, 'cwd': str(ROOT.resolve()),
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'other': 'inherited'},
              'request_cases': sorted(REQUEST_CASES),
              'request_transport': {'fd': 198, 'payload': 'regular file at offset zero',
                                    'loader_environment': {'LD_PRELOAD': str(ROOT / '.tools/request-clock.so')},
                                    'logical_environment': ['LC_ALL=C', 'TZ=UTC']},
              'records': records}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'], flush=True)
    assert report['result'] == 'pass'


if __name__ == '__main__':
    main()

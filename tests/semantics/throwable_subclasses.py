#!/usr/bin/env python3
"""Original-source differentials for linked source Throwable subclasses."""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
CASES = [
    ('link-private-shadow', '<?php class Child extends Exception { private $trace="shadow"; protected $code="word"; } echo (new Child)->getCode();', 'agreement'),
    ('inherited-exception-ctor', '<?php class Child extends Exception {} $e=new Child("m",2);echo get_class($e),"|",$e->getMessage(),"|",$e->getCode();', 'agreement'),
    ('inherited-error-exception-ctor', '<?php class Child extends ErrorException {} $e=new Child("m",2,3,"f.php",7);echo get_class($e),"|",$e->getSeverity(),"|",$e->getFile(),"|",$e->getLine();', 'agreement'),
    ('parent-constructor', '<?php class Child extends ErrorException { function __construct(){ parent::__construct("m",2,3,"f.php",7); } } $e=new Child;echo $e->getMessage(),"|",$e->getSeverity(),"|",$e->getFile();', 'agreement'),
    ('parent-constructor-alias', '<?php class Child extends Exception { function f(){ $x=&$this->message;parent::__construct("B");echo $x,"|",$this->message; } } (new Child("A"))->f();', 'agreement'),
    ('two-level-catch-trace', '<?php class Base extends ErrorException {} class Child extends Base {} function raiseChild(){throw new Child("m",0,9);} try{raiseChild();}catch(Exception $e){echo get_class($e),"|",$e instanceof ErrorException?"yes":"no","|",$e->getSeverity(),"|",$e->getTrace()[0]["function"];}', 'agreement'),
    ('severity-write-atomic', '<?php class Child extends ErrorException { function set($v){$this->severity=$v;} } $e=new Child;$e->set(13);echo $e->getSeverity(),"|";try{$e->set([]);}catch(TypeError $x){echo "TypeError|";}echo $e->getSeverity();', 'agreement'),
    ('subclass-cast-order', '<?php class Child extends ErrorException { private $token=1; protected $extra=2; public $x=3; } foreach((array)(new Child) as $key=>$value){echo $key,",";}', 'agreement'),
    ('final-severity-override', '<?php class Child extends ErrorException { public function getSeverity(): int { return 2; } }', 'agreement'),
    ('final-message-override', '<?php class Child extends Exception { public function getMessage(): string { return "x"; } }', 'agreement'),
    ('inherited-string-explicit', '<?php class Child extends Exception {} echo (new Child("M"))->__toString();', 'agreement'),
    ('inherited-string-echo', '<?php class Child extends Exception {} echo new Child("M");', 'agreement'),
    ('inherited-string-cast', '<?php class Child extends Exception {} echo (string)(new Child("M"));', 'agreement'),
    ('source-string-override', '<?php class Child extends Exception { public function __toString(): string { return "X"; } } echo new Child("M");', 'agreement'),
    ('parent-string-override', '<?php class Child extends Exception { public function __toString(): string { return "X".parent::__toString(); } } echo (new Child("M"))->__toString();', 'agreement'),
    ('uncaught-filename', '<?php class Child extends ErrorException {} throw new Child("m",0,3,"changed.php",17);', 'agreement'),
    ('uncaught-previous', '<?php class Child extends Exception {} throw new Child("outer",0,new Exception("inner"));', 'agreement'),
    ('uncaught-integer-message', '<?php class Child extends Exception { protected $message=7; } throw new Child;', 'agreement'),
    ('uncaught-array-message', '<?php class Child extends Exception { protected $message=[]; } throw new Child;', 'agreement'),
    ('uncaught-object-message-control', '<?php class Child extends Exception { function poison(){ $this->message=new stdClass; } } $e=new Child;$e->poison();throw $e;', 'unsupported'),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    watched = [*modules, 'spec/semantics/modules.json', 'bin/php-semantics',
               'frontend/worker.php', 'frontend/wire.php', '.tools/php-file.so',
               'tests/semantics/profile.json', 'tests/semantics/throwable_subclasses.py',
               '.tools/php/bin/php', '_build/default/adapter/main.exe']
    before = {name: digest(ROOT / name) for name in watched}
    out = Path(tempfile.mkdtemp(prefix='throwable-subclass-probes-', dir=ROOT / '.tools'))
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    env = dict(os.environ, LC_ALL='C', TZ='UTC')
    rows = []
    for case_id, source_text, kind in CASES:
        directory = out / case_id
        directory.mkdir()
        source = directory / 'source.php'
        source.write_bytes(source_text.encode())
        native = subprocess.run([str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(source)],
                                cwd=directory, env=env, capture_output=True, timeout=65)
        model = subprocess.run([str(ROOT / 'bin/php-semantics'), str(source), '--timeout', '60'],
                               cwd=directory, env=env, capture_output=True, timeout=65)
        (directory / 'native.stdout').write_bytes(native.stdout)
        (directory / 'native.stderr').write_bytes(native.stderr)
        (directory / 'model.stdout').write_bytes(model.stdout)
        (directory / 'model.stderr').write_bytes(model.stderr)
        actual = json.loads(model.stdout)
        expected = {'stdout': base64.b64encode(native.stdout).decode(),
                    'stderr': base64.b64encode(native.stderr).decode(), 'exit_status': native.returncode}
        passed = (model.returncode == 0 and not model.stderr and
                  all(actual.get(key) == value for key, value in expected.items())) if kind == 'agreement' else (
                      model.returncode == 1 and not model.stderr and actual.get('status') == 'unsupported')
        rows.append({'id': case_id, 'kind': kind, 'pass': passed,
                     'source_sha256': digest(source), 'actual': actual, 'native': expected})
        print(case_id, passed, actual.get('status'), flush=True)
    assert before == {name: digest(ROOT / name) for name in watched}, 'inputs changed'
    report = {'result': 'pass' if all(row['pass'] for row in rows) else 'fail',
              'agreements': sum(row['kind'] == 'agreement' for row in rows),
              'unsupported_controls': sum(row['kind'] == 'unsupported' for row in rows),
              'inputs': before, 'profile': profile, 'records': rows, 'raw': str(out)}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'])
    assert report['result'] == 'pass'


if __name__ == '__main__':
    main()

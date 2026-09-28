#!/usr/bin/env python3
"""Compare authored get_class calls with the pinned PHP CLI profile."""
from pathlib import Path
import base64
import hashlib
import json
import os
import subprocess
import tempfile

import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCES = {
    'object-identity': '<?php class P{} class C extends P{} echo get_class(new C),"|",get_class(new stdClass);',
    'closure-and-throwable': '<?php echo get_class(function(){}),"|",get_class(get_class(...)),"|",get_class(new Error("x"));',
    'lexical-method': '<?php class P { function f(){ echo get_class(); }} (new P)->f();',
    'inherited-instance': '<?php class P { function f(){ echo get_class(),"|",get_class($this); }} class C extends P{} (new C)->f();',
    'lexical-closure': '<?php class P { function f(){ return function(){return get_class();}; }} $f=(new P)->f(); echo $f();',
    'global-zero': '<?php get_class();',
    'dynamic-zero': '<?php $f="get_class"; $f();',
    'firstclass-zero': '<?php class P{function f(){return get_class(...);}} $f=(new P)->f(); $f();',
    'firstclass-invoked-in-method': '<?php class P{function f(){ $f=get_class(...); return $f(); }} (new P)->f();',
    'direct-type': '<?php get_class(1);',
    'null-type': '<?php get_class(null);',
    'array-type': '<?php get_class([]);',
    'dynamic-type': '<?php $f="get_class"; $f(1);',
    'firstclass-type': '<?php $f=get_class(...); $f(1);',
    'invoke-type': '<?php $f=get_class(...); $f->__invoke(1);',
    'named-type': '<?php get_class(object:1);',
    'unpack-type': '<?php get_class(...[1]);',
    'unpack-zero': '<?php get_class(...[]);',
    'named-object': '<?php echo get_class(object:new stdClass);',
    'unpack-object': '<?php echo get_class(...["object"=>new stdClass]);',
    'pipe-object': '<?php echo new stdClass |> get_class(...);',
    'arity-and-order': '<?php function a($x){echo $x;return new stdClass;} get_class(a("A"),a("B"));',
    'unknown-name': '<?php get_class(foo:1);',
    'duplicate-name': '<?php get_class(object:new stdClass,object:new stdClass);',
    'namespace-fallback': '<?php namespace N; get_class(1);',
    'namespace-user-override': '<?php namespace N; function get_class($o){return "USER";} echo get_class(new \\stdClass);',
    'alias-direct': '<?php namespace N; use function get_class as gc; gc(1);',
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    oracle = ROOT / '.tools/php/bin/php'
    oracle_hash = digest(oracle)
    before = types.syntax_validation.implementation_fingerprint()
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, ROOT / 'spec/semantics/modules.json', Path(__file__),
               ROOT / 'bin/php-semantics', ROOT / 'tests/semantics/profile.json']
    direct = {str(path.relative_to(ROOT)): digest(path) for path in watched}
    out = Path(tempfile.mkdtemp(prefix='get-class-source-', dir=ROOT / '.tools'))
    env = os.environ.copy()
    env.update(LC_ALL='C', TZ='UTC')
    rows = []
    for name, source in SOURCES.items():
        directory = out / name
        directory.mkdir()
        path = directory / 'source.php'
        path.write_bytes(source.encode())
        native_command = [str(oracle), '-n']
        for key, value in profile.items():
            native_command.extend(['-d', f'{key}={value}'])
        native_command.append(str(path))
        native = subprocess.run(native_command, cwd=directory, env=env,
                                capture_output=True, timeout=30)
        model = subprocess.run([str(ROOT / 'bin/php-semantics'), str(path),
                                '--steps', '100000', '--timeout', '45'], cwd=directory,
                               env=env, capture_output=True, timeout=55)
        (directory / 'native.stdout').write_bytes(native.stdout)
        (directory / 'native.stderr').write_bytes(native.stderr)
        (directory / 'model.stdout').write_bytes(model.stdout)
        (directory / 'model.stderr').write_bytes(model.stderr)
        try:
            result = json.loads(model.stdout)
            passed = (model.returncode == 0 and result['frontend'] == 'accepted'
                      and result['checked'] == 'program'
                      and result['status'] == ('normal' if native.returncode == 0 else 'php_error')
                      and base64.b64decode(result['stdout']) == native.stdout
                      and base64.b64decode(result['stderr']) == native.stderr
                      and result['exit_status'] == native.returncode)
        except (ValueError, KeyError):
            result = {'status': 'invalid_model_packet'}
            passed = False
        rows.append({'id': name, 'pass': passed, 'source_sha256': digest(path),
                     'native_stdout_sha256': digest(directory / 'native.stdout'),
                     'native_stderr_sha256': digest(directory / 'native.stderr'),
                     'status': result['status']})
        print(name, passed, result['status'], flush=True)
    assert before == types.syntax_validation.implementation_fingerprint()
    assert oracle_hash == digest(oracle)
    assert all(direct[key] == digest(ROOT / key) for key in direct)
    report = {'result': 'pass' if all(row['pass'] for row in rows) else 'fail',
              'cases': len(rows), 'fingerprint': before, 'direct_inputs': direct,
              'oracle_sha256': oracle_hash, 'profile': profile, 'rows': rows,
              'raw': str(out)}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'])
    return report['result'] == 'pass'


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)

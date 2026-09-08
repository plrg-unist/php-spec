#!/usr/bin/env python3
"""Retain engine defect observations; a reproduced crash is never conformance."""
import base64
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'frontend'))
import wire
sys.path.insert(0, str(ROOT / 'tests'))
import validate as syntax_validation
PHP = ROOT / '.tools/php/bin/php'
CASES = [
    ('relative-static-no-parent', 'class C { function f(): namespace\\static {} }', 'lint', -11, b''),
    ('relative-static-parent', 'class P {} class C extends P { function f(): namespace\\static { return new P; } } echo ((new C)->f()) instanceof P;', 'execute', 0, b'1'),
    ('bare-static-parent-control', 'class P {} class C extends P { function f(): static { return new P; } } echo ((new C)->f()) instanceof P;', 'execute', 255, b''),
    ('relative-static-global-control', 'function f(): namespace\\static {}', 'lint', 255, None),
    ('relative-static-new-control', 'class C { function f() { return new namespace\\static; } } echo ((new C)->f()) instanceof C;', 'execute', 0, b'1'),
]

def main():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    flags = [x for key,value in profile.items() for x in ('-d',key+'='+value)]
    env = dict(os.environ, LC_ALL='C', TZ='UTC')
    env.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    watched = [Path(__file__), PHP, ROOT / '.tools/php-file.so', ROOT / 'frontend/worker.php', ROOT / 'tests/semantics/profile.json', ROOT / 'vendor/php-src/Zend/zend_compile.c']
    def fingerprints():
        return {'implementation_closure': syntax_validation.implementation_fingerprint(), 'direct': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}}
    before = fingerprints()
    identity = subprocess.run([str(PHP),'-n',*flags,'-r','echo json_encode([PHP_VERSION,PHP_SAPI,PHP_INT_SIZE,PHP_ZTS]);'],capture_output=True,env=env,timeout=5,check=True)
    target = json.loads(identity.stdout)
    assert target == ['8.5.10','cli',8,False], target
    records = []
    for name,body,mode,status,stdout in CASES:
        source = ('<?php '+body).encode()
        requests = ''.join(wire.dumps({'op':op,'source':base64.b64encode(source).decode()})+'\n' for op in ('parse','oracle'))
        parser = subprocess.run([str(PHP),'-n',*flags,'-d','extension='+str(ROOT / '.tools/php-file.so'),str(ROOT / 'frontend/worker.php')],input=requests.encode(),capture_output=True,env=env,timeout=10,check=True)
        responses = [wire.loads(line.decode()) for line in parser.stdout.splitlines()]
        assert len(responses) == 2 and all(r['ok'] and r['accepted'] for r in responses), (name,responses)
        run = subprocess.run([str(PHP),'-n',*flags,*(['-l'] if mode == 'lint' else [])],input=source,capture_output=True,cwd=ROOT,env=env,timeout=5)
        assert run.returncode == status and (stdout is None or run.stdout == stdout), (name,run)
        if status == -11: assert run.stderr == b''
        if name == 'bare-static-parent-control': assert b'Return value must be of type C, P returned' in run.stderr
        if name == 'relative-static-global-control': assert b'Cannot use "static" when no class scope is active' in run.stderr
        records.append({'id':name,'source':source.decode(),'source_sha256':hashlib.sha256(source).hexdigest(),'mode':mode,'frontend_accepted':True,'native_parser_accepted':True,'stdout':base64.b64encode(run.stdout).decode(),'stderr':base64.b64encode(run.stderr).decode(),'returncode':run.returncode,'outcome':'engine-crash' if run.returncode < 0 else 'php-error' if run.returncode else 'normal'})
    assert before == fingerprints(), 'defect evidence inputs changed'
    report = {'scope':'oracle-only engine defect observations; no semantic agreement claim','source_pin':'34308a6666b2d489c509541ea9befea9e2b42348','target':target,'profile':profile,'environment':{'LC_ALL':'C','TZ':'UTC'},'cwd':str(ROOT),'timeout_seconds':5,'fingerprints':before,'records':records}
    (ROOT / 'coverage/semantics/engine-defects.json').write_text(json.dumps(report,indent=2)+'\n')
    print('5 engine defect/control observations retained; crash is not conformance.')

if __name__ == '__main__': main()

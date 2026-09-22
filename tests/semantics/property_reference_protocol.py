#!/usr/bin/env python3
"""Source-authenticated reference binding and temporary owner controls."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import tempfile

from recorded_worker import Worker
import request_environment as request

ROOT = Path(__file__).resolve().parents[2]
SOURCE = b'<?php class C{public int $x=1;} $o=new C; $v=2; $o->x=&$v; echo $o->x;'
PREFIX = '''
dec $ref_prep_head(pstate) : bool
def $ref_prep_head(S) = true -- if S.TODO = (PROPERTY_REF_PREP expression z) :: ptask*
def $ref_prep_head(S) = false -- otherwise
dec $ref_bind_head(pstate) : bool
def $ref_bind_head(S) = true -- if S.TODO = (PROPERTY_REF_BIND_CV pbase n_name* z) :: ptask*
def $ref_bind_head(S) = false -- otherwise
dec $ref_seek_prep(pstate, nat) : pstate
def $ref_seek_prep(S, n) = S -- if $ref_prep_head(S)
def $ref_seek_prep(S, 0) = S -- if ~$ref_prep_head(S)
def $ref_seek_prep(S, n) = $ref_seek_prep($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$ref_prep_head(S) /\\ $(n > 0)
dec $ref_seek_bind(pstate, nat) : pstate
def $ref_seek_bind(S, n) = S -- if $ref_bind_head(S)
def $ref_seek_bind(S, 0) = S -- if ~$ref_bind_head(S)
def $ref_seek_bind(S, n) = $ref_seek_bind($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$ref_bind_head(S) /\\ $(n > 0)
'''


def main():
    out = Path(tempfile.mkdtemp(prefix='property-reference-protocol-', dir=ROOT / '.tools'))
    before = request.t.syntax_validation.implementation_fingerprint()
    path = out / 'source.php'
    path.write_bytes(SOURCE)
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(SOURCE).decode()})
        assert parsed['accepted'], parsed
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'], checked
    finally:
        frontend.close()
        adapter.close()
    modules = [str(ROOT / path) for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    initial = '$php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')'
    checks = [
        'S_initial = ' + initial,
        'S_prep = $ref_seek_prep(S_initial[.COMPLETION = NORMAL], 1024)[.COMPLETION = NORMAL]',
        'S_prep.TODO = (PROPERTY_REF_PREP expression_rhs z_prep) :: ptask_prep*',
        '$call_tasks_valid(S_prep, S_prep.TODO)',
        '~$call_task_valid(S_prep, PROPERTY_REF_PREP expression_rhs $(z_prep + 1))',
        '~$call_task_valid(S_prep[.ORIGIN = eps], PROPERTY_REF_PREP expression_rhs z_prep)',
        'S_bind = $ref_seek_bind(S_prep, 1024)[.COMPLETION = NORMAL]',
        'S_bind.TODO = (PROPERTY_REF_BIND_CV (BASE_PROPERTY (POBJECT n_object) n_name_property*) n_name_source* z_bind) :: ptask_bind*',
        'n_name_property* = [120]',
        '$call_tasks_valid(S_bind, S_bind.TODO)',
        '~$call_task_valid(S_bind, PROPERTY_REF_BIND_CV (BASE_PROPERTY (POBJECT n_object) $ptascii("y")) n_name_source* z_bind)',
        '~$call_task_valid(S_bind, PROPERTY_REF_BIND_CV (BASE_PROPERTY (POBJECT n_object) n_name_property*) n_name_source* $(z_bind + 1))',
        '~$call_task_valid(S_bind[.ORIGIN = eps], PROPERTY_REF_BIND_CV (BASE_PROPERTY (POBJECT n_object) n_name_property*) n_name_source* z_bind)',
        '$heap_valid($heap_graph(S_bind))',
        '$($heap_owners($heap_graph(S_bind), HOBJECT n_object) > 0)',
        'S_done = $drive(S_bind, 1024)',
        'S_done.COMPLETION = NORMAL',
        '$heap_valid($heap_graph(S_done))',
        '$property_read(S_done, POBJECT n_object, [120], 1).RESULT = KNOWN (PINT 2)',
    ]
    fixture = out / 'protocol.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + x + '\n' for x in checks))
    result = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), *modules, str(fixture)], capture_output=True, text=True, timeout=180)
    (out / 'stdout').write_text(result.stdout)
    (out / 'stderr').write_text(result.stderr)
    assert result.returncode == 0 and result.stdout == 'true\n' and not result.stderr, result.stderr[-2400:]
    assert before == request.t.syntax_validation.implementation_fingerprint()
    (out / 'report.json').write_text(json.dumps({'result': 'pass', 'fingerprint': before,
        'source_sha256': hashlib.sha256(SOURCE).hexdigest(), 'assertions': len(checks)}, indent=2) + '\n')
    print('PASS property reference protocol', len(checks), out)


if __name__ == '__main__':
    main()

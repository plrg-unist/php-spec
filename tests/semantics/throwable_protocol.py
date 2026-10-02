#!/usr/bin/env python3
"""Throwable handler ownership, strict binding and budget resumption."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import tempfile

from recorded_worker import Worker
import request_environment as request

ROOT = Path(__file__).resolve().parents[2]
CASES = [('search-main',
  b'<?php try {1/0;} catch(Throwable $e){echo $e instanceof Error;}',
  'S.TODO = (THROW_SEARCH n) :: ptask*',
  ['S.TODO = (THROW_SEARCH n) :: ptask*',
   '$call_task_valid(S,THROW_SEARCH n)',
   '$throwable_result_valid(S)',
   '~$throwable_result_valid(S[.RESULT = KNOWN (PINT 9)])',
   '~$call_task_valid(S,THROW_SEARCH 999)',
   '$($heap_owners($heap_graph(S),HOBJECT n) > 0)',
   '~$closure_scope_complete(S[.CLOSURESCOPES = [{OBJECT n, LEXICAL PORIGIN 0 eps, CALLED PORIGIN 0 eps, RECEIVER eps, CREATION eps}]], S.ALLOCATIONS)',
        '$call_descriptors_valid(S)',
   '$heap_valid($heap_graph(S))',
   'S_done = $drive(S,1000)',
   '$heap_valid($heap_graph(S_done))',
   'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
   'S_done.COMPLETION = NORMAL',
   'S_done.TODO = eps',
   'S_done.FRAMES = eps',
   'S_done.TRACE = eps']),
 ('search-frame',
  b'<?php function f(){1/0;} try {f();} catch(Throwable $e){echo 1;}',
  'S.TODO = [THROW_SEARCH n]',
  ['S.TODO = [THROW_SEARCH n]',
   'S.FRAMES =/= eps',
   '$call_task_valid(S,THROW_SEARCH n)',
   '$call_descriptors_valid(S)',
   '$heap_valid($heap_graph(S))',
   'S_done = $drive(S,1000)',
   '$heap_valid($heap_graph(S_done))',
   'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
   'S_done.COMPLETION = NORMAL',
   'S_done.TODO = eps',
   'S_done.FRAMES = eps',
   'S_done.TRACE = eps']),
 ('catch-bind',
  b'<?php try {1/0;} catch(TypeError $x) {} catch(Throwable $e){echo 1;}',
  'S.TODO = (CATCH_BIND porigin n_index n) :: ptask*',
  ['S.TODO = (CATCH_BIND porigin n_index n) :: ptask*',
   'n_index = 1',
   '$throwable_result_valid(S)',
   '~$throwable_result_valid(S[.RESULT = KNOWN (PINT 9)])',
   '$call_task_valid(S,CATCH_BIND porigin n_index n)',
   '~$call_task_valid(S,CATCH_BIND porigin 0 n)',
   '~$call_task_valid(S,CATCH_BIND porigin n_index 999)',
   '~$call_task_valid(S,CATCH_BIND (PORIGIN 999 eps) n_index n)',
   '$call_descriptors_valid(S)',
   '$heap_valid($heap_graph(S))',
   'S_done = $drive(S,1000)',
   '$heap_valid($heap_graph(S_done))',
   'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
   'S_done.COMPLETION = NORMAL',
   'S_done.TODO = eps',
   'S_done.FRAMES = eps',
   'S_done.TRACE = eps']),
 ('throw-rethrow',
  b'<?php try {try {1/0;} catch(Error $e){throw $e;}} catch(Throwable $outer){echo $outer === $e;}',
  'S.TODO = (THROW_VALUE porigin z) :: ptask*',
  ['S.TODO = (THROW_VALUE porigin z) :: ptask*',
   '$call_task_valid(S,THROW_VALUE porigin z)',
   '~$call_task_valid(S,THROW_VALUE porigin 999)',
   '~$call_task_valid(S[.ORIGIN = eps],THROW_VALUE porigin z)',
   '$throwable_result_valid(S)',
   '~$throwable_result_valid(S[.RESULT = VARIABLE $ptascii("forged") 1])',
   '~$throwable_result_valid(S[.RESULT = VARIABLE $ptascii("e") 99])',
   '~$throwable_result_valid(S[.RESULT = KNOWN PNULL])',
   '$call_descriptors_valid(S)',
   '$heap_valid($heap_graph(S))',
   'S_done = $drive(S,1000)',
   '$heap_valid($heap_graph(S_done))',
   'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
   'S_done.COMPLETION = NORMAL',
   'S_done.TODO = eps',
   'S_done.FRAMES = eps',
   'S_done.TRACE = eps']),
 ('strict-binding',
  b'<?php class C{public string $p="old";} $c=new C;$e=&$c->p;try {try {1/0;}catch(Error $e){ech'
  b'o "BAD";}}catch(TypeError $outer){echo $c->p;}',
  'S.TODO = (CATCH_BIND porigin n_index n) :: ptask*',
  ['S.TODO = (CATCH_BIND porigin n_index n) :: ptask*',
   '$call_task_valid(S,CATCH_BIND porigin n_index n)',
   '$call_descriptors_valid(S)',
   '$heap_valid($heap_graph(S))',
   'S_done = $drive(S,1000)',
   '$heap_valid($heap_graph(S_done))',
   'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
   'S_done.COMPLETION = NORMAL',
   'S_done.TODO = eps',
   'S_done.FRAMES = eps',
   'S_done.TRACE = eps']),
 ('outer-foreach',
  b'<?php $a=[1,2];foreach($a as &$v){try {1/0;}catch(Error $e){$v+=1;}}echo $a[0],$a[1];',
  'S.TODO = (THROW_SEARCH n) :: ptask*',
  ['S.TODO = (THROW_SEARCH n) :: ptask*',
   'S.ITERATORS =/= eps',
   '$call_descriptors_valid(S)',
   '$heap_valid($heap_graph(S))',
   'S_done = $drive(S,1000)',
   '$heap_valid($heap_graph(S_done))',
   'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
   'S_done.COMPLETION = NORMAL',
   'S_done.TODO = eps',
   'S_done.FRAMES = eps',
   'S_done.TRACE = eps']),
 ('uncaught-terminal',
  b'<?php throw 1;',
  'S.TODO = [THROW_SEARCH n]',
  ['S.TODO = [THROW_SEARCH n]',
   'S.FRAMES = eps',
   '$call_descriptors_valid(S)',
   '$heap_valid($heap_graph(S))',
   'S_done = $drive(S,1000)',
   'S_done.COMPLETION = UNCAUGHT n',
   'S_done.TODO = eps',
   '$heap_valid($heap_graph(S_done))',
   '$($heap_owners($heap_graph(S_done),HOBJECT n) > 0)',
   'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)'])]
PREFIX = '''
dec $stage(pstate) : bool
def $stage(S) = true -- if STAGE
def $stage(S) = false -- otherwise
dec $seek(pstate, nat) : pstate
def $seek(S, n) = S -- if $stage(S)
def $seek(S, n) = $seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$stage(S)
  -- if $(n > 0)
dec $outputs(pevent*) : nat*
def $outputs(eps) = eps
def $outputs((OUTPUT n*) :: pevent*) = n* ++ $outputs(pevent*)
def $outputs((WARNING n* z) :: pevent*) = $outputs(pevent*)
def $outputs((DIAGNOSTIC text n* z) :: pevent*) = $outputs(pevent*)
'''


def main():
    out = Path(tempfile.mkdtemp(prefix='throwable-protocol-', dir=ROOT / '.tools'))
    before = request.t.syntax_validation.implementation_fingerprint()
    modules = [str(ROOT / p) for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    results = []
    for name, source, stage, checks in CASES:
        directory = out / name
        directory.mkdir()
        path = directory / 'source.php'
        path.write_bytes(source)
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                           'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], directory / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
            assert parsed['accepted'], (name, parsed)
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], (name, checked)
        finally:
            frontend.close()
            adapter.close()
        initial = '$php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')'
        conditions = ['S_initial = ' + initial,
                      'S = $seek(S_initial[.COMPLETION = NORMAL], 1000)[.COMPLETION = NORMAL]'] + checks
        fixture = directory / 'protocol.watsup'
        fixture.write_text(PREFIX.replace('STAGE', stage) + '\ndec $main() : bool\ndef $main() = true\n'
                           + ''.join('  -- if ' + line + '\n' for line in conditions))
        process = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                  *modules, str(fixture)], capture_output=True, text=True, timeout=300)
        (directory / 'stdout').write_text(process.stdout)
        (directory / 'stderr').write_text(process.stderr)
        assert process.returncode == 0 and process.stdout == 'true\n' and not process.stderr, (name, process.stderr[-2400:])
        results.append({'name': name, 'assertions': len(conditions),
                        'source_sha256': hashlib.sha256(source).hexdigest()})
        print(name, len(conditions), flush=True)
    assert before == request.t.syntax_validation.implementation_fingerprint()
    report = {'result': 'pass', 'fingerprint': before, 'assertions': sum(r['assertions'] for r in results),
              'cases': results, 'raw': str(out)}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, 'pass')


if __name__ == '__main__':
    main()

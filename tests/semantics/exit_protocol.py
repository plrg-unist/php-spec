#!/usr/bin/env python3
"""Exit binder authentication, terminal status and retained request roots."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import tempfile

from recorded_worker import Worker
import request_environment as request

ROOT = Path(__file__).resolve().parents[2]
CASES = [('fixed-args',
  b'<?php\nexit;echo "BAD";\n',
  'S.TODO = (EXIT_ARGS pexitcall) :: ptask*',
  ['S.TODO = (EXIT_ARGS pexitcall) :: ptask*',
   '$call_task_valid(S, EXIT_ARGS pexitcall)',
   '~$call_task_valid(S, EXIT_ARGS pexitcall[.KIND = INTRINSIC_DIE])',
   '~$call_task_valid(S, EXIT_ARGS pexitcall[.INDEX = 1])',
   '~$call_task_valid(S, EXIT_ARGS pexitcall[.SITE = PORIGIN 99 eps])',
   '~$call_task_valid(S, EXIT_ARGS pexitcall[.LINE = 99])',
   '~$call_task_valid(S, EXIT_ARGS pexitcall[.OWNER = (99)])',
   '~$call_task_valid(S[.ORIGIN = eps], EXIT_ARGS pexitcall)',
   '$call_descriptors_valid(S)',
   '$heap_valid($heap_graph(S))',
   'S_done = $drive(S,1000)',
   'S_done.COMPLETION = EXITED 0',
   '$heap_valid($heap_graph(S_done))',
   'S_done.HELD = eps',
   'S_done.FRAMES = eps',
   'S_done.TRACE = eps',
   'S_done.TODO = eps',
   'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
   '$outputs(S_done.EVENTS) = eps']),
 ('deferred-reference-send',
  b'<?php $x=4;$r=&$x;exit($r);',
  'S.TODO = (EXIT_SEND pexitcall) :: ptask*',
  ['S.TODO = (EXIT_SEND pexitcall) :: ptask*',
   '$call_task_valid(S, EXIT_SEND pexitcall)',
   '$exit_result_valid(S)',
   '~$exit_result_valid(S[.RESULT = VARIABLE $ptascii("forged") 1])',
   '~$exit_result_valid(S[.RESULT = VARIABLE $ptascii("r") 99])',
   '~$exit_result_valid(S[.RESULT = KNOWN (PINT 4)])',
   '~$call_task_valid(S, EXIT_SEND pexitcall[.INDEX = 99])',
   '~$call_task_valid(S, EXIT_SEND pexitcall[.NAMED = true])',
   '~$call_task_valid(S, EXIT_SEND pexitcall[.SENT = [REFERENCE 0]])',
   '$call_descriptors_valid(S)',
   '$heap_valid($heap_graph(S))',
   'S_done = $drive(S,1000)',
   'S_done.COMPLETION = EXITED 4',
   '$heap_valid($heap_graph(S_done))',
   'S_done.HELD = eps',
   'S_done.FRAMES = eps',
   'S_done.TRACE = eps',
   'S_done.TODO = eps',
   'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
   '$outputs(S_done.EVENTS) = eps']),
 ('unpack-prepare',
  b'<?php\nexit(...["status"=>null]);echo "UNREACHABLE";\n',
  'S.TODO = (EXIT_UNPACK_PREP pexitcall) :: ptask*',
  ['S.TODO = (EXIT_UNPACK_PREP pexitcall) :: ptask*',
   '$call_task_valid(S, EXIT_UNPACK_PREP pexitcall)',
   '$exit_result_valid(S)',
   '~$exit_result_valid(S[.RESULT = VARIABLE $ptascii("forged") 1])',
   '~$call_task_valid(S, EXIT_UNPACK_PREP pexitcall[.INDEX = 99])',
   '~$call_task_valid(S, EXIT_SEND pexitcall)',
   '~$call_task_valid(S, EXIT_UNPACK_PREP pexitcall[.NAMED = true])',
   '$call_descriptors_valid(S)',
   '$heap_valid($heap_graph(S))',
   'S_done = $drive(S,1000)',
   'S_done.COMPLETION = EXITED 0',
   '$heap_valid($heap_graph(S_done))',
   'S_done.HELD = eps',
   'S_done.FRAMES = eps',
   'S_done.TRACE = eps',
   'S_done.TODO = eps',
   'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
   '$outputs(S_done.EVENTS) = eps']),
 ('unpack-named-cursor',
  b'<?php\nexit(...["status"=>null]);echo "UNREACHABLE";\n',
  'S.TODO = (EXIT_UNPACK_NEXT pexitcall poperand 1) :: ptask*',
  ['S.TODO = (EXIT_UNPACK_NEXT pexitcall poperand 1) :: ptask*',
   'poperand = KNOWN (PARRAY n)',
   '$($heap_owners($heap_graph(S),HARRAY n) > 0)',
   '$call_task_valid(S, EXIT_UNPACK_NEXT pexitcall poperand 1)',
   '~$call_task_valid(S, EXIT_UNPACK_NEXT pexitcall[.NAMED = false] poperand 1)',
   '~$call_task_valid(S, EXIT_UNPACK_NEXT pexitcall poperand 99)',
   '~$call_task_valid(S, EXIT_UNPACK_NEXT pexitcall (KNOWN (PARRAY 999)) 1)',
   '~$call_task_valid(S, EXIT_UNPACK_NEXT pexitcall[.SENT = eps] poperand 1)',
   '$call_descriptors_valid(S)',
   '$heap_valid($heap_graph(S))',
   'S_done = $drive(S,1000)',
   'S_done.COMPLETION = EXITED 0',
   '$heap_valid($heap_graph(S_done))',
   'S_done.HELD = eps',
   'S_done.FRAMES = eps',
   'S_done.TRACE = eps',
   'S_done.TODO = eps',
   'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
   '$outputs(S_done.EVENTS) = eps']),
 ('pipe-invoke',
  b'<?php "P" |> exit(...); echo "BAD";',
  'S.TODO = (EXIT_INVOKE pexitcall) :: ptask*',
  ['S.TODO = (EXIT_INVOKE pexitcall) :: ptask*',
   '$call_task_valid(S, EXIT_INVOKE pexitcall)',
   '~$call_task_valid(S, EXIT_INVOKE pexitcall[.KIND = INTRINSIC_DIE])',
   '~$call_task_valid(S, EXIT_INVOKE pexitcall[.SENT = eps])',
   '~$call_task_valid(S, EXIT_INVOKE pexitcall[.NAMED = true])',
   '$call_descriptors_valid(S)',
   '$heap_valid($heap_graph(S))',
   'S_done = $drive(S,1000)',
   'S_done.COMPLETION = EXITED 0',
   '$heap_valid($heap_graph(S_done))',
   'S_done.HELD = eps',
   'S_done.FRAMES = eps',
   'S_done.TRACE = eps',
   'S_done.TODO = eps',
   'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
   '$outputs(S_done.EVENTS) = [80]']),
 ('request-roots-unwind',
  b'<?php $g=new stdClass;function f(){static $s; $s=new stdClass;exit(2);}f();',
  'S.TODO = (EXIT_UNWIND z) :: ptask*',
  ['S.TODO = (EXIT_UNWIND z) :: ptask*',
   '$call_task_valid(S, EXIT_UNWIND z)',
   '~$call_task_valid(S, EXIT_UNWIND 4294967296)',
   '~$call_task_valid(S[.RESULT = KNOWN (PINT 1)], EXIT_UNWIND z)',
   '~$call_task_valid(S[.ERRORORIGIN = (PORIGIN 0 eps)], EXIT_UNWIND z)',
   '|S.STATICS| = 1',
   '$call_descriptors_valid(S)',
   '$heap_valid($heap_graph(S))',
   'S_done = $drive(S,1000)',
   'S_done.COMPLETION = EXITED 2',
   '$heap_valid($heap_graph(S_done))',
   'S_done.HELD = eps',
   'S_done.FRAMES = eps',
   'S_done.TRACE = eps',
   'S_done.TODO = eps',
   'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
   '$outputs(S_done.EVENTS) = eps',
   '$lookup(S_done.ENV, $ptascii("g")) = (n_global)',
   'S_done.STORE[n_global] = DEFINED (POBJECT n_object)',
   '$($heap_owners($heap_graph(S_done),HOBJECT n_object) > 0)',
   'S_done.STATICS = [pstaticcell]',
   '$($heap_owners($heap_graph(S_done),HCELL pstaticcell.CELL) > 0)'])]

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
    out = Path(tempfile.mkdtemp(prefix='exit-protocol-', dir=ROOT / '.tools'))
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

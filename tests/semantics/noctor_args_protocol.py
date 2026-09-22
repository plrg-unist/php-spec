#!/usr/bin/env python3
"""Owned no-constructor dummy sends and authenticated paused tasks."""
from pathlib import Path
import hashlib, json, subprocess, sys, tempfile

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(tempfile.mkdtemp(prefix='noctor-protocol-', dir=ROOT/'.tools'))
sys.path.insert(0, str(Path(__file__).parent))
import request_environment as request
from recorded_worker import Worker

source = OUT/'owned.php'
source.write_text("<?php\nclass A{} function side($x){echo $x;return [new stdClass];} new A(side('A'),side('B'));echo 'C';\n")
abrupt = OUT/'abrupt.php'
abrupt.write_text("<?php\nclass A{} function side(){echo 'A';return [new stdClass];} new A(side(), missing()); echo 'Z';\n")
named = OUT/'named.php'
named.write_text("<?php\nnew stdClass(foo:1);\n")
before = request.t.syntax_validation.implementation_fingerprint()
frontend = adapter = None
try:
    frontend = Worker([str(request.t.PHP), '-n', *request.t.FLAGS, '-d',
                       'extension='+str(ROOT/'.tools/php-file.so'),
                       str(ROOT/'frontend/worker.php')], OUT/'frontend-wire')
    adapter = Worker([str(ROOT/'_build/default/adapter/main.exe'), str(ROOT)], OUT/'adapter-wire')
    parsed = frontend.request({'op':'parse','source':request.b64(source.read_bytes())})
    assert parsed['ok'] and parsed['accepted']
    checked = adapter.request({'op':'check','ast':parsed['ast'],'fixture':True})
    assert checked['ok']
    parsed_abrupt = frontend.request({'op':'parse','source':request.b64(abrupt.read_bytes())})
    assert parsed_abrupt['ok'] and parsed_abrupt['accepted']
    checked_abrupt = adapter.request({'op':'check','ast':parsed_abrupt['ast'],'fixture':True})
    assert checked_abrupt['ok']
    parsed_named = frontend.request({'op':'parse','source':request.b64(named.read_bytes())})
    assert parsed_named['ok'] and parsed_named['accepted']
    checked_named = adapter.request({'op':'check','ast':parsed_named['ast'],'fixture':True})
    assert checked_named['ok']
finally:
    try:
        if frontend: frontend.close()
    finally:
        if adapter: adapter.close()
initial = '$php_run('+checked['fixture']+', 0, '+json.dumps(request.b64(str(source).encode()))+')'
initial_abrupt = '$php_run('+checked_abrupt['fixture']+', 0, '+json.dumps(request.b64(str(abrupt).encode()))+')'
initial_named = '$php_run('+checked_named['fixture']+', 0, '+json.dumps(request.b64(str(named).encode()))+')'
prefix = '''
dec $pending_head(ptask) : pnoctorcall?
def $pending_head(NOCTOR_SEND pnoctorcall) = (pnoctorcall)
def $pending_head(ptask) = eps -- otherwise
dec $pending(ptask*) : pnoctorcall?
def $pending(eps) = eps
def $pending(ptask_head :: ptask_tail*) = (pnoctorcall)
  -- if $pending_head(ptask_head) = (pnoctorcall)
def $pending(ptask_head :: ptask_tail*) = $pending(ptask_tail*)
  -- if $pending_head(ptask_head) = eps
dec $stage(pstate) : bool
def $stage(S) = true
  -- if S.TODO = (NOCTOR_ARGS pnoctorcall) :: ptask*
  -- if pnoctorcall.INDEX = 1
  -- if |pnoctorcall.SENT| = 1
def $stage(S) = false -- otherwise
dec $seek(pstate, nat) : pstate
def $seek(S, n) = S -- if $stage(S)
def $seek(S, n) = $seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$stage(S)
  -- if $(n > 0)
dec $frame_stage(pstate) : bool
def $frame_stage(S) = true
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ORIGIN_RETURN porigin?) :: (NOCTOR_SEND pnoctorcall) :: ptask*
  -- if |pnoctorcall.SENT| = 1
def $frame_stage(S) = false -- otherwise
dec $seek_frame(pstate, nat) : pstate
def $seek_frame(S, n) = S -- if $frame_stage(S)
def $seek_frame(S, n) = $seek_frame($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$frame_stage(S)
  -- if $(n > 0)
dec $named_stage(pstate) : bool
def $named_stage(S) = true -- if S.TODO = (NOCTOR_SEND pnoctorcall) :: ptask*
def $named_stage(S) = false -- otherwise
dec $seek_named(pstate, nat) : pstate
def $seek_named(S, n) = S -- if $named_stage(S)
def $seek_named(S, n) = $seek_named($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$named_stage(S)
  -- if $(n > 0)
dec $outputs(pevent*) : nat*
def $outputs(eps) = eps
def $outputs((OUTPUT n*) :: pevent*) = n* ++ $outputs(pevent*)
def $outputs((WARNING n* z) :: pevent*) = $outputs(pevent*)
def $outputs((DIAGNOSTIC text n* z) :: pevent*) = $outputs(pevent*)
'''
checks = [
    'S_initial = '+initial,
    'S = $seek(S_initial[.COMPLETION = NORMAL], 1000)[.COMPLETION = NORMAL]',
    '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    'S.TODO = (NOCTOR_ARGS pnoctorcall) :: ptask_tail*',
    'pnoctorcall.SENT = [KNOWN (PARRAY n_array)]',
    'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_child))]',
    'S.OBJECTS[n_child] = STDINSTANCE',
    'S.OBJECTS[pnoctorcall.OBJECT] = INSTANCE porigin_class',
    '$call_task_valid(S, NOCTOR_ARGS pnoctorcall)',
    '~$call_task_valid(S[.ORIGIN = eps], NOCTOR_ARGS pnoctorcall)',
    '~$call_task_valid(S, NOCTOR_ARGS pnoctorcall[.SITE = PORIGIN 999 eps])',
    '~$call_task_valid(S, NOCTOR_ARGS pnoctorcall[.CLASS = $ptascii("B")])',
    '~$call_task_valid(S, NOCTOR_ARGS pnoctorcall[.LINE = $(pnoctorcall.LINE + 1)])',
    '~$call_task_valid(S, NOCTOR_ARGS pnoctorcall[.INDEX = 2])',
    '~$call_task_valid(S, NOCTOR_ARGS pnoctorcall[.SENT = eps])',
    '$( $heap_owners($heap_graph(S), HOBJECT pnoctorcall.OBJECT) > 0)',
    '$( $heap_owners($heap_graph(S), HARRAY n_array) > 0)',
    '$( $heap_owners($heap_graph(S), HOBJECT n_child) > 0)',
    'S_frame = $seek_frame(S[.COMPLETION = NORMAL], 1000)[.COMPLETION = NORMAL]',
    'S_frame.FRAMES = pframe :: pframe_tail*',
    'pframe.TODO = (ORIGIN_RETURN porigin_return?) :: (NOCTOR_SEND pnoctorcall_frame) :: ptask_frame*',
    'pnoctorcall_frame.SENT = [KNOWN (PARRAY n_array)]',
    '$call_descriptors_valid(S_frame)', '$heap_valid($heap_graph(S_frame))',
    '$pending(pframe.TODO) = (pnoctorcall_pending)',
    '~$call_frames_valid(S_frame, pframe[.TODO = [NOCTOR_SEND pnoctorcall_pending[.LINE = $(pnoctorcall_pending.LINE + 1)]]] :: pframe_tail*)',
    '$( $heap_owners($heap_graph(S_frame), HOBJECT pnoctorcall.OBJECT) > 0)',
    '$( $heap_owners($heap_graph(S_frame), HARRAY n_array) > 0)',
    'S_done = $drive(S, 1000)', 'S_done.COMPLETION = NORMAL',
    '$outputs(S_done.EVENTS) = [65,66,67]',
    '$heap_valid($heap_graph(S_done))',
    '$heap_owners($heap_graph(S_done), HOBJECT pnoctorcall.OBJECT) = 0',
    '$heap_owners($heap_graph(S_done), HARRAY n_array) = 0',
    '$heap_owners($heap_graph(S_done), HOBJECT n_child) = 0',
    'S_abrupt_initial = '+initial_abrupt,
    'S_abrupt = $drive(S_abrupt_initial[.COMPLETION = NORMAL], 1000)',
    'S_abrupt.COMPLETION = THROWN "Error" n_message* 2',
    'S_abrupt.FRAMES = eps', 'S_abrupt.CURRENT = eps',
    '$outputs(S_abrupt.EVENTS) = [65]',
    '$heap_valid($heap_graph(S_abrupt))',
    'S_abrupt.OBJECTS[0] = INSTANCE porigin_abrupt_class',
    'S_abrupt.OBJECTS[1] = STDINSTANCE',
    '$heap_owners($heap_graph(S_abrupt), HOBJECT 0) = 0',
    '$heap_owners($heap_graph(S_abrupt), HOBJECT 1) = 0',
    'S_named_initial = '+initial_named,
    'S_named = $seek_named(S_named_initial[.COMPLETION = NORMAL], 1000)[.COMPLETION = NORMAL]',
    'S_named.TODO = (NOCTOR_SEND pnoctorcall_named) :: ptask_named*',
    '$call_task_valid(S_named, NOCTOR_SEND pnoctorcall_named)',
    '~$call_task_valid(S_named, NOCTOR_ARGS pnoctorcall_named[.INDEX = 1])',
    '~$call_task_valid(S_named, NOCTOR_ARGS pnoctorcall_named[.INDEX = 99])',
    '~$call_task_valid(S_named, NOCTOR_UNPACK_NEXT pnoctorcall_named (KNOWN (PARRAY 99)) 99)',
]
fixture = OUT/'guard.watsup'
fixture.write_text(prefix+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+line+'\n' for line in checks))
modules = [str(ROOT/path) for path in json.loads((ROOT/'spec/semantics/modules.json').read_text())]
result = subprocess.run([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'), *modules, str(fixture)], capture_output=True, timeout=300)
(OUT/'stdout').write_bytes(result.stdout); (OUT/'stderr').write_bytes(result.stderr)
assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr, result.stderr
assert before == request.t.syntax_validation.implementation_fingerprint()
(OUT/'report.json').write_text(json.dumps({'result':'pass','fingerprint':before,'assertions':len(checks),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'abrupt_source_sha256':hashlib.sha256(abrupt.read_bytes()).hexdigest(),'named_source_sha256':hashlib.sha256(named.read_bytes()).hexdigest()},indent=2)+'\n')
print('PASS noctor protocol:',len(checks),'assertions',OUT)

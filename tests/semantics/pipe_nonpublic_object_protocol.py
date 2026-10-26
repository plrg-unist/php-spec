#!/usr/bin/env python3
"""Reached nonpublic __invoke pipe selection, receipt and cleanup."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(tempfile.mkdtemp(prefix='pipe-nonpublic-object-protocol-', dir=ROOT / '.tools'))
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import request_environment as request
from recorded_worker import Worker

SOURCES = json.loads((ROOT / 'tests/semantics/pipe_nonpublic_object_cases.json').read_text())
MODULES = [str(ROOT / path) for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
FINGERPRINT = request.t.syntax_validation.implementation_fingerprint()

PREFIX = '''
dec $review_stage(pstate, nat) : bool
def $review_stage(S, 0) = true
  -- if S.TODO = (PIPE_OBJECT_SEND (PIPE_OBJECT_TARGET (METHOD_TARGET n_receiver porigin_method) pobjectselection) pobjectselection pvalue_left z_send z_call) :: ptask*
def $review_stage(S, 1) = true
  -- if S.TODO = (PIPE_OBJECT_RESULT (METHOD_TARGET n_receiver porigin_method) pobjectselection) :: ptask*
def $review_stage(S, 2) = true
  -- if S.TODO = (PIPE_OBJECT_SEND (PIPE_OBJECT_TARGET (METHOD_TARGET n_receiver porigin_method) pobjectselection) pobjectselection pvalue_left z_send z_call) :: ptask*
  -- if $origin_node(S.SOURCES, pobjectselection.SITE) = (NExprBinaryOpPipe expression_left expression_right metadata)
  -- if $pppipe_optimized(expression_right)
def $review_stage(S, n) = false -- otherwise
dec $review_seek(pstate, nat, nat) : pstate
def $review_seek(S, n_stage, n_left) = S -- if $review_stage(S, n_stage)
def $review_seek(S, n_stage, n_left) = $review_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, n_rest)
  -- if ~$review_stage(S, n_stage)
  -- if $(n_left > 0)
  -- if n_rest = $(n_left - 1)
dec $outputs(pevent*) : nat*
def $outputs(eps) = eps
def $outputs((OUTPUT n*) :: pevent*) = n* ++ $outputs(pevent*)
def $outputs((WARNING n* z) :: pevent*) = $outputs(pevent*)
def $outputs((DIAGNOSTIC text n* z) :: pevent*) = $outputs(pevent*)
'''


def checked_source(name, stage):
    stem = name + '-stage' + str(stage)
    path = OUT / (stem + '.php')
    path.write_bytes(SOURCES[name].encode())
    frontend = adapter = None
    try:
        frontend = Worker([str(request.t.PHP), '-n', *request.t.FLAGS,
                           '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], OUT / (stem + '-frontend'))
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)],
                         OUT / (stem + '-adapter'))
        parsed = frontend.request({'op': 'parse', 'source': request.b64(path.read_bytes())})
        assert parsed['ok'] and parsed['accepted']
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok']
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    return '$php_run(' + checked['fixture'] + ', 0, ' + json.dumps(request.b64(str(path).encode())) + ')'


def run_case(name, stage, checks):
    stem = name + '-stage' + str(stage)
    fixture = OUT / (stem + '.watsup')
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                       '  -- if S_initial = ' + checked_source(name, stage) + '\n' +
                       '  -- if S_pause = $review_seek(S_initial[.COMPLETION = NORMAL], ' + str(stage) + ', 800)\n' +
                       '  -- if S = S_pause[.COMPLETION = NORMAL]\n' +
                       ''.join('  -- if ' + check + '\n' for check in checks))
    result = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                             *MODULES, str(fixture)], capture_output=True, timeout=300)
    (OUT / (stem + '.stdout')).write_bytes(result.stdout)
    (OUT / (stem + '.stderr')).write_bytes(result.stderr)
    assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr, (stem, OUT)
    print(name, stage, len(checks), 'pass', flush=True)


run_case('private-variable', 0, [
    'S.TODO = (PIPE_OBJECT_SEND (PIPE_OBJECT_TARGET (METHOD_TARGET n_receiver porigin_method) pobjectselection) pobjectselection (PINT 3) z_send z_call) :: ptask_tail*',
    '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    '$class_method_origin(S.CLASSES, porigin_method) = (pmethoddesc)',
    'pmethoddesc.VISIBILITY = PROPERTY_PRIVATE',
    '$pipe_object_send_valid(S, PIPE_OBJECT_TARGET (METHOD_TARGET n_receiver porigin_method) pobjectselection, pobjectselection, PINT 3, z_send, z_call)',
    '~$call_task_valid(S, PIPE_OBJECT_SEND (PIPE_OBJECT_TARGET (METHOD_TARGET n_receiver porigin_method) pobjectselection[.METHOD = PORIGIN 999 eps]) pobjectselection[.METHOD = PORIGIN 999 eps] (PINT 3) z_send z_call)',
    'S_done = $drive(S, 3000)', 'S_done.COMPLETION = NORMAL',
    '$outputs(S_done.EVENTS) = $ptascii("P3|4|P4|5")',
])
run_case('protected-inherited', 0, [
    'S.TODO = (PIPE_OBJECT_SEND (PIPE_OBJECT_TARGET (METHOD_TARGET n_receiver porigin_method) pobjectselection) pobjectselection (PINT 3) z_send z_call) :: ptask_tail*',
    '$class_method_origin(S.CLASSES, porigin_method) = (pmethoddesc)',
    'pmethoddesc.VISIBILITY = PROPERTY_PROTECTED',
    'pmethoddesc.OWNER =/= pobjectselection.REQUESTED',
    'S.OBJECTS[n_receiver] = INSTANCE pobjectselection.REQUESTED',
    '$pipe_object_target_identity(S, METHOD_TARGET n_receiver porigin_method, pobjectselection, true)',
    'S_done = $drive(S, 3000)', 'S_done.COMPLETION = NORMAL',
    '$outputs(S_done.EVENTS) = $ptascii("PipeChild117:3|5|PipeChild117:4|6")',
])
run_case('protected-inherited', 2, [
    'S.TODO = (PIPE_OBJECT_SEND (PIPE_OBJECT_TARGET (METHOD_TARGET n_receiver porigin_method) pobjectselection) pobjectselection (PINT 4) z_send z_call) :: ptask_tail*',
    '$class_method_origin(S.CLASSES, porigin_method) = (pmethoddesc)',
    'pmethoddesc.VISIBILITY = PROPERTY_PROTECTED',
    '$firstclass_evaluated(S, $pipe_rhs_origin(pobjectselection.SITE))',
    '$call_selected_valid(S, PIPE_OBJECT_TARGET (METHOD_TARGET n_receiver porigin_method) pobjectselection, (pobjectselection.SITE))',
])
run_case('temporary-owner', 1, [
    'S.TODO = (PIPE_OBJECT_RESULT (METHOD_TARGET n_receiver porigin_method) pobjectselection) :: ptask_tail*',
    '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    '~((HOBJECT n_receiver) <- S.ALLOCATIONS)',
    '$task_nodes(PIPE_OBJECT_RESULT (METHOD_TARGET n_receiver porigin_method) pobjectselection) = eps',
    '$call_task_valid(S, PIPE_OBJECT_RESULT (METHOD_TARGET n_receiver porigin_method) pobjectselection)',
    '~$call_task_valid(S, PIPE_OBJECT_RESULT (METHOD_TARGET n_receiver porigin_method) pobjectselection[.METHOD = PORIGIN 999 eps])',
    'S.RESULT = KNOWN (PINT 4)',
])
run_case('byref-owned-error', 0, [
    'S.TODO = (PIPE_OBJECT_SEND (PIPE_OBJECT_TARGET (METHOD_TARGET n_receiver porigin_method) pobjectselection) pobjectselection (POBJECT n_left) z_send z_call) :: ptask_tail*',
    'n_left =/= n_receiver',
    '$task_nodes(PIPE_OBJECT_SEND (PIPE_OBJECT_TARGET (METHOD_TARGET n_receiver porigin_method) pobjectselection) pobjectselection (POBJECT n_left) z_send z_call) = [HOBJECT n_left, HOBJECT n_receiver]',
    'S_done = $drive(S, 3000)', 'S_done.COMPLETION = NORMAL',
    '$outputs(S_done.EVENTS) = $ptascii("R|L|I|E|PipeRef117::__invoke(): Argument #1 ($x) could not be passed by reference|")',
])
assert FINGERPRINT == request.t.syntax_validation.implementation_fingerprint()
print('PASS pipe nonpublic object protocol: five reached stages', OUT, flush=True)

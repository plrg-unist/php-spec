#!/usr/bin/env python3
"""Reached pipe object selection, send, ownership and result receipts."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(tempfile.mkdtemp(prefix='pipe-object-protocol-', dir=ROOT / '.tools'))
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import request_environment as request
from recorded_worker import Worker

SOURCES = json.loads((ROOT / 'tests/semantics/pipe_object_cases.json').read_text())
SOURCES['scalar-rhs'] = '<?php class PipeImpossible116 { public function __invoke($x) {} } $f = new PipeImpossible116; echo 3 |> 4;\n'
MODULES = [str(ROOT / path) for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
FINGERPRINT = request.t.syntax_validation.implementation_fingerprint()

PREFIX = '''
dec $review_stage(pstate, nat) : bool
def $review_stage(S, 0) = true
  -- if S.TODO = (PIPE_OBJECT_SEND (PIPE_OBJECT_TARGET (METHOD_TARGET n_receiver porigin_method) pobjectselection) pobjectselection pvalue_left z_send z_call) :: ptask*
def $review_stage(S, 1) = true
  -- if S.TODO = (PIPE_OBJECT_RESULT (METHOD_TARGET n_receiver porigin_method) pobjectselection) :: ptask*
def $review_stage(S, 2) = true
  -- if S.TODO = (PIPE_APPLY porigin (KNOWN (PINT 3)) z_send z_call) :: ptask*
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
    fixture = OUT / (name + '-stage' + str(stage) + '.watsup')
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                       '  -- if S_initial = ' + checked_source(name, stage) + '\n' +
                       '  -- if S_pause = $review_seek(S_initial[.COMPLETION = NORMAL], ' + str(stage) + ', 500)\n' +
                       '  -- if S = S_pause[.COMPLETION = NORMAL]\n' +
                       ''.join('  -- if ' + check + '\n' for check in checks))
    result = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                             *MODULES, str(fixture)], capture_output=True, timeout=300)
    (OUT / (name + '-stage' + str(stage) + '.stdout')).write_bytes(result.stdout)
    (OUT / (name + '-stage' + str(stage) + '.stderr')).write_bytes(result.stderr)
    assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr, (name, stage, OUT)
    print(name, stage, len(checks), 'pass', flush=True)


run_case('temporary-owner', 0, [
    'S.TODO = (PIPE_OBJECT_SEND (PIPE_OBJECT_TARGET (METHOD_TARGET n_receiver porigin_method) pobjectselection) pobjectselection (PINT 3) z_send z_call) :: ptask_tail*',
    '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    'S.RESULT = KNOWN (POBJECT n_receiver)',
    '$origin_node(S.SOURCES, pobjectselection.SITE) = (NExprBinaryOpPipe expression_left expression_right metadata)',
    '~$pppipe_optimized(expression_right)',
    '$pipe_send_line(S, pobjectselection.SITE) = z_send',
    '$pipe_lookup_line(S, pobjectselection.SITE) = pobjectselection.INIT',
    '$call_line_valid(S, (pobjectselection.SITE), z_call)',
    '$task_nodes(PIPE_OBJECT_SEND (PIPE_OBJECT_TARGET (METHOD_TARGET n_receiver porigin_method) pobjectselection) pobjectselection (PINT 3) z_send z_call) = [HOBJECT n_receiver]',
    '(HOBJECT n_receiver) <- S.ALLOCATIONS',
    '$pipe_object_send_valid(S, PIPE_OBJECT_TARGET (METHOD_TARGET n_receiver porigin_method) pobjectselection, pobjectselection, PINT 3, z_send, z_call)',
    '~$pipe_object_send_valid(S[.RESULT = KNOWN PNULL], PIPE_OBJECT_TARGET (METHOD_TARGET n_receiver porigin_method) pobjectselection, pobjectselection, PINT 3, z_send, z_call)',
    '~$pipe_object_send_valid(S, PIPE_OBJECT_TARGET (METHOD_TARGET n_receiver porigin_method) pobjectselection[.METHOD = PORIGIN 999 eps], pobjectselection[.METHOD = PORIGIN 999 eps], PINT 3, z_send, z_call)',
    '~$pipe_object_send_valid(S, PIPE_OBJECT_TARGET (METHOD_TARGET n_receiver porigin_method) pobjectselection[.REQUESTED = PORIGIN 999 eps], pobjectselection[.REQUESTED = PORIGIN 999 eps], PINT 3, z_send, z_call)',
    '~$pipe_object_send_valid(S, PIPE_OBJECT_TARGET (METHOD_TARGET n_receiver porigin_method) pobjectselection[.SITE = porigin_method], pobjectselection[.SITE = porigin_method], PINT 3, z_send, z_call)',
    '~$pipe_object_send_valid(S, PIPE_OBJECT_TARGET (METHOD_TARGET n_receiver porigin_method) pobjectselection[.INIT = $(pobjectselection.INIT + 1)], pobjectselection[.INIT = $(pobjectselection.INIT + 1)], PINT 3, z_send, z_call)',
    '~$pipe_object_send_valid(S, PIPE_OBJECT_TARGET (METHOD_TARGET n_receiver porigin_method) pobjectselection[.LINE = $(pobjectselection.LINE + 1)], pobjectselection[.LINE = $(pobjectselection.LINE + 1)], PINT 3, z_send, z_call)',
    'S_done = $drive(S, 3000)', 'S_done.COMPLETION = NORMAL',
    '$outputs(S_done.EVENTS) = $ptascii("R|C|D|4|E")',
])
run_case('temporary-owner', 1, [
    'S.TODO = (PIPE_OBJECT_RESULT (METHOD_TARGET n_receiver porigin_method) pobjectselection) :: ptask_tail*',
    '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    '~((HOBJECT n_receiver) <- S.ALLOCATIONS)',
    '$task_nodes(PIPE_OBJECT_RESULT (METHOD_TARGET n_receiver porigin_method) pobjectselection) = eps',
    '$pipe_object_target_identity(S, METHOD_TARGET n_receiver porigin_method, pobjectselection, false)',
    '~$call_task_valid(S, PIPE_OBJECT_RESULT (METHOD_TARGET n_receiver porigin_method) pobjectselection[.METHOD = PORIGIN 999 eps])',
    '~$call_task_valid(S, PIPE_OBJECT_RESULT (METHOD_TARGET n_receiver porigin_method) pobjectselection[.INIT = $(pobjectselection.INIT + 1)])',
    'S.RESULT = KNOWN (PINT 4)',
    'S_one = $drive_steps(S[.COMPLETION = NORMAL], 1)',
    'S_one.TODO = ptask_tail*', 'S_one.BASE = BASE_VALUE S.RESULT',
])
run_case('optimized-variable', 0, [
    'S.TODO = (PIPE_OBJECT_SEND (PIPE_OBJECT_TARGET (METHOD_TARGET n_receiver porigin_method) pobjectselection) pobjectselection (PINT 3) z_send z_call) :: ptask_tail*',
    '$origin_node(S.SOURCES, pobjectselection.SITE) = (NExprBinaryOpPipe expression_left expression_right metadata)',
    '$pppipe_optimized(expression_right)',
    '$firstclass_evaluated(S, $pipe_rhs_origin(pobjectselection.SITE))',
    '$pipe_object_site_valid(S, pobjectselection)',
    '$call_selected_valid(S, PIPE_OBJECT_TARGET (METHOD_TARGET n_receiver porigin_method) pobjectselection, (pobjectselection.SITE))',
    'S_done = $drive(S, 3000)', 'S_done.COMPLETION = NORMAL',
    '$outputs(S_done.EVENTS) = $ptascii("O3|8")',
])
run_case('temporary-byref', 0, [
    'S.TODO = (PIPE_OBJECT_SEND (PIPE_OBJECT_TARGET (METHOD_TARGET n_receiver porigin_method) pobjectselection) pobjectselection (POBJECT n_left) z_send z_call) :: ptask_tail*',
    'n_left =/= n_receiver',
    '$task_nodes(PIPE_OBJECT_SEND (PIPE_OBJECT_TARGET (METHOD_TARGET n_receiver porigin_method) pobjectselection) pobjectselection (POBJECT n_left) z_send z_call) = [HOBJECT n_left, HOBJECT n_receiver]',
    'S_done = $drive(S, 3000)', 'S_done.COMPLETION = NORMAL',
    '$outputs(S_done.EVENTS) = $ptascii("R|L|I|E|I::__invoke(): Argument #1 ($x) could not be passed by reference|")',
])
run_case('scalar-rhs', 2, [
    'S.TODO = (PIPE_APPLY porigin (KNOWN (PINT 3)) z_send z_call) :: ptask_tail*',
    'S.OBJECTS[0] = INSTANCE porigin_class',
    '$effective_method(S, porigin_class, $ptascii("__invoke"), |S.CLASSES|) = (pmethoddesc)',
    'pobjectselection = {SITE porigin, INIT $pipe_lookup_line(S, porigin), LINE z_call, REQUESTED porigin_class, METHOD pmethoddesc.FUNCTION.ORIGIN}',
    '~$pipe_object_site_valid(S, pobjectselection)',
    '~$call_task_valid(S, PIPE_OBJECT_RESULT (METHOD_TARGET 0 pmethoddesc.FUNCTION.ORIGIN) pobjectselection)',
])
assert FINGERPRINT == request.t.syntax_validation.implementation_fingerprint()
print('PASS pipe object protocol: five reached stages', OUT, flush=True)

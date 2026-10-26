#!/usr/bin/env python3
"""Reached pipe-array selection, owner and result-certificate checks."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = Path(tempfile.mkdtemp(prefix='pipe-array-protocol-', dir=ROOT / '.tools'))
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import request_environment as request
from recorded_worker import Worker

SOURCES = json.loads((ROOT / 'tests/semantics/pipe_array_cases.json').read_text())
SOURCES['nonarray-right'] = '''<?php
class Box { public function run($x) { return $x; } }
$b = new Box;
echo 5 |> "strval";
'''
MODULES = [str(ROOT / path) for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
FINGERPRINT = request.t.syntax_validation.implementation_fingerprint()

PREFIX = '''
dec $review_stage(pstate, nat) : bool
def $review_stage(S, 0) = true
  -- if S.TODO = (PIPE_ARRAY_SEND (ARRAY_METHOD_TARGET (METHOD_TARGET n_receiver porigin_method) parrayselection) parrayselection (POBJECT n_left) z_send z_call) :: ptask*
def $review_stage(S, 1) = true
  -- if S.TODO = (PIPE_ARRAY_RESULT (METHOD_TARGET n_receiver porigin_method) parrayselection) :: ptask*
def $review_stage(S, 2) = true
  -- if S.TODO = (PIPE_APPLY porigin (KNOWN (PINT 5)) z_send z_call) :: ptask*
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


def checked_source(name):
    source = OUTPUT / (name + '.php')
    source.write_bytes(SOURCES[name].encode())
    frontend = adapter = None
    try:
        frontend = Worker([str(request.t.PHP), '-n', *request.t.FLAGS,
                           '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], OUTPUT / (name + '-frontend'))
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)],
                         OUTPUT / (name + '-adapter'))
        parsed = frontend.request({'op': 'parse', 'source': request.b64(source.read_bytes())})
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
    return '$php_run(' + checked['fixture'] + ', 0, ' + json.dumps(request.b64(str(source).encode())) + ')'


def run_case(name, stage, checks):
    fixture = OUTPUT / (name + '.watsup')
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                       '  -- if S_initial = ' + checked_source(name) + '\n' +
                       '  -- if S_pause = $review_seek(S_initial[.COMPLETION = NORMAL], ' + str(stage) + ', 400)\n' +
                       '  -- if S = S_pause[.COMPLETION = NORMAL]\n' +
                       ''.join('  -- if ' + check + '\n' for check in checks))
    result = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                             *MODULES, str(fixture)], capture_output=True, timeout=300)
    (OUTPUT / (name + '.stdout')).write_bytes(result.stdout)
    (OUTPUT / (name + '.stderr')).write_bytes(result.stderr)
    assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr, (name, OUTPUT)
    print(name, len(checks), 'pass', flush=True)


run_case('selected_receiver_hold', 0, [
    'S.TODO = (PIPE_ARRAY_SEND (ARRAY_METHOD_TARGET (METHOD_TARGET n_receiver porigin_method) parrayselection) parrayselection (POBJECT n_left) z_send z_call) :: ptask_tail*',
    '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    'S.RESULT = KNOWN PNULL',
    '$origin_node(S.SOURCES, parrayselection.SITE) = (NExprBinaryOpPipe expression_left expression_right metadata)',
    '~$pppipe_optimized(expression_right)',
    '$pipe_send_line(S, parrayselection.SITE) = z_send',
    '$pipe_lookup_line(S, parrayselection.SITE) = parrayselection.INIT',
    '$call_line_valid(S, (parrayselection.SITE), z_call)',
    '$task_nodes(PIPE_ARRAY_SEND (ARRAY_METHOD_TARGET (METHOD_TARGET n_receiver porigin_method) parrayselection) parrayselection (POBJECT n_left) z_send z_call) = [HOBJECT n_left, HOBJECT n_receiver]',
    'n_left =/= n_receiver',
    '(HOBJECT n_left) <- S.ALLOCATIONS', '(HOBJECT n_receiver) <- S.ALLOCATIONS',
    'S.ARRAYS[0] = parray_rhs',
    '$entry_lookup(parray_rhs.ITEMS, KINT 0) = (pitem_receiver)',
    '$entry_value(S, pitem_receiver) = POBJECT n_receiver',
    '~((HARRAY 0) <- S.ALLOCATIONS)',
    'n_owners = $heap_owners($heap_graph(S), HOBJECT n_receiver)', '$(n_owners > 0)',
    '~$pipe_array_send_valid(S, ARRAY_METHOD_TARGET (METHOD_TARGET n_receiver porigin_method) parrayselection[.NAME = $ptascii("missing")], parrayselection[.NAME = $ptascii("missing")], POBJECT n_left, z_send, z_call)',
    '~$pipe_array_send_valid(S, ARRAY_METHOD_TARGET (METHOD_TARGET n_receiver porigin_method) parrayselection[.REQUESTED = PORIGIN 999 eps], parrayselection[.REQUESTED = PORIGIN 999 eps], POBJECT n_left, z_send, z_call)',
    '~$pipe_array_send_valid(S, ARRAY_METHOD_TARGET (METHOD_TARGET n_receiver porigin_method) parrayselection[.SITE = porigin_method], parrayselection[.SITE = porigin_method], POBJECT n_left, z_send, z_call)',
    '~$pipe_array_send_valid(S, ARRAY_METHOD_TARGET (METHOD_TARGET n_receiver porigin_method) parrayselection[.INIT = $(parrayselection.INIT + 1)], parrayselection[.INIT = $(parrayselection.INIT + 1)], POBJECT n_left, z_send, z_call)',
    '~$pipe_array_send_valid(S, ARRAY_METHOD_TARGET (METHOD_TARGET n_receiver porigin_method) parrayselection[.LINE = $(parrayselection.LINE + 1)], parrayselection[.LINE = $(parrayselection.LINE + 1)], POBJECT n_left, z_send, z_call)',
    'S_done = $drive(S, 2000)', 'S_done.COMPLETION = NORMAL',
    '$outputs(S_done.EVENTS) = $ptascii("RHS|L1|L2|R|E|R::set(): Argument #1 ($x) could not be passed by reference|")',
])
run_case('last_receiver', 1, [
    'S.TODO = (PIPE_ARRAY_RESULT (METHOD_TARGET n_receiver porigin_method) parrayselection) :: ptask_tail*',
    '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    'S.OBJECTS[n_receiver] = INSTANCE parrayselection.REQUESTED',
    '~((HOBJECT n_receiver) <- S.ALLOCATIONS)',
    '$task_nodes(PIPE_ARRAY_RESULT (METHOD_TARGET n_receiver porigin_method) parrayselection) = eps',
    '$pipe_array_result_target(S, METHOD_TARGET n_receiver porigin_method, parrayselection)',
    '~$call_task_valid(S, PIPE_ARRAY_RESULT (METHOD_TARGET n_receiver porigin_method) parrayselection[.NAME = $ptascii("missing")])',
    '~$call_task_valid(S, PIPE_ARRAY_RESULT (METHOD_TARGET n_receiver porigin_method) parrayselection[.REQUESTED = PORIGIN 999 eps])',
    '~$call_task_valid(S, PIPE_ARRAY_RESULT (METHOD_TARGET n_receiver porigin_method) parrayselection[.SITE = porigin_method])',
    '~$call_task_valid(S, PIPE_ARRAY_RESULT (METHOD_TARGET n_receiver porigin_method) parrayselection[.INIT = $(parrayselection.INIT + 1)])',
    '~$call_task_valid(S, PIPE_ARRAY_RESULT (METHOD_TARGET n_receiver porigin_method) parrayselection[.LINE = $(parrayselection.LINE + 1)])',
    'S_one = $drive_steps(S[.COMPLETION = NORMAL], 1)',
    'S_one.TODO = ptask_tail*', 'S_one.BASE = BASE_VALUE S.RESULT',
    'S_done = $drive(S, 2000)', 'S_done.COMPLETION = NORMAL',
    '$outputs(S_done.EVENTS) = $ptascii("RESULT|BODY|5|D|6|")',
])
run_case('nonarray-right', 2, [
    'S.TODO = (PIPE_APPLY porigin (KNOWN (PINT 5)) z_send z_call) :: ptask_tail*',
    'S.OBJECTS[0] = INSTANCE porigin_class',
    '$effective_method(S, porigin_class, $ptascii("run"), |S.CLASSES|) = (pmethoddesc)',
    'parrayselection = {SITE porigin, INIT $pipe_lookup_line(S, porigin), LINE z_call, REQUESTED porigin_class, NAME $ptascii("run")}',
    '~$call_task_valid(S, PIPE_ARRAY_RESULT (METHOD_TARGET 0 pmethoddesc.FUNCTION.ORIGIN) parrayselection)',
])
assert FINGERPRINT == request.t.syntax_validation.implementation_fingerprint()
print('PASS pipe array protocol: 3 reached stages', OUTPUT, flush=True)

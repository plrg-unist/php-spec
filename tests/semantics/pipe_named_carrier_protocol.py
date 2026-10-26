#!/usr/bin/env python3
"""Reached ordinary pipe string selection and carrier/source guards."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(tempfile.mkdtemp(prefix='pipe-named-carrier-protocol-', dir=ROOT / '.tools'))
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import request_environment as request
from recorded_worker import Worker

SOURCES = json.loads((ROOT / 'tests/semantics/pipe_named_carrier_cases.json').read_text())
SOURCES['nonstring_rhs'] = '<?php function f($x) { return $x; } echo (3 |> 4);\n'
MODULES = [str(ROOT / path) for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
FINGERPRINT = request.t.syntax_validation.implementation_fingerprint()
PREFIX = '''
dec $review_stage(pstate, nat) : bool
def $review_stage(S, 0) = true
  -- if S.TODO = (PIPE_APPLY porigin (KNOWN (PINT n_left)) z_send z_call) :: ptask*
def $review_stage(S, 1) = true
  -- if S.TODO = (PIPE_APPLY porigin (KNOWN (POBJECT n_left)) z_send z_call) :: ptask*
def $review_stage(S, 2) = true
  -- if S.TODO = (PIPE_APPLY porigin (KNOWN (PINT 3)) z_send z_call) :: ptask*
  -- if S.RESULT = KNOWN (PINT 4)
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
    path = OUT / (name + '.php')
    path.write_bytes(SOURCES[name].encode())
    front = adapter = None
    try:
        front = Worker([str(request.t.PHP), '-n', *request.t.FLAGS, '-d',
                        'extension=' + str(ROOT / '.tools/php-file.so'),
                        str(ROOT / 'frontend/worker.php')], OUT / (name + '-frontend'))
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)],
                         OUT / (name + '-adapter'))
        parsed = front.request({'op': 'parse', 'source': request.b64(path.read_bytes())})
        assert parsed['ok'] and parsed['accepted']
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok']
    finally:
        try:
            if front:
                front.close()
        finally:
            if adapter:
                adapter.close()
    return '$php_run(' + checked['fixture'] + ', 0, ' + json.dumps(request.b64(str(path).encode())) + ')'


def run_case(name, stage, checks):
    fixture = OUT / (name + '.watsup')
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
                       + '  -- if S_initial = ' + checked_source(name) + '\n'
                       + '  -- if S_pause = $review_seek(S_initial[.COMPLETION = NORMAL], ' + str(stage) + ', 400)\n'
                       + '  -- if S = S_pause[.COMPLETION = NORMAL]\n'
                       + ''.join('  -- if ' + check + '\n' for check in checks))
    command = [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), *MODULES, str(fixture)]
    (OUT / (name + '.command.json')).write_text(json.dumps(command) + '\n')
    result = subprocess.run(command, capture_output=True, timeout=300)
    (OUT / (name + '.stdout')).write_bytes(result.stdout)
    (OUT / (name + '.stderr')).write_bytes(result.stderr)
    (OUT / (name + '.status.json')).write_text(json.dumps({'exit_status': result.returncode}) + '\n')
    assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr, (name, OUT)
    print(name, len(checks), 'pass', flush=True)
    return len(checks)


count = 0
count += run_case('optimized_variable_basic', 0, [
    'S.TODO = (PIPE_APPLY porigin (KNOWN (PINT 2)) z_send z_call) :: ptask_tail*',
    '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    'S_read = $resolve_at($hold_task_inputs(S), S.RESULT, $pipe_lookup_line(S, porigin))',
    'S_read.RESULT = KNOWN (PSTRING_CARRIER pstringidentity n*)',
    'n* = $ptascii("f")',
    '$pipe_apply_task_valid(S, porigin, KNOWN (PINT 2), z_send, z_call)',
    '$pipe_named_carrier_site(S_read, porigin, n*)',
    '$string_carrier_valid(S_read, PSTRING_CARRIER pstringidentity n*)',
    '$origin_node(S.SOURCES, porigin) = (NExprBinaryOpPipe expression_left expression_right metadata)',
    '$pppipe_optimized(expression_right)',
    '$pipe_fixed_name(S, porigin) = eps',
    '$firstclass_evaluated(S, $pipe_rhs_origin(porigin))',
    '~$string_carrier_valid(S_read, PSTRING_CARRIER (REQUEST_STRING 999) n*)',
    'S_after = $drive_steps(S, 1)',
    'S_after.TODO = (CALL_ARGS pcalltarget eps 1 poperand* (porigin) z_call) :: ptask_after*',
    '$target_function(S_after, pcalltarget) = (pfunction)',
    'pfunction.NAME = $ptascii("f")',
    'S_after.CURRENT = S.CURRENT',
    'S_done = $drive(S, 2000)', 'S_done.COMPLETION = NORMAL',
    '$outputs(S_done.EVENTS) = $ptascii("F|2|3|")',
])
count += run_case('selected_name', 0, [
    'S.TODO = (PIPE_APPLY porigin (KNOWN (PINT 3)) z_send z_call) :: ptask_tail*',
    '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    'S_read = $resolve_at($hold_task_inputs(S), S.RESULT, $pipe_lookup_line(S, porigin))',
    'S_read.RESULT = KNOWN (PSTRING_CARRIER pstringidentity n*)',
    'n* = $ptascii("f")',
    '$outputs(S.EVENTS) = $ptascii("R|")',
    '$pipe_named_carrier_site(S_read, porigin, n*)',
    'S_after = $drive_steps(S, 1)',
    'S_after.TODO = (CALL_ARGS pcalltarget eps 1 poperand* (porigin) z_call) :: ptask_after*',
    '$target_function(S_after, pcalltarget) = (pfunction)',
    'pfunction.NAME = $ptascii("f")',
    'S_done = $drive(S, 2000)', 'S_done.COMPLETION = NORMAL',
    '$outputs(S_done.EVENTS) = $ptascii("R|F|3|4|g|")',
])
count += run_case('nonoptimized_literal', 0, [
    'S.TODO = (PIPE_APPLY porigin (KNOWN (PINT 3)) z_send z_call) :: ptask_tail*',
    '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    'S_read = $resolve_at($hold_task_inputs(S), S.RESULT, $pipe_lookup_line(S, porigin))',
    'S_read.RESULT = KNOWN (PSTRING_CARRIER pstringidentity n*)',
    'n* = $ptascii("f")',
    '$origin_node(S.SOURCES, porigin) = (NExprBinaryOpPipe expression_left expression_right metadata)',
    '~$pppipe_optimized(expression_right)',
    '$parser_literal(expression_right) = (PSTRING n*)',
    '$pipe_named_carrier_site(S_read, porigin, n*)',
    '~$pipe_named_carrier_site(S_read, porigin, $ptascii("g"))',
    'S_done = $drive(S, 2000)', 'S_done.COMPLETION = NORMAL',
    '$outputs(S_done.EVENTS) = $ptascii("F|3|4|")',
])
count += run_case('owned_missing_rhs', 1, [
    'S.TODO = (PIPE_APPLY porigin (KNOWN (POBJECT n_left)) z_send z_call) :: ptask_tail*',
    '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    'S_read = $resolve_at($hold_task_inputs(S), S.RESULT, $pipe_lookup_line(S, porigin))',
    'S_read.RESULT = KNOWN (PSTRING_CARRIER pstringidentity n*)',
    'n* = $ptascii("missing")',
    '$task_nodes(PIPE_APPLY porigin (KNOWN (POBJECT n_left)) z_send z_call) = [HOBJECT n_left]',
    '(HOBJECT n_left) <- S.ALLOCATIONS',
    'n_owners = $heap_owners($heap_graph(S), HOBJECT n_left)', '$(n_owners > 0)',
    '$outputs(S.EVENTS) = $ptascii("R|")',
    'S_done = $drive(S, 2000)', 'S_done.COMPLETION = NORMAL',
    '$heap_owners($heap_graph(S_done), HOBJECT n_left) = 0',
    '$outputs(S_done.EVENTS) = $ptascii("R|L|E|Call to undefined function missing()|5|")',
])
count += run_case('nonstring_rhs', 2, [
    'S.TODO = (PIPE_APPLY porigin (KNOWN (PINT 3)) z_send z_call) :: ptask_tail*',
    '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    'S.RESULT = KNOWN (PINT 4)',
    '$origin_node(S.SOURCES, porigin) = (NExprBinaryOpPipe expression_left expression_right metadata)',
    '~$pipe_named_carrier_site(S, porigin, $ptascii("f"))',
])
assert FINGERPRINT == request.t.syntax_validation.implementation_fingerprint()
print('PASS pipe named carrier protocol: 5 reached stages,', count, 'assertions', OUT, flush=True)

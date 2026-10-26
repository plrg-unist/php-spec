#!/usr/bin/env python3
"""Reached public static pipe-string selection, send and result receipts."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(tempfile.mkdtemp(prefix='pipe-static-string-protocol-', dir=ROOT / '.tools'))
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import request_environment as request
from recorded_worker import Worker

SOURCES = json.loads((ROOT / 'tests/semantics/pipe_static_string_cases.json').read_text())
SOURCES['nonstring_rhs'] = '<?php\nclass C { public static function m($x) { return $x; } }\necho (3 |> 4);\n'
MODULES = [str(ROOT / path) for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
FINGERPRINT = request.t.syntax_validation.implementation_fingerprint()
PREFIX = '''
dec $review_stage(pstate, nat) : bool
def $review_stage(S, 0) = true
  -- if S.TODO = (PIPE_STRING_SEND (STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_class porigin_method) pstringselection) pstringselection (PINT 7) z_send z_call) :: ptask*
def $review_stage(S, 1) = true
  -- if S.TODO = (PIPE_STRING_SEND (STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_class porigin_method) pstringselection) pstringselection (POBJECT n_left) z_send z_call) :: ptask*
def $review_stage(S, 2) = true
  -- if S.TODO = (PIPE_STRING_RESULT (STATIC_METHOD_TARGET porigin_class porigin_method) pstringselection) :: ptask*
def $review_stage(S, 3) = true
  -- if S.TODO = (PIPE_STRING_SEND (STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_class porigin_method) pstringselection) pstringselection (PINT 8) z_send z_call) :: ptask*
def $review_stage(S, 4) = true
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
count += run_case('variable_basic', 0, [
    'S.TODO = (PIPE_STRING_SEND (STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_class porigin_method) pstringselection) pstringselection (PINT 7) z_send z_call) :: ptask_tail*',
    '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    'S.RESULT = KNOWN PNULL', 'pstringselection.ORIGINAL = $ptascii("C::twice")',
    '$origin_node(S.SOURCES, pstringselection.SITE) = (NExprBinaryOpPipe expression_left expression_right metadata)',
    '~$pppipe_optimized(expression_right)',
    '$pipe_lookup_line(S, pstringselection.SITE) = pstringselection.INIT',
    '$pipe_send_line(S, pstringselection.SITE) = z_send',
    '$call_task_valid(S, PIPE_STRING_SEND (STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_class porigin_method) pstringselection) pstringselection (PINT 7) z_send z_call)',
    '~$pipe_string_send_valid(S, STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_class porigin_method) pstringselection[.ORIGINAL = $ptascii("C::missing")], pstringselection[.ORIGINAL = $ptascii("C::missing")], PINT 7, z_send, z_call)',
    '~$pipe_string_send_valid(S, STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_class porigin_method) pstringselection[.REQUESTED = PORIGIN 999 eps], pstringselection[.REQUESTED = PORIGIN 999 eps], PINT 7, z_send, z_call)',
    '~$pipe_string_send_valid(S, STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_class porigin_method) pstringselection[.SITE = porigin_method], pstringselection[.SITE = porigin_method], PINT 7, z_send, z_call)',
    '~$pipe_string_send_valid(S, STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_class porigin_method) pstringselection[.INIT = $(pstringselection.INIT + 1)], pstringselection[.INIT = $(pstringselection.INIT + 1)], PINT 7, z_send, z_call)',
    '~$pipe_string_send_valid(S, STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_class porigin_method) pstringselection[.LINE = $(pstringselection.LINE + 1)], pstringselection[.LINE = $(pstringselection.LINE + 1)], PINT 7, z_send, z_call)',
    '~$pipe_string_send_valid(S, STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_class (PORIGIN 999 eps)) pstringselection, pstringselection, PINT 7, z_send, z_call)',
    'S_done = $drive(S, 2000)', 'S_done.COMPLETION = NORMAL',
    '$outputs(S_done.EVENTS) = $ptascii("M|7|14|")',
])
count += run_case('independent_byref_owner', 1, [
    'S.TODO = (PIPE_STRING_SEND (STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_class porigin_method) pstringselection) pstringselection (POBJECT n_left) z_send z_call) :: ptask_tail*',
    '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    '$task_nodes(PIPE_STRING_SEND (STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_class porigin_method) pstringselection) pstringselection (POBJECT n_left) z_send z_call) = [HOBJECT n_left]',
    '(HOBJECT n_left) <- S.ALLOCATIONS',
    'n_owners = $heap_owners($heap_graph(S), HOBJECT n_left)', '$(n_owners > 0)',
    'S_done = $drive(S, 2000)', 'S_done.COMPLETION = NORMAL',
    '$outputs(S_done.EVENTS) = $ptascii("L|E|C::set(): Argument #1 ($x) could not be passed by reference|")',
])
count += run_case('variable_ref_return', 2, [
    'S.TODO = (PIPE_STRING_RESULT (STATIC_METHOD_TARGET porigin_class porigin_method) pstringselection) :: ptask_tail*',
    '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    '$pipe_string_result_valid(S, STATIC_METHOD_TARGET porigin_class porigin_method, pstringselection)',
    'S.RESULT = REFERENCE n_result',
    '$task_nodes(PIPE_STRING_RESULT (STATIC_METHOD_TARGET porigin_class porigin_method) pstringselection) = eps',
    '~$call_task_valid(S, PIPE_STRING_RESULT (STATIC_METHOD_TARGET porigin_class porigin_method) pstringselection[.ORIGINAL = $ptascii("C::missing")])',
    '~$call_task_valid(S, PIPE_STRING_RESULT (STATIC_METHOD_TARGET porigin_class porigin_method) pstringselection[.REQUESTED = PORIGIN 999 eps])',
    '~$call_task_valid(S, PIPE_STRING_RESULT (STATIC_METHOD_TARGET porigin_class porigin_method) pstringselection[.SITE = porigin_method])',
    '~$call_task_valid(S, PIPE_STRING_RESULT (STATIC_METHOD_TARGET porigin_class porigin_method) pstringselection[.INIT = $(pstringselection.INIT + 1)])',
    '~$call_task_valid(S, PIPE_STRING_RESULT (STATIC_METHOD_TARGET porigin_class porigin_method) pstringselection[.LINE = $(pstringselection.LINE + 1)])',
    '~$call_task_valid(S, PIPE_STRING_RESULT (STATIC_METHOD_TARGET porigin_class (PORIGIN 999 eps)) pstringselection)',
    'S_one = $drive_steps(S[.COMPLETION = NORMAL], 1)',
    'S_one.TODO = ptask_tail*', 'S_one.BASE = BASE_VALUE S.RESULT',
    'S_done = $drive(S, 2000)', 'S_done.COMPLETION = NORMAL',
    '$outputs(S_done.EVENTS) = $ptascii("S|1|T|9|")',
])
count += run_case('literal_basic', 3, [
    'S.TODO = (PIPE_STRING_SEND (STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_class porigin_method) pstringselection) pstringselection (PINT 8) z_send z_call) :: ptask_tail*',
    '$origin_node(S.SOURCES, pstringselection.SITE) = (NExprBinaryOpPipe expression_left expression_right metadata)',
    '$parser_literal(expression_right) = (PSTRING pstringselection.ORIGINAL)',
    'pstringselection.ORIGINAL = $ptascii("C::twice")',
    '$string_site_valid(S, pstringselection, false)',
    '$string_target_identity(S, STATIC_METHOD_TARGET porigin_class porigin_method, pstringselection[.ORIGINAL = $ptascii("c::twice")])',
    '~$string_site_valid(S, pstringselection[.ORIGINAL = $ptascii("c::twice")], false)',
    'S_done = $drive(S, 2000)', 'S_done.COMPLETION = NORMAL',
    '$outputs(S_done.EVENTS) = $ptascii("M|8|16|")',
])
count += run_case('nonstring_rhs', 4, [
    'S.TODO = (PIPE_APPLY porigin (KNOWN (PINT 3)) z_send z_call) :: ptask_tail*',
    '$origin_node(S.SOURCES, porigin) = (NExprBinaryOpPipe expression_left expression_right metadata)',
    '$parser_literal(expression_right) = (PINT 4)',
    '$class_named(S.CLASSNAMES, $ptascii("c")) = (porigin_class)',
    '$effective_method(S, porigin_class, $ptascii("m"), |S.CLASSES|) = (pmethoddesc)',
    'pstringselection = {SITE porigin, INIT $pipe_lookup_line(S, porigin), LINE z_call, REQUESTED porigin_class, ORIGINAL $ptascii("C::m")}',
    '~$string_site_valid(S, pstringselection, false)',
    '~$call_task_valid(S, PIPE_STRING_RESULT (STATIC_METHOD_TARGET porigin_class pmethoddesc.FUNCTION.ORIGIN) pstringselection)',
])
assert FINGERPRINT == request.t.syntax_validation.implementation_fingerprint()
print('PASS pipe static string protocol: 5 reached stages,', count, 'assertions', OUT, flush=True)

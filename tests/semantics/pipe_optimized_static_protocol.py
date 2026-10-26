#!/usr/bin/env python3
"""Reached optimized static method-string pipe selection and receipts."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(tempfile.mkdtemp(prefix='pipe-optimized-static-protocol-', dir=ROOT / '.tools'))
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import request_environment as request
from recorded_worker import Worker

SOURCES = json.loads((ROOT / 'tests/semantics/pipe_optimized_static_cases.json').read_text())
SOURCES['nonstring_rhs'] = '<?php\nclass C { public static function f($x) { return $x; } }\necho (3 |> 4);\n'
MODULES = [str(ROOT / path) for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
FINGERPRINT = request.t.syntax_validation.implementation_fingerprint()
PREFIX = '''
dec $review_stage(pstate, nat) : bool
def $review_stage(S, 0) = true
  -- if S.TODO = (PIPE_STRING_SEND (STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_class porigin_method) pstringselection) pstringselection (PINT 3) z_send z_call) :: ptask*
def $review_stage(S, 1) = true
  -- if S.TODO = (PIPE_STRING_SEND (STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_class porigin_method) pstringselection) pstringselection (POBJECT n_left) z_send z_call) :: ptask*
def $review_stage(S, 2) = true
  -- if S.TODO = (PIPE_STRING_RESULT (STATIC_METHOD_TARGET porigin_class porigin_method) pstringselection) :: ptask*
def $review_stage(S, 3) = true
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
count += run_case('fixed_literal', 0, [
    'S.TODO = (PIPE_STRING_SEND (STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_class porigin_method) pstringselection) pstringselection (PINT 3) z_send z_call) :: ptask_tail*',
    '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    'pstringselection.ORIGINAL = $ptascii("C::f")',
    '$origin_node(S.SOURCES, pstringselection.SITE) = (NExprBinaryOpPipe expression_left (NExprFuncCall expression_callee (SEQUENCE ([(NVariadicPlaceholder metadata_placeholder)])) metadata_call) metadata)',
    '$pppipe_optimized(NExprFuncCall expression_callee (SEQUENCE ([(NVariadicPlaceholder metadata_placeholder)])) metadata_call)',
    '$parser_literal(expression_callee) = (PSTRING pstringselection.ORIGINAL)',
    '$pipe_fixed_name(S, pstringselection.SITE) = ((pstringselection.ORIGINAL, preqbytes_fallback?))',
    '$pipe_optimized_method_source(S, pstringselection.SITE, pstringselection.ORIGINAL)',
    '$string_site_valid(S, pstringselection, false)',
    '~$pipe_optimized_method_source(S, pstringselection.SITE, $ptascii("c::f"))',
    '~$string_site_valid(S, pstringselection[.ORIGINAL = $ptascii("c::f")], false)',
    '~$pipe_string_send_valid(S, STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_class porigin_method) pstringselection[.SITE = porigin_method], pstringselection[.SITE = porigin_method], PINT 3, z_send, z_call)',
    '~$pipe_string_send_valid(S, STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_class porigin_method) pstringselection[.INIT = $(pstringselection.INIT + 1)], pstringselection[.INIT = $(pstringselection.INIT + 1)], PINT 3, z_send, z_call)',
    '~$pipe_string_send_valid(S, STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_class porigin_method) pstringselection[.LINE = $(pstringselection.LINE + 1)], pstringselection[.LINE = $(pstringselection.LINE + 1)], PINT 3, z_send, z_call)',
    'S_done = $drive(S, 2000)', 'S_done.COMPLETION = NORMAL',
    '$outputs(S_done.EVENTS) = $ptascii("M|3|4|")',
])
count += run_case('fixed_literal_leading_slash', 0, [
    'S.TODO = (PIPE_STRING_SEND (STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_class porigin_method) pstringselection) pstringselection (PINT 3) z_send z_call) :: ptask_tail*',
    '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    'pstringselection.ORIGINAL = $ptascii("C::f")',
    '$origin_node(S.SOURCES, pstringselection.SITE) = (NExprBinaryOpPipe expression_left (NExprFuncCall expression_callee (SEQUENCE ([(NVariadicPlaceholder metadata_placeholder)])) metadata_call) metadata)',
    '$parser_literal(expression_callee) = (PSTRING ptbytes_literal)',
    'ptbytes_literal =/= pstringselection.ORIGINAL',
    '$ppcall_literal_name(ptbytes_literal) = pstringselection.ORIGINAL',
    '$pipe_optimized_method_source(S, pstringselection.SITE, pstringselection.ORIGINAL)',
    '$string_site_valid(S, pstringselection, false)',
    '~$string_site_valid(S, pstringselection[.ORIGINAL = ptbytes_literal], false)',
    'S_done = $drive(S, 2000)', 'S_done.COMPLETION = NORMAL',
    '$outputs(S_done.EVENTS) = $ptascii("F|3|4|")',
])
count += run_case('selected_method_after_rebind', 0, [
    'S.TODO = (PIPE_STRING_SEND (STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_class porigin_method) pstringselection) pstringselection (PINT 3) z_send z_call) :: ptask_tail*',
    '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    'pstringselection.ORIGINAL = $ptascii("C::m")',
    '$outputs(S.EVENTS) = $ptascii("R|")',
    '$pipe_fixed_name(S, pstringselection.SITE) = eps',
    '$firstclass_evaluated(S, $pipe_rhs_origin(pstringselection.SITE))',
    '$pipe_optimized_method_source(S, pstringselection.SITE, pstringselection.ORIGINAL)',
    '$string_target_descriptor(S, pstringselection) = (pmethoddesc)',
    'pmethoddesc.NAME = $ptascii("m")',
    'S_after = $drive_steps(S, 1)',
    'S_after.TODO = (CALL_ARGS pcalltarget eps 1 poperand* (pstringselection.SITE) z_call) :: ptask_after*',
    '$target_function(S_after, pcalltarget) = (pmethoddesc.FUNCTION)',
    'S_after.CURRENT = S.CURRENT',
    'S_done = $drive(S, 2000)', 'S_done.COMPLETION = NORMAL',
    '$outputs(S_done.EVENTS) = $ptascii("R|M|3|4|C::n|")',
])
count += run_case('byref_owned_left', 1, [
    'S.TODO = (PIPE_STRING_SEND (STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_class porigin_method) pstringselection) pstringselection (POBJECT n_left) z_send z_call) :: ptask_tail*',
    '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    '$task_nodes(PIPE_STRING_SEND (STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_class porigin_method) pstringselection) pstringselection (POBJECT n_left) z_send z_call) = [HOBJECT n_left]',
    '(HOBJECT n_left) <- S.ALLOCATIONS',
    'n_owners = $heap_owners($heap_graph(S), HOBJECT n_left)', '$(n_owners > 0)',
    'S_done = $drive(S, 2000)', 'S_done.COMPLETION = NORMAL',
    '$heap_owners($heap_graph(S_done), HOBJECT n_left) = 0',
    '$outputs(S_done.EVENTS) = $ptascii("L|E|C::set(): Argument #1 ($x) could not be passed by reference|")',
])
count += run_case('ref_return', 2, [
    'S.TODO = (PIPE_STRING_RESULT (STATIC_METHOD_TARGET porigin_class porigin_method) pstringselection) :: ptask_tail*',
    '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    'S.RESULT = REFERENCE n_result',
    '$task_nodes(PIPE_STRING_RESULT (STATIC_METHOD_TARGET porigin_class porigin_method) pstringselection) = eps',
    '$pipe_string_result_valid(S, STATIC_METHOD_TARGET porigin_class porigin_method, pstringselection)',
    '$pipe_optimized_method_source(S, pstringselection.SITE, pstringselection.ORIGINAL)',
    '~$pipe_string_result_valid(S, STATIC_METHOD_TARGET porigin_class porigin_method, pstringselection[.ORIGINAL = $ptascii("C::missing")])',
    'S_done = $drive(S, 2000)', 'S_done.COMPLETION = NORMAL',
    '$outputs(S_done.EVENTS) = $ptascii("S|1|T|9|")',
])
count += run_case('nonstring_rhs', 3, [
    'S.TODO = (PIPE_APPLY porigin (KNOWN (PINT 3)) z_send z_call) :: ptask_tail*',
    '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    '$origin_node(S.SOURCES, porigin) = (NExprBinaryOpPipe expression_left expression_right metadata)',
    '~$pipe_optimized_method_source(S, porigin, $ptascii("C::f"))',
    '$class_named(S.CLASSNAMES, $ptascii("c")) = (porigin_class)',
    'pstringselection = {SITE porigin, INIT $pipe_lookup_line(S, porigin), LINE z_call, REQUESTED porigin_class, ORIGINAL $ptascii("C::f")}',
    '~$string_site_valid(S, pstringselection, false)',
])
assert FINGERPRINT == request.t.syntax_validation.implementation_fingerprint()
print('PASS optimized static pipe protocol: 6 reached stages,', count, 'assertions', OUT, flush=True)
